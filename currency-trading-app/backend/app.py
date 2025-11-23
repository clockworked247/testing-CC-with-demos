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

from database import init_db, get_db
from config import config
from services.currency_service import currency_service
from services.historical_service import historical_service
from services.portfolio_service import portfolio_service
from services.technical_analysis import technical_analysis
from services.news_service import news_service
from services.llm_service import llm_service
from services.signals_service import signals_service

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
    """Initialize database on startup"""
    init_db()
    logger.info("Application started successfully")


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
