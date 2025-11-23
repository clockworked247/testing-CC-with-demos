"""
Database models and setup for the currency trading application.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import config

Base = declarative_base()

class ExchangeRate(Base):
    """Historical exchange rate data"""
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3), nullable=False, index=True)
    quote_currency = Column(String(3), nullable=False, index=True)
    rate = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), default="frankfurter")

    def __repr__(self):
        return f"<ExchangeRate {self.base_currency}/{self.quote_currency}: {self.rate}>"


class Portfolio(Base):
    """User's currency portfolio"""
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(3), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    purchase_price_usd = Column(Float, nullable=False)  # Price in USD when purchased
    purchase_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Portfolio {self.amount} {self.currency} @ ${self.purchase_price_usd}>"


class TradingSignal(Base):
    """Generated trading signals"""
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True)
    currency_pair = Column(String(7), nullable=False, index=True)  # e.g., EUR/USD
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    strength = Column(Float, nullable=False)  # 0-100
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Signal components
    technical_score = Column(Float, default=0.0)
    fundamental_score = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)

    # Analysis details
    reasoning = Column(Text, nullable=True)
    indicators = Column(Text, nullable=True)  # JSON string of indicator values

    def __repr__(self):
        return f"<TradingSignal {self.currency_pair}: {self.signal_type} ({self.strength})>"


class EconomicIndicator(Base):
    """Economic indicators from IMF and other sources"""
    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(3), nullable=False, index=True)  # ISO 3-letter code
    indicator_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), default="imf")
    period = Column(String(20), nullable=True)  # e.g., "2024-Q4"

    def __repr__(self):
        return f"<EconomicIndicator {self.country} {self.indicator_name}: {self.value}>"


class NewsArticle(Base):
    """News articles for sentiment analysis"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    content = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    published_date = Column(DateTime, nullable=True)
    fetched_date = Column(DateTime, default=datetime.utcnow)

    # Sentiment analysis results
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    currencies_mentioned = Column(String(100), nullable=True)  # Comma-separated
    llm_analysis = Column(Text, nullable=True)

    def __repr__(self):
        return f"<NewsArticle {self.title[:50]}...>"


class LLMAnalysis(Base):
    """LLM-generated analysis and insights"""
    __tablename__ = "llm_analysis"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False)  # daily_summary, signal_analysis, etc.
    currency_pair = Column(String(7), nullable=True, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    tokens_used = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<LLMAnalysis {self.analysis_type} for {self.currency_pair}>"


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone_number = Column(String(20), nullable=True)

    # Notification methods
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)

    # What to notify about
    notify_on_buy_signals = Column(Boolean, default=True)
    notify_on_sell_signals = Column(Boolean, default=True)
    notify_on_price_changes = Column(Boolean, default=True)
    notify_on_portfolio_changes = Column(Boolean, default=False)

    # Thresholds
    min_signal_strength = Column(Float, default=70.0)  # Only notify for signals >= this strength
    price_change_threshold = Column(Float, default=2.0)  # Notify if price changes > this %

    # Currencies to watch (comma-separated)
    watched_currencies = Column(String(500), nullable=True)  # e.g., "EUR/USD,GBP/USD"

    # Schedule
    notification_frequency = Column(String(20), default="daily")  # instant, hourly, daily
    quiet_hours_start = Column(String(5), nullable=True)  # e.g., "22:00"
    quiet_hours_end = Column(String(5), nullable=True)  # e.g., "08:00"

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<NotificationPreference {self.email or self.phone_number}>"


class NotificationLog(Base):
    """Log of sent notifications"""
    __tablename__ = "notification_log"

    id = Column(Integer, primary_key=True, index=True)
    preference_id = Column(Integer, ForeignKey("notification_preferences.id"), nullable=True)
    notification_type = Column(String(50), nullable=False)  # signal, price_change, portfolio
    method = Column(String(10), nullable=False)  # email or sms
    recipient = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<NotificationLog {self.method} to {self.recipient} at {self.sent_at}>"


# Database engine and session
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
