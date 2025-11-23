"""
Currency data fetching service using public APIs.
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CurrencyService:
    """Service for fetching currency exchange rates"""

    def __init__(self):
        self.frankfurter_url = config.FRANKFURTER_API_URL
        self.exchangerate_url = config.EXCHANGERATE_API_URL

    def get_latest_rates(self, base: str = "USD") -> Optional[Dict]:
        """
        Get latest exchange rates for a base currency.

        Args:
            base: Base currency (default USD)

        Returns:
            Dictionary with rates or None if error
        """
        try:
            # Try Frankfurter first (no API key needed)
            response = requests.get(
                f"{self.frankfurter_url}/latest",
                params={"from": base},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                "base": data.get("base"),
                "date": data.get("date"),
                "rates": data.get("rates", {}),
                "timestamp": datetime.utcnow(),
                "source": "frankfurter"
            }

        except Exception as e:
            logger.error(f"Error fetching latest rates from Frankfurter: {e}")

            # Fallback to exchangerate.host
            try:
                response = requests.get(
                    f"{self.exchangerate_url}/latest",
                    params={"base": base},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    return {
                        "base": data.get("base"),
                        "date": data.get("date"),
                        "rates": data.get("rates", {}),
                        "timestamp": datetime.utcnow(),
                        "source": "exchangerate.host"
                    }
            except Exception as e2:
                logger.error(f"Error fetching latest rates from exchangerate.host: {e2}")

        return None

    def get_historical_rates(
        self,
        base: str = "USD",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        currencies: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Get historical exchange rates.

        Args:
            base: Base currency
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            currencies: List of currencies to fetch

        Returns:
            Dictionary with historical rates
        """
        if not start_date:
            # Default to last 30 days
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")

        try:
            # Frankfurter supports time series
            url = f"{self.frankfurter_url}/{start_date}..{end_date}"
            params = {"from": base}

            if currencies:
                params["to"] = ",".join(currencies)

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                "base": data.get("base"),
                "start_date": start_date,
                "end_date": end_date,
                "rates": data.get("rates", {}),
                "source": "frankfurter"
            }

        except Exception as e:
            logger.error(f"Error fetching historical rates: {e}")
            return None

    def get_rate_for_pair(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get current exchange rate for a specific currency pair.

        Args:
            from_currency: Source currency
            to_currency: Target currency

        Returns:
            Exchange rate or None
        """
        try:
            response = requests.get(
                f"{self.frankfurter_url}/latest",
                params={"from": from_currency, "to": to_currency},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            rates = data.get("rates", {})
            return rates.get(to_currency)

        except Exception as e:
            logger.error(f"Error fetching rate for {from_currency}/{to_currency}: {e}")
            return None

    def get_multiple_base_rates(self, bases: List[str]) -> Dict[str, Dict]:
        """
        Get latest rates for multiple base currencies.

        Args:
            bases: List of base currencies

        Returns:
            Dictionary mapping base currency to rates
        """
        results = {}

        for base in bases:
            rates = self.get_latest_rates(base)
            if rates:
                results[base] = rates
            else:
                logger.warning(f"Could not fetch rates for {base}")

        return results

    def convert_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Optional[float]:
        """
        Convert an amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency

        Returns:
            Converted amount or None
        """
        rate = self.get_rate_for_pair(from_currency, to_currency)
        if rate:
            return amount * rate
        return None

    def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies.

        Returns:
            List of currency codes
        """
        try:
            response = requests.get(f"{self.frankfurter_url}/currencies", timeout=10)
            response.raise_for_status()
            currencies = response.json()
            return list(currencies.keys())

        except Exception as e:
            logger.error(f"Error fetching supported currencies: {e}")
            return config.CURRENCIES  # Return configured list as fallback


# Singleton instance
currency_service = CurrencyService()
