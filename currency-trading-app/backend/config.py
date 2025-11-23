"""
Configuration management for the currency trading application.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/trading.db")

    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")  # Optional: newsapi.org

    # Currency APIs (these are free and don't require keys)
    FRANKFURTER_API_URL = "https://api.frankfurter.app"
    EXCHANGERATE_API_URL = "https://api.exchangerate.host"

    # IMF API (free, no key required)
    IMF_API_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

    # OpenRouter Configuration
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")

    # Trading Configuration
    MAJOR_CURRENCY_PAIRS = [
        "EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF",
        "USD/CAD", "AUD/USD", "NZD/USD", "USD/SGD",
        "USD/INR", "EUR/GBP", "EUR/JPY"
    ]

    # Supported currencies
    CURRENCIES = [
        "USD", "EUR", "GBP", "JPY", "CHF", "CAD",
        "AUD", "NZD", "SGD", "INR", "CNY", "HKD",
        "SEK", "NOK", "DKK", "MXN", "BRL"
    ]

    # Technical Analysis Parameters
    MA_SHORT_PERIOD = 20  # Short-term moving average
    MA_LONG_PERIOD = 50   # Long-term moving average
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    # Data Update Intervals (in seconds)
    REALTIME_UPDATE_INTERVAL = 300  # 5 minutes
    HISTORICAL_UPDATE_INTERVAL = 3600  # 1 hour
    NEWS_UPDATE_INTERVAL = 1800  # 30 minutes

config = Config()
