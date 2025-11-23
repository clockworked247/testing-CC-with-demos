"""
Historical data management service.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging

from database import ExchangeRate
from services.currency_service import currency_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoricalDataService:
    """Service for managing historical exchange rate data"""

    def store_rate(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str,
        rate: float,
        source: str = "frankfurter"
    ) -> ExchangeRate:
        """
        Store an exchange rate in the database.

        Args:
            db: Database session
            base_currency: Base currency code
            quote_currency: Quote currency code
            rate: Exchange rate
            source: Data source

        Returns:
            Created ExchangeRate entry
        """
        rate_entry = ExchangeRate(
            base_currency=base_currency.upper(),
            quote_currency=quote_currency.upper(),
            rate=rate,
            timestamp=datetime.utcnow(),
            source=source
        )

        db.add(rate_entry)
        db.commit()
        db.refresh(rate_entry)

        return rate_entry

    def store_multiple_rates(
        self,
        db: Session,
        base_currency: str,
        rates: Dict[str, float],
        source: str = "frankfurter"
    ) -> int:
        """
        Store multiple exchange rates.

        Args:
            db: Database session
            base_currency: Base currency
            rates: Dictionary of quote_currency: rate
            source: Data source

        Returns:
            Number of rates stored
        """
        count = 0
        timestamp = datetime.utcnow()

        for quote_currency, rate in rates.items():
            rate_entry = ExchangeRate(
                base_currency=base_currency.upper(),
                quote_currency=quote_currency.upper(),
                rate=rate,
                timestamp=timestamp,
                source=source
            )
            db.add(rate_entry)
            count += 1

        db.commit()
        logger.info(f"Stored {count} exchange rates for {base_currency}")
        return count

    def get_latest_rate(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str
    ) -> Optional[ExchangeRate]:
        """
        Get the most recent exchange rate.

        Args:
            db: Database session
            base_currency: Base currency
            quote_currency: Quote currency

        Returns:
            Latest ExchangeRate or None
        """
        return db.query(ExchangeRate).filter(
            ExchangeRate.base_currency == base_currency.upper(),
            ExchangeRate.quote_currency == quote_currency.upper()
        ).order_by(ExchangeRate.timestamp.desc()).first()

    def get_historical_rates(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ExchangeRate]:
        """
        Get historical exchange rates for a currency pair.

        Args:
            db: Database session
            base_currency: Base currency
            quote_currency: Quote currency
            start_date: Start date (optional)
            end_date: End date (optional)
            limit: Maximum number of results

        Returns:
            List of ExchangeRate entries
        """
        query = db.query(ExchangeRate).filter(
            ExchangeRate.base_currency == base_currency.upper(),
            ExchangeRate.quote_currency == quote_currency.upper()
        )

        if start_date:
            query = query.filter(ExchangeRate.timestamp >= start_date)

        if end_date:
            query = query.filter(ExchangeRate.timestamp <= end_date)

        return query.order_by(ExchangeRate.timestamp.desc()).limit(limit).all()

    def get_rates_for_period(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get exchange rates for the last N days.

        Args:
            db: Database session
            base_currency: Base currency
            quote_currency: Quote currency
            days: Number of days to look back

        Returns:
            List of rate dictionaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        rates = self.get_historical_rates(
            db,
            base_currency,
            quote_currency,
            start_date=start_date
        )

        return [{
            "timestamp": rate.timestamp.isoformat(),
            "rate": rate.rate,
            "source": rate.source
        } for rate in reversed(rates)]

    def fetch_and_store_historical_data(
        self,
        db: Session,
        base_currency: str,
        quote_currencies: List[str],
        days: int = 30
    ) -> Dict:
        """
        Fetch historical data from API and store in database.

        Args:
            db: Database session
            base_currency: Base currency
            quote_currencies: List of quote currencies
            days: Number of days of history to fetch

        Returns:
            Summary of operation
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        # Fetch from API
        historical_data = currency_service.get_historical_rates(
            base=base_currency,
            start_date=start_date,
            end_date=end_date,
            currencies=quote_currencies
        )

        if not historical_data or "rates" not in historical_data:
            logger.error("Failed to fetch historical data")
            return {"success": False, "error": "Failed to fetch data"}

        total_stored = 0
        rates_by_date = historical_data["rates"]

        # Store each day's rates
        for date_str, currencies in rates_by_date.items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                for quote_currency, rate in currencies.items():
                    rate_entry = ExchangeRate(
                        base_currency=base_currency.upper(),
                        quote_currency=quote_currency.upper(),
                        rate=rate,
                        timestamp=date_obj,
                        source=historical_data.get("source", "frankfurter")
                    )
                    db.add(rate_entry)
                    total_stored += 1

            except Exception as e:
                logger.error(f"Error storing rate for {date_str}: {e}")
                continue

        db.commit()

        logger.info(f"Stored {total_stored} historical exchange rates")
        return {
            "success": True,
            "base_currency": base_currency,
            "days": days,
            "total_stored": total_stored
        }

    def get_price_series(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str,
        days: int = 30
    ) -> List[float]:
        """
        Get price series as a simple list of floats (for technical analysis).

        Args:
            db: Database session
            base_currency: Base currency
            quote_currency: Quote currency
            days: Number of days

        Returns:
            List of prices (oldest to newest)
        """
        rates = self.get_rates_for_period(db, base_currency, quote_currency, days)
        return [rate["rate"] for rate in rates]

    def calculate_price_change(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str,
        period_hours: int = 24
    ) -> Optional[Dict]:
        """
        Calculate price change over a period.

        Args:
            db: Database session
            base_currency: Base currency
            quote_currency: Quote currency
            period_hours: Period in hours

        Returns:
            Dictionary with change metrics
        """
        latest = self.get_latest_rate(db, base_currency, quote_currency)
        if not latest:
            return None

        period_start = datetime.utcnow() - timedelta(hours=period_hours)
        old_rate = db.query(ExchangeRate).filter(
            ExchangeRate.base_currency == base_currency.upper(),
            ExchangeRate.quote_currency == quote_currency.upper(),
            ExchangeRate.timestamp >= period_start
        ).order_by(ExchangeRate.timestamp.asc()).first()

        if not old_rate:
            return None

        change = latest.rate - old_rate.rate
        change_percent = (change / old_rate.rate * 100) if old_rate.rate > 0 else 0

        return {
            "current_rate": latest.rate,
            "previous_rate": old_rate.rate,
            "change": change,
            "change_percent": change_percent,
            "period_hours": period_hours
        }


# Singleton instance
historical_service = HistoricalDataService()
