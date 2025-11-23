"""
News service for fetching forex and financial news.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching financial news relevant to forex trading"""

    def __init__(self):
        # Public RSS feeds and news sources
        self.news_sources = {
            "reuters_forex": "https://www.reuters.com/markets/currencies/",
            "investing_forex": "https://www.investing.com/news/forex-news",
            "forexlive": "https://www.forexlive.com/",
        }

    def fetch_reuters_headlines(self) -> List[Dict]:
        """
        Fetch latest forex headlines from Reuters.

        Returns:
            List of news articles
        """
        articles = []
        try:
            url = self.news_sources["reuters_forex"]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Reuters article structure (may need adjustment based on current site structure)
            article_elements = soup.find_all("a", {"data-testid": re.compile("Heading")})

            for element in article_elements[:10]:
                try:
                    title = element.get_text(strip=True)
                    link = element.get("href", "")

                    if link and not link.startswith("http"):
                        link = "https://www.reuters.com" + link

                    if title:
                        articles.append({
                            "title": title,
                            "url": link,
                            "source": "Reuters",
                            "published_date": datetime.utcnow(),
                            "content": ""
                        })
                except Exception as e:
                    logger.debug(f"Error parsing Reuters article: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Reuters headlines: {e}")

        return articles

    def fetch_generic_forex_news(self) -> List[Dict]:
        """
        Fetch forex news from multiple public sources.

        Returns:
            List of news articles
        """
        all_articles = []

        # Add Reuters
        all_articles.extend(self.fetch_reuters_headlines())

        # You can add more sources here
        # all_articles.extend(self.fetch_other_source())

        return all_articles

    def search_currency_mentions(self, articles: List[Dict], currencies: List[str]) -> Dict:
        """
        Search for currency mentions in articles.

        Args:
            articles: List of article dictionaries
            currencies: List of currency codes to search for

        Returns:
            Dictionary mapping currencies to articles mentioning them
        """
        currency_mentions = {currency: [] for currency in currencies}

        for article in articles:
            title = article.get("title", "").upper()
            content = article.get("content", "").upper()
            combined_text = f"{title} {content}"

            for currency in currencies:
                # Search for currency code and common names
                currency_patterns = [currency]

                # Add common currency names
                currency_names = {
                    "USD": ["DOLLAR", "USD"],
                    "EUR": ["EURO", "EUR"],
                    "GBP": ["POUND", "STERLING", "GBP"],
                    "JPY": ["YEN", "JPY"],
                    "CHF": ["FRANC", "CHF"],
                    "CAD": ["CANADIAN", "CAD"],
                    "AUD": ["AUSSIE", "AUD"],
                    "NZD": ["KIWI", "NZD"],
                    "INR": ["RUPEE", "INR"],
                    "CNY": ["YUAN", "RENMINBI", "CNY"]
                }

                if currency in currency_names:
                    currency_patterns.extend(currency_names[currency])

                for pattern in currency_patterns:
                    if pattern in combined_text:
                        currency_mentions[currency].append(article)
                        break

        return currency_mentions

    def get_mock_headlines(self) -> List[Dict]:
        """
        Get mock headlines for testing when news sources are unavailable.

        Returns:
            List of mock articles
        """
        mock_articles = [
            {
                "title": "Federal Reserve Signals Potential Rate Adjustment Amid Inflation Concerns",
                "url": "https://example.com/fed-rates",
                "source": "Mock Financial News",
                "published_date": datetime.utcnow(),
                "content": "The Federal Reserve indicated today that interest rate adjustments may be necessary to combat persistent inflation pressures."
            },
            {
                "title": "Euro Strengthens Against Dollar as ECB Maintains Hawkish Stance",
                "url": "https://example.com/euro-dollar",
                "source": "Mock Financial News",
                "published_date": datetime.utcnow() - timedelta(hours=2),
                "content": "The euro gained ground against the U.S. dollar following the European Central Bank's commitment to fighting inflation."
            },
            {
                "title": "Japanese Yen Under Pressure as Bank of Japan Maintains Ultra-Loose Policy",
                "url": "https://example.com/yen-policy",
                "source": "Mock Financial News",
                "published_date": datetime.utcnow() - timedelta(hours=4),
                "content": "The yen continues to weaken as the Bank of Japan resists joining other central banks in tightening monetary policy."
            },
            {
                "title": "British Pound Volatile Ahead of GDP Release",
                "url": "https://example.com/gbp-gdp",
                "source": "Mock Financial News",
                "published_date": datetime.utcnow() - timedelta(hours=6),
                "content": "Sterling showed increased volatility as markets await the latest GDP figures from the UK."
            },
            {
                "title": "Emerging Market Currencies Rally on Risk Appetite Return",
                "url": "https://example.com/em-currencies",
                "source": "Mock Financial News",
                "published_date": datetime.utcnow() - timedelta(hours=8),
                "content": "Currencies from emerging markets saw broad gains as investor risk appetite improved on positive economic data."
            }
        ]

        return mock_articles

    def fetch_latest_news(self, use_mock: bool = False) -> List[Dict]:
        """
        Fetch latest forex news.

        Args:
            use_mock: Whether to use mock data (for testing)

        Returns:
            List of news articles
        """
        if use_mock:
            return self.get_mock_headlines()

        articles = self.fetch_generic_forex_news()

        # If no articles fetched, fall back to mock data
        if not articles:
            logger.warning("No articles fetched from sources, using mock data")
            return self.get_mock_headlines()

        return articles

    def get_economic_calendar_events(self) -> List[Dict]:
        """
        Get upcoming economic calendar events (mock data for now).

        In a production app, you would integrate with a real economic calendar API.

        Returns:
            List of economic events
        """
        # Mock economic events
        today = datetime.utcnow()
        events = [
            {
                "event": "US Non-Farm Payrolls",
                "currency": "USD",
                "impact": "HIGH",
                "forecast": "190K",
                "previous": "187K",
                "datetime": today + timedelta(days=2, hours=8, minutes=30)
            },
            {
                "event": "ECB Interest Rate Decision",
                "currency": "EUR",
                "impact": "HIGH",
                "forecast": "4.00%",
                "previous": "4.00%",
                "datetime": today + timedelta(days=3, hours=12, minutes=45)
            },
            {
                "event": "UK GDP Growth Rate",
                "currency": "GBP",
                "impact": "MEDIUM",
                "forecast": "0.2%",
                "previous": "0.1%",
                "datetime": today + timedelta(days=1, hours=7, minutes=0)
            },
            {
                "event": "Japan Trade Balance",
                "currency": "JPY",
                "impact": "MEDIUM",
                "forecast": "-¥500B",
                "previous": "-¥458B",
                "datetime": today + timedelta(hours=18)
            },
            {
                "event": "Australian Employment Change",
                "currency": "AUD",
                "impact": "HIGH",
                "forecast": "20K",
                "previous": "15.9K",
                "datetime": today + timedelta(days=4, hours=1, minutes=30)
            }
        ]

        return events

    def summarize_news_for_currency(self, currency: str, articles: List[Dict]) -> str:
        """
        Create a simple summary of news for a specific currency.

        Args:
            currency: Currency code
            articles: List of articles

        Returns:
            Summary text
        """
        relevant_articles = []

        for article in articles:
            title = article.get("title", "").upper()
            content = article.get("content", "").upper()

            if currency in title or currency in content:
                relevant_articles.append(article["title"])

        if not relevant_articles:
            return f"No recent news found mentioning {currency}."

        summary = f"Recent news mentioning {currency}:\n"
        for i, title in enumerate(relevant_articles[:5], 1):
            summary += f"{i}. {title}\n"

        return summary


# Singleton instance
news_service = NewsService()
