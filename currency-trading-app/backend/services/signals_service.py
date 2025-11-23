"""
Trading signals service combining technical, fundamental, and sentiment analysis.
"""
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import logging

from database import TradingSignal
from services.technical_analysis import technical_analysis
from services.historical_service import historical_service
from services.news_service import news_service
from services.llm_service import llm_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalsService:
    """Service for generating comprehensive trading signals"""

    def generate_signal(
        self,
        db: Session,
        base_currency: str,
        quote_currency: str,
        use_llm: bool = True
    ) -> Dict:
        """
        Generate a comprehensive trading signal for a currency pair.

        Args:
            db: Database session
            base_currency: Base currency
            quote_currency: Quote currency
            use_llm: Whether to use LLM for qualitative analysis

        Returns:
            Comprehensive signal dictionary
        """
        currency_pair = f"{base_currency}/{quote_currency}"

        # 1. Get historical price data
        prices = historical_service.get_price_series(db, base_currency, quote_currency, days=90)

        if len(prices) < 20:
            return {
                "currency_pair": currency_pair,
                "signal": "HOLD",
                "strength": 0,
                "error": "Insufficient historical data"
            }

        # 2. Technical Analysis
        technical_signal = technical_analysis.generate_signal(prices)

        technical_score = 0
        if technical_signal["signal"] == "BUY":
            technical_score = technical_signal["strength"]
        elif technical_signal["signal"] == "SELL":
            technical_score = -technical_signal["strength"]

        # 3. News Sentiment Analysis
        sentiment_score = 0
        news_summary = ""

        try:
            news_articles = news_service.fetch_latest_news(use_mock=True)
            currency_mentions = news_service.search_currency_mentions(
                news_articles,
                [base_currency, quote_currency]
            )

            # Simple sentiment based on news volume
            base_news_count = len(currency_mentions.get(base_currency, []))
            quote_news_count = len(currency_mentions.get(quote_currency, []))

            if base_news_count > quote_news_count:
                sentiment_score = 10  # Slight positive bias
                news_summary = f"{base_currency} has more news coverage ({base_news_count} vs {quote_news_count})"
            elif quote_news_count > base_news_count:
                sentiment_score = -10  # Slight negative bias
                news_summary = f"{quote_currency} has more news coverage ({quote_news_count} vs {base_news_count})"
            else:
                news_summary = "Balanced news coverage"

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            news_summary = "News analysis unavailable"

        # 4. Combine scores
        # Weight: Technical (60%), Sentiment (20%), Fundamental (20%)
        fundamental_score = 0  # Placeholder for now

        combined_score = (
            technical_score * 0.6 +
            sentiment_score * 0.2 +
            fundamental_score * 0.2
        )

        # Determine final signal
        if combined_score > 20:
            final_signal = "BUY"
            strength = min(abs(combined_score), 100)
        elif combined_score < -20:
            final_signal = "SELL"
            strength = min(abs(combined_score), 100)
        else:
            final_signal = "HOLD"
            strength = 50

        # 5. LLM Analysis (if enabled)
        llm_analysis = None
        if use_llm:
            try:
                recent_news = [article["title"] for article in news_articles[:5]]
                llm_analysis = llm_service.analyze_currency_pair(
                    currency_pair,
                    technical_signal["indicators"],
                    recent_news
                )
            except Exception as e:
                logger.error(f"Error in LLM analysis: {e}")

        # 6. Create signal object
        result = {
            "currency_pair": currency_pair,
            "signal": final_signal,
            "strength": round(strength, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "technical_analysis": {
                "signal": technical_signal["signal"],
                "strength": technical_signal["strength"],
                "indicators": technical_signal["indicators"],
                "reason": technical_signal["reason"]
            },
            "sentiment_analysis": {
                "score": sentiment_score,
                "summary": news_summary
            },
            "fundamental_analysis": {
                "score": fundamental_score,
                "note": "Fundamental analysis coming soon"
            },
            "combined_score": round(combined_score, 2),
            "llm_analysis": llm_analysis
        }

        return result

    def store_signal(
        self,
        db: Session,
        signal_data: Dict
    ) -> TradingSignal:
        """
        Store a trading signal in the database.

        Args:
            db: Database session
            signal_data: Signal data dictionary

        Returns:
            Created TradingSignal
        """
        technical_strength = signal_data.get("technical_analysis", {}).get("strength", 0)
        sentiment_score = signal_data.get("sentiment_analysis", {}).get("score", 0)
        fundamental_score = signal_data.get("fundamental_analysis", {}).get("score", 0)

        signal = TradingSignal(
            currency_pair=signal_data["currency_pair"],
            signal_type=signal_data["signal"],
            strength=signal_data["strength"],
            technical_score=technical_strength,
            fundamental_score=fundamental_score,
            sentiment_score=sentiment_score,
            reasoning=signal_data.get("technical_analysis", {}).get("reason", ""),
            indicators=str(signal_data.get("technical_analysis", {}).get("indicators", {}))
        )

        db.add(signal)
        db.commit()
        db.refresh(signal)

        return signal

    def get_recent_signals(
        self,
        db: Session,
        currency_pair: Optional[str] = None,
        limit: int = 10
    ) -> List[TradingSignal]:
        """
        Get recent trading signals.

        Args:
            db: Database session
            currency_pair: Optional currency pair filter
            limit: Maximum number of signals

        Returns:
            List of TradingSignal objects
        """
        query = db.query(TradingSignal)

        if currency_pair:
            query = query.filter(TradingSignal.currency_pair == currency_pair)

        return query.order_by(TradingSignal.timestamp.desc()).limit(limit).all()

    def generate_multiple_signals(
        self,
        db: Session,
        currency_pairs: List[tuple],
        use_llm: bool = False  # Default to False for bulk operations
    ) -> List[Dict]:
        """
        Generate signals for multiple currency pairs.

        Args:
            db: Database session
            currency_pairs: List of (base, quote) tuples
            use_llm: Whether to use LLM analysis

        Returns:
            List of signal dictionaries
        """
        signals = []

        for base, quote in currency_pairs:
            try:
                signal = self.generate_signal(db, base, quote, use_llm=use_llm)
                signals.append(signal)

                # Store in database
                self.store_signal(db, signal)

            except Exception as e:
                logger.error(f"Error generating signal for {base}/{quote}: {e}")
                continue

        return signals

    def get_top_opportunities(
        self,
        db: Session,
        currency_pairs: List[tuple],
        signal_type: str = "BUY",
        min_strength: float = 60
    ) -> List[Dict]:
        """
        Get top trading opportunities based on signal strength.

        Args:
            db: Database session
            currency_pairs: List of currency pairs to analyze
            signal_type: "BUY" or "SELL"
            min_strength: Minimum signal strength

        Returns:
            List of top opportunities
        """
        signals = self.generate_multiple_signals(db, currency_pairs, use_llm=False)

        # Filter by signal type and strength
        opportunities = [
            s for s in signals
            if s["signal"] == signal_type and s["strength"] >= min_strength
        ]

        # Sort by strength
        opportunities.sort(key=lambda x: x["strength"], reverse=True)

        return opportunities


# Singleton instance
signals_service = SignalsService()
