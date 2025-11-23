"""
Main FastAPI application for currency trading analysis.
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database import init_db, get_db, NotificationPreference, NotificationLog
from config import config
from services.currency_service import currency_service
from services.historical_service import historical_service
from services.portfolio_service import portfolio_service
from services.technical_analysis import technical_analysis
from services.news_service import news_service
from services.llm_service import llm_service
from services.signals_service import signals_service
from services.notification_service import notification_service
from services.scheduler_service import scheduler

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Currency Trading Analysis Platform",
    description="Comprehensive forex trading analysis with AI-powered insights",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and scheduler on startup"""
    init_db()
    scheduler.start()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.stop()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Currency Trading Analysis Platform API",
        "version": "1.0.0",
        "endpoints": {
            "currency_rates": "/api/rates",
            "historical_data": "/api/historical",
            "portfolio": "/api/portfolio",
            "signals": "/api/signals",
            "news": "/api/news",
            "analysis": "/api/analysis"
        }
    }


# ===== Currency Rates Endpoints =====

@app.get("/api/rates/latest")
async def get_latest_rates(base: str = Query("USD", description="Base currency")):
    """Get latest exchange rates for a base currency"""
    rates = currency_service.get_latest_rates(base)
    if not rates:
        raise HTTPException(status_code=500, detail="Failed to fetch exchange rates")
    return rates


