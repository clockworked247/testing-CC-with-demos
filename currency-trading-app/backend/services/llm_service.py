"""
LLM service for qualitative currency analysis using OpenRouter.
"""
import requests
import json
from typing import Dict, List, Optional
import logging

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered qualitative analysis via OpenRouter"""

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.api_url = config.OPENROUTER_API_URL
        self.model = config.DEFAULT_LLM_MODEL

    def _make_request(self, prompt: str, system_message: Optional[str] = None) -> Optional[Dict]:
        """
        Make a request to OpenRouter API.

        Args:
            prompt: User prompt
            system_message: Optional system message

        Returns:
            API response or None
        """
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")
            return None

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yourusername/currency-trading-app",
                "X-Title": "Currency Trading Analysis App"
            }

            payload = {
                "model": self.model,
                "messages": messages
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error making LLM request: {e}")
            return None

    def analyze_currency_pair(
        self,
        currency_pair: str,
        technical_indicators: Dict,
        recent_news: Optional[List[str]] = None,
        economic_data: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Analyze a currency pair using LLM.

        Args:
            currency_pair: Currency pair (e.g., "EUR/USD")
            technical_indicators: Dictionary of technical indicator values
            recent_news: Optional list of recent news headlines
            economic_data: Optional economic indicators

        Returns:
            Analysis text or None
        """
        system_message = """You are an expert forex analyst with deep knowledge of currency markets,
        technical analysis, fundamental analysis, and global economics. Provide concise, actionable
        insights based on the data provided."""

        # Build context
        context_parts = [
            f"Analyze the {currency_pair} currency pair.",
            "\n**Technical Indicators:**"
        ]

        for key, value in technical_indicators.items():
            if value is not None:
                context_parts.append(f"- {key}: {value}")

        if recent_news:
            context_parts.append("\n**Recent News:**")
            for i, headline in enumerate(recent_news[:5], 1):
                context_parts.append(f"{i}. {headline}")

        if economic_data:
            context_parts.append("\n**Economic Data:**")
            for key, value in economic_data.items():
                context_parts.append(f"- {key}: {value}")

        context_parts.append(
            "\nProvide a brief analysis (3-4 paragraphs) covering:\n"
            "1. Technical outlook based on the indicators\n"
            "2. Fundamental factors affecting this pair\n"
            "3. Short-term trading recommendation (bullish/bearish/neutral)\n"
            "4. Key levels to watch and potential risks"
        )

        prompt = "\n".join(context_parts)
        response = self._make_request(prompt, system_message)

        if response and "choices" in response:
            return response["choices"][0]["message"]["content"]

        return None

    def generate_daily_market_summary(
        self,
        top_movers: List[Dict],
        market_sentiment: str,
        key_events: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Generate a daily market summary.

        Args:
            top_movers: List of currency pairs with biggest moves
            market_sentiment: Overall market sentiment
            key_events: List of key events affecting markets

        Returns:
            Summary text or None
        """
        system_message = """You are a professional forex market analyst writing a daily market
        briefing for currency traders. Be concise, informative, and highlight actionable insights."""

        prompt_parts = [
            "Generate a daily forex market summary based on the following data:",
            f"\n**Overall Market Sentiment:** {market_sentiment}",
            "\n**Top Movers Today:**"
        ]

        for mover in top_movers[:10]:
            change_pct = mover.get("change_pct", 0)
            prompt_parts.append(
                f"- {mover['pair']}: {change_pct:+.2f}% ({mover.get('current_rate', 'N/A')})"
            )

        if key_events:
            prompt_parts.append("\n**Key Events:**")
            for event in key_events:
                prompt_parts.append(f"- {event}")

        prompt_parts.append(
            "\nProvide a concise summary (2-3 paragraphs) highlighting:\n"
            "1. Main themes driving currency movements today\n"
            "2. Opportunities and risks for traders\n"
            "3. Key pairs to watch tomorrow"
        )

        prompt = "\n".join(prompt_parts)
        response = self._make_request(prompt, system_message)

        if response and "choices" in response:
            return response["choices"][0]["message"]["content"]

        return None

    def analyze_news_sentiment(self, news_articles: List[Dict]) -> Optional[Dict]:
        """
        Analyze sentiment from news articles.

        Args:
            news_articles: List of news articles with title and content

        Returns:
            Dictionary with sentiment analysis
        """
        if not news_articles:
            return None

        system_message = """You are a financial news analyst specializing in forex markets.
        Analyze the sentiment and potential impact of news on currency markets."""

        prompt_parts = [
            "Analyze the following news articles for forex market sentiment:",
            "\n**Articles:**\n"
        ]

        for i, article in enumerate(news_articles[:10], 1):
            title = article.get("title", "")
            content = article.get("content", "")[:300]  # Limit content length
            prompt_parts.append(f"{i}. **{title}**\n{content}...\n")

        prompt_parts.append(
            "\nProvide:\n"
            "1. Overall sentiment (Very Bearish / Bearish / Neutral / Bullish / Very Bullish)\n"
            "2. Key themes identified\n"
            "3. Which currencies are likely to be most affected and how\n"
            "4. Confidence level (Low / Medium / High)"
        )

        prompt = "\n".join(prompt_parts)
        response = self._make_request(prompt, system_message)

        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            return {
                "analysis": content,
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }

        return None

    def explain_currency_fundamentals(self, currency: str) -> Optional[str]:
        """
        Get an explanation of what drives a specific currency's value.

        Args:
            currency: Currency code (e.g., "USD", "EUR")

        Returns:
            Explanation text or None
        """
        system_message = """You are an expert in international economics and currency markets.
        Explain complex economic concepts in clear, accessible language."""

        prompt = f"""Explain what fundamental factors drive the value of {currency}.

        Cover:
        1. Key economic indicators to watch (interest rates, GDP, inflation, etc.)
        2. The role of the central bank
        3. Political and geopolitical factors
        4. Trade relationships and current account balance
        5. How global events typically affect this currency

        Keep it concise (4-5 paragraphs) and practical for traders."""

        response = self._make_request(prompt, system_message)

        if response and "choices" in response:
            return response["choices"][0]["message"]["content"]

        return None

    def generate_trading_strategy(
        self,
        currency_pair: str,
        risk_tolerance: str,
        timeframe: str,
        market_conditions: Dict
    ) -> Optional[str]:
        """
        Generate a trading strategy recommendation.

        Args:
            currency_pair: Currency pair to trade
            risk_tolerance: "low", "medium", or "high"
            timeframe: "short" (day trading), "medium" (swing), or "long" (position)
            market_conditions: Current market data

        Returns:
            Strategy recommendation or None
        """
        system_message = """You are an experienced forex trader and strategy advisor.
        Provide practical, risk-aware trading strategies."""

        prompt = f"""Generate a trading strategy for {currency_pair}.

        **Parameters:**
        - Risk Tolerance: {risk_tolerance}
        - Timeframe: {timeframe}

        **Current Market Conditions:**
        {json.dumps(market_conditions, indent=2)}

        Provide:
        1. Entry strategy and levels
        2. Stop-loss placement
        3. Take-profit targets
        4. Position sizing recommendation
        5. Risk management considerations
        6. Alternative scenarios (what if analysis)

        Be specific and actionable."""

        response = self._make_request(prompt, system_message)

        if response and "choices" in response:
            return response["choices"][0]["message"]["content"]

        return None


# Singleton instance
llm_service = LLMService()