@app.get("/api/rates/pair/{from_currency}/{to_currency}")
async def get_pair_rate(from_currency: str, to_currency: str):
    """Get exchange rate for a specific currency pair"""
    rate = currency_service.get_rate_for_pair(from_currency, to_currency)
    if rate is None:
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    return {
        "pair": f"{from_currency}/{to_currency}",
        "rate": rate,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/rates/convert")
async def convert_currency(
    amount: float = Query(..., description="Amount to convert"),
    from_currency: str = Query(..., description="Source currency"),
    to_currency: str = Query(..., description="Target currency")
):
    """Convert amount from one currency to another"""
    converted = currency_service.convert_amount(amount, from_currency, to_currency)
    if converted is None:
        raise HTTPException(status_code=404, detail="Conversion failed")

    return {
        "from": {
            "currency": from_currency,
            "amount": amount
        },
        "to": {
            "currency": to_currency,
            "amount": round(converted, 2)
        },
        "rate": round(converted / amount, 6) if amount > 0 else 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/rates/supported")
async def get_supported_currencies():
    """Get list of supported currencies"""
    currencies = currency_service.get_supported_currencies()
    return {"currencies": currencies}


# ===== Historical Data Endpoints =====

@app.get("/api/historical/{base}/{quote}")
async def get_historical_data(
    base: str,
    quote: str,
    days: int = Query(30, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """Get historical exchange rate data"""
    rates = historical_service.get_rates_for_period(db, base, quote, days)

    if not rates:
        # Try to fetch and store if not in database
        logger.info(f"No historical data found, fetching from API for {base}/{quote}")
        result = historical_service.fetch_and_store_historical_data(
            db, base, [quote], days
        )

        if result.get("success"):
            rates = historical_service.get_rates_for_period(db, base, quote, days)

    return {
        "pair": f"{base}/{quote}",
        "days": days,
        "data": rates
    }


@app.post("/api/historical/fetch")
async def fetch_historical_data(
    base: str = Query(..., description="Base currency"),
    quotes: List[str] = Query(..., description="Quote currencies"),
    days: int = Query(30, description="Days of history to fetch"),
    db: Session = Depends(get_db)
):
    """Fetch and store historical data from API"""
    result = historical_service.fetch_and_store_historical_data(
        db, base, quotes, days
    )
    return result


@app.get("/api/historical/change/{base}/{quote}")
async def get_price_change(
    base: str,
    quote: str,
    hours: int = Query(24, description="Period in hours"),
    db: Session = Depends(get_db)
):
    """Get price change over a period"""
    change = historical_service.calculate_price_change(db, base, quote, hours)

    if not change:
        raise HTTPException(status_code=404, detail="No data available for this period")

    return {
        "pair": f"{base}/{quote}",
        "period_hours": hours,
        **change
    }


# ===== Portfolio Endpoints =====

@app.get("/api/portfolio")
async def get_portfolio(db: Session = Depends(get_db)):
    """Get portfolio value and positions"""
    portfolio_value = portfolio_service.calculate_portfolio_value(db)
    return portfolio_value


@app.post("/api/portfolio/position")
async def add_position(
    currency: str = Query(..., description="Currency code"),
    amount: float = Query(..., description="Amount"),
    purchase_price_usd: float = Query(..., description="Purchase price in USD"),
    notes: Optional[str] = Query(None, description="Notes"),
    db: Session = Depends(get_db)
):
    """Add a new currency position"""
    position = portfolio_service.add_position(
        db, currency, amount, purchase_price_usd, notes
    )
    return {
        "id": position.id,
        "currency": position.currency,
        "amount": position.amount,
        "purchase_price_usd": position.purchase_price_usd,
        "purchase_date": position.purchase_date.isoformat()
    }


@app.delete("/api/portfolio/position/{position_id}")
async def delete_position(position_id: int, db: Session = Depends(get_db)):
    """Delete a portfolio position"""
    success = portfolio_service.delete_position(db, position_id)

    if not success:
        raise HTTPException(status_code=404, detail="Position not found")

    return {"message": "Position deleted successfully"}


@app.get("/api/portfolio/allocation")
async def get_allocation(db: Session = Depends(get_db)):
    """Get portfolio allocation by currency"""
    allocation = portfolio_service.get_currency_allocation(db)
    return {"allocation": allocation}


@app.get("/api/portfolio/history")
async def get_position_history(
    currency: Optional[str] = Query(None, description="Filter by currency"),
    db: Session = Depends(get_db)
):
    """Get position history"""
    history = portfolio_service.get_position_history(db, currency)
    return {"history": history}


# ===== Trading Signals Endpoints =====

@app.get("/api/signals/{base}/{quote}")
async def get_signal(
    base: str,
    quote: str,
    use_llm: bool = Query(False, description="Include LLM analysis"),
    db: Session = Depends(get_db)
):
    """Generate trading signal for a currency pair"""
    signal = signals_service.generate_signal(db, base, quote, use_llm)
    return signal


@app.get("/api/signals/recent")
async def get_recent_signals(
    pair: Optional[str] = Query(None, description="Currency pair filter"),
    limit: int = Query(10, description="Number of signals"),
    db: Session = Depends(get_db)
):
    """Get recent trading signals"""
    signals = signals_service.get_recent_signals(db, pair, limit)

    return {
        "signals": [{
            "id": s.id,
            "currency_pair": s.currency_pair,
            "signal": s.signal_type,
            "strength": s.strength,
            "technical_score": s.technical_score,
            "fundamental_score": s.fundamental_score,
            "sentiment_score": s.sentiment_score,
            "timestamp": s.timestamp.isoformat()
        } for s in signals]
    }


@app.post("/api/signals/scan")
async def scan_opportunities(
    signal_type: str = Query("BUY", description="BUY or SELL"),
    min_strength: float = Query(60, description="Minimum signal strength"),
    db: Session = Depends(get_db)
):
    """Scan for trading opportunities across major pairs"""
    # Major currency pairs
    pairs = [
        ("EUR", "USD"), ("USD", "JPY"), ("GBP", "USD"),
        ("USD", "CHF"), ("USD", "CAD"), ("AUD", "USD"),
        ("NZD", "USD"), ("EUR", "GBP"), ("EUR", "JPY")
    ]

    opportunities = signals_service.get_top_opportunities(
        db, pairs, signal_type, min_strength
    )

    return {
        "signal_type": signal_type,
        "min_strength": min_strength,
        "opportunities": opportunities
    }


# ===== News Endpoints =====

@app.get("/api/news")
async def get_news(use_mock: bool = Query(False, description="Use mock data")):
    """Get latest forex news"""
    news = news_service.fetch_latest_news(use_mock)

    return {
        "count": len(news),
        "articles": [{
            "title": article["title"],
            "url": article.get("url"),
            "source": article.get("source"),
            "published_date": article.get("published_date").isoformat() if article.get("published_date") else None
        } for article in news]
    }


@app.get("/api/news/calendar")
async def get_economic_calendar():
    """Get economic calendar events"""
    events = news_service.get_economic_calendar_events()

    return {
        "events": [{
            "event": e["event"],
            "currency": e["currency"],
            "impact": e["impact"],
            "forecast": e.get("forecast"),
            "previous": e.get("previous"),
            "datetime": e["datetime"].isoformat()
        } for e in events]
    }


# ===== LLM Analysis Endpoints =====

@app.post("/api/analysis/currency-pair")
async def analyze_currency_pair(
    base: str = Query(..., description="Base currency"),
    quote: str = Query(..., description="Quote currency"),
    db: Session = Depends(get_db)
):
    """Get AI-powered analysis of a currency pair"""
    # Get technical indicators
    prices = historical_service.get_price_series(db, base, quote, days=60)

    if len(prices) < 20:
        raise HTTPException(status_code=400, detail="Insufficient historical data")

    signal = technical_analysis.generate_signal(prices)

    # Get news
    news = news_service.fetch_latest_news(use_mock=True)
    recent_headlines = [article["title"] for article in news[:5]]

    # Get LLM analysis
    analysis = llm_service.analyze_currency_pair(
        f"{base}/{quote}",
        signal["indicators"],
        recent_headlines
    )

    if not analysis:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    return {
        "currency_pair": f"{base}/{quote}",
        "technical_indicators": signal["indicators"],
        "recent_news": recent_headlines,
        "ai_analysis": analysis
    }


@app.get("/api/analysis/daily-summary")
async def get_daily_summary(db: Session = Depends(get_db)):
    """Get AI-generated daily market summary"""
    # Calculate top movers
    major_pairs = [
        ("EUR", "USD"), ("USD", "JPY"), ("GBP", "USD"),
        ("USD", "CHF"), ("AUD", "USD")
    ]

    top_movers = []
    for base, quote in major_pairs:
        change = historical_service.calculate_price_change(db, base, quote, 24)
        if change:
            top_movers.append({
                "pair": f"{base}/{quote}",
                "current_rate": change["current_rate"],
                "change_pct": change["change_percent"]
            })

    # Sort by absolute change
    top_movers.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

    # Get events
    events = news_service.get_economic_calendar_events()
    key_events = [
        f"{e['currency']}: {e['event']} ({e['impact']} impact)"
        for e in events[:5]
    ]

    # Generate summary
    summary = llm_service.generate_daily_market_summary(
        top_movers,
        "Mixed",  # Could be calculated based on overall market direction
        key_events
    )

    if not summary:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    return {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "top_movers": top_movers[:5],
        "upcoming_events": key_events,
        "ai_summary": summary
    }


@app.get("/api/analysis/fundamentals/{currency}")
async def get_currency_fundamentals(currency: str):
    """Get explanation of currency fundamentals"""
    explanation = llm_service.explain_currency_fundamentals(currency)

    if not explanation:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    return {
        "currency": currency,
        "explanation": explanation
    }


# ===== Notification Endpoints =====

@app.post("/api/notifications/preferences")
async def create_notification_preference(
    email: Optional[str] = Query(None, description="Email address"),
    phone_number: Optional[str] = Query(None, description="Phone number (E.164 format)"),
    email_enabled: bool = Query(True, description="Enable email notifications"),
    sms_enabled: bool = Query(False, description="Enable SMS notifications"),
    notify_on_buy_signals: bool = Query(True),
    notify_on_sell_signals: bool = Query(True),
    notify_on_price_changes: bool = Query(True),
    min_signal_strength: float = Query(70.0, description="Minimum signal strength (0-100)"),
    price_change_threshold: float = Query(2.0, description="Price change % threshold"),
    watched_currencies: Optional[str] = Query(None, description="Comma-separated pairs (e.g., EUR/USD,GBP/USD)"),
    notification_frequency: str = Query("daily", description="instant, hourly, or daily"),
    quiet_hours_start: Optional[str] = Query(None, description="Quiet hours start (HH:MM)"),
    quiet_hours_end: Optional[str] = Query(None, description="Quiet hours end (HH:MM)"),
    db: Session = Depends(get_db)
):
    """Create or update notification preferences"""

    if not email and not phone_number:
        raise HTTPException(status_code=400, detail="Must provide email or phone number")

    # Check if preference already exists
    existing = None
    if email:
        existing = db.query(NotificationPreference).filter(
            NotificationPreference.email == email
        ).first()
    elif phone_number:
        existing = db.query(NotificationPreference).filter(
            NotificationPreference.phone_number == phone_number
        ).first()

    if existing:
        # Update existing preference
        existing.email = email
        existing.phone_number = phone_number
        existing.email_enabled = email_enabled
        existing.sms_enabled = sms_enabled
        existing.notify_on_buy_signals = notify_on_buy_signals
        existing.notify_on_sell_signals = notify_on_sell_signals
        existing.notify_on_price_changes = notify_on_price_changes
        existing.min_signal_strength = min_signal_strength
        existing.price_change_threshold = price_change_threshold
        existing.watched_currencies = watched_currencies
        existing.notification_frequency = notification_frequency
        existing.quiet_hours_start = quiet_hours_start
        existing.quiet_hours_end = quiet_hours_end
        existing.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing)
        pref = existing
    else:
        # Create new preference
        pref = NotificationPreference(
            email=email,
            phone_number=phone_number,
            email_enabled=email_enabled,
            sms_enabled=sms_enabled,
            notify_on_buy_signals=notify_on_buy_signals,
            notify_on_sell_signals=notify_on_sell_signals,
            notify_on_price_changes=notify_on_price_changes,
            min_signal_strength=min_signal_strength,
            price_change_threshold=price_change_threshold,
            watched_currencies=watched_currencies,
            notification_frequency=notification_frequency,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end
        )

        db.add(pref)
        db.commit()
        db.refresh(pref)

    return {
        "id": pref.id,
        "email": pref.email,
        "phone_number": pref.phone_number,
        "email_enabled": pref.email_enabled,
        "sms_enabled": pref.sms_enabled,
        "notify_on_buy_signals": pref.notify_on_buy_signals,
        "notify_on_sell_signals": pref.notify_on_sell_signals,
        "notify_on_price_changes": pref.notify_on_price_changes,
        "min_signal_strength": pref.min_signal_strength,
        "price_change_threshold": pref.price_change_threshold,
        "watched_currencies": pref.watched_currencies,
        "notification_frequency": pref.notification_frequency,
        "quiet_hours_start": pref.quiet_hours_start,
        "quiet_hours_end": pref.quiet_hours_end
    }


@app.get("/api/notifications/preferences")
async def get_notification_preferences(db: Session = Depends(get_db)):
    """Get all notification preferences"""
    preferences = db.query(NotificationPreference).all()

    return {
        "preferences": [{
            "id": p.id,
            "email": p.email,
            "phone_number": p.phone_number,
            "email_enabled": p.email_enabled,
            "sms_enabled": p.sms_enabled,
            "min_signal_strength": p.min_signal_strength,
            "watched_currencies": p.watched_currencies
        } for p in preferences]
    }


@app.delete("/api/notifications/preferences/{preference_id}")
async def delete_notification_preference(
    preference_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification preference"""
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.id == preference_id
    ).first()

    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")

    db.delete(pref)
    db.commit()

    return {"message": "Preference deleted successfully"}


@app.post("/api/notifications/test-email")
async def test_email(
    email: str = Query(..., description="Email to test"),
):
    """Send a test email"""
    success, error = notification_service.test_email_configuration(email)

    if not success:
        raise HTTPException(status_code=500, detail=error or "Failed to send email")

    return {"message": "Test email sent successfully"}


@app.post("/api/notifications/test-sms")
async def test_sms(
    phone: str = Query(..., description="Phone number to test (E.164 format)"),
):
    """Send a test SMS"""
    success, error = notification_service.test_sms_configuration(phone)

    if not success:
        raise HTTPException(status_code=500, detail=error or "Failed to send SMS")

    return {"message": "Test SMS sent successfully"}


@app.get("/api/notifications/logs")
async def get_notification_logs(
    limit: int = Query(50, description="Number of logs to retrieve"),
    db: Session = Depends(get_db)
):
    """Get notification logs"""
    logs = db.query(NotificationLog).order_by(
        NotificationLog.sent_at.desc()
    ).limit(limit).all()

    return {
        "logs": [{
            "id": log.id,
            "type": log.notification_type,
            "method": log.method,
            "recipient": log.recipient,
            "subject": log.subject,
            "sent_at": log.sent_at.isoformat(),
            "success": log.success,
            "error_message": log.error_message
        } for log in logs]
    }


@app.post("/api/notifications/trigger-check")
async def trigger_notification_check():
    """Manually trigger a notification check (for testing)"""
    try:
        scheduler.trigger_manual_check()
        return {"message": "Notification check triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Health Check =====

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
