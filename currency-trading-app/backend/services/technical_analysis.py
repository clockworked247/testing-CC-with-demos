"""
Technical analysis service for currency trading signals.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Service for calculating technical indicators"""

    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """
        Calculate Simple Moving Average.

        Args:
            prices: List of prices
            period: Period for SMA

        Returns:
            List of SMA values
        """
        if len(prices) < period:
            return [np.nan] * len(prices)

        df = pd.DataFrame({"price": prices})
        sma = df["price"].rolling(window=period).mean()
        return sma.tolist()

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """
        Calculate Exponential Moving Average.

        Args:
            prices: List of prices
            period: Period for EMA

        Returns:
            List of EMA values
        """
        if len(prices) < period:
            return [np.nan] * len(prices)

        df = pd.DataFrame({"price": prices})
        ema = df["price"].ewm(span=period, adjust=False).mean()
        return ema.tolist()

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """
        Calculate Relative Strength Index.

        Args:
            prices: List of prices
            period: Period for RSI (default 14)

        Returns:
            List of RSI values (0-100)
        """
        if len(prices) < period + 1:
            return [np.nan] * len(prices)

        df = pd.DataFrame({"price": prices})

        # Calculate price changes
        delta = df["price"].diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0.0)
        losses = -delta.where(delta < 0, 0.0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi.tolist()

    @staticmethod
    def calculate_macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: List of prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        if len(prices) < slow_period:
            return [np.nan] * len(prices), [np.nan] * len(prices), [np.nan] * len(prices)

        df = pd.DataFrame({"price": prices})

        # Calculate EMAs
        ema_fast = df["price"].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df["price"].ewm(span=slow_period, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        return macd_line.tolist(), signal_line.tolist(), histogram.tolist()

    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Calculate Bollinger Bands.

        Args:
            prices: List of prices
            period: Period for moving average
            std_dev: Number of standard deviations

        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        if len(prices) < period:
            return [np.nan] * len(prices), [np.nan] * len(prices), [np.nan] * len(prices)

        df = pd.DataFrame({"price": prices})

        # Middle band (SMA)
        middle_band = df["price"].rolling(window=period).mean()

        # Standard deviation
        std = df["price"].rolling(window=period).std()

        # Upper and lower bands
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band.tolist(), middle_band.tolist(), lower_band.tolist()

    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> List[float]:
        """
        Calculate price volatility (standard deviation).

        Args:
            prices: List of prices
            period: Period for calculation

        Returns:
            List of volatility values
        """
        if len(prices) < period:
            return [np.nan] * len(prices)

        df = pd.DataFrame({"price": prices})
        volatility = df["price"].rolling(window=period).std()
        return volatility.tolist()

    @staticmethod
    def identify_trend(prices: List[float], short_period: int = 20, long_period: int = 50) -> str:
        """
        Identify current trend based on moving averages.

        Args:
            prices: List of prices
            short_period: Short-term MA period
            long_period: Long-term MA period

        Returns:
            "UPTREND", "DOWNTREND", or "NEUTRAL"
        """
        if len(prices) < long_period:
            return "NEUTRAL"

        short_ma = TechnicalAnalysisService.calculate_sma(prices, short_period)
        long_ma = TechnicalAnalysisService.calculate_sma(prices, long_period)

        # Get latest non-NaN values
        short_latest = None
        long_latest = None

        for i in range(len(short_ma) - 1, -1, -1):
            if not np.isnan(short_ma[i]) and short_latest is None:
                short_latest = short_ma[i]
            if not np.isnan(long_ma[i]) and long_latest is None:
                long_latest = long_ma[i]
            if short_latest is not None and long_latest is not None:
                break

        if short_latest is None or long_latest is None:
            return "NEUTRAL"

        # Golden cross / Death cross
        if short_latest > long_latest * 1.001:  # 0.1% threshold
            return "UPTREND"
        elif short_latest < long_latest * 0.999:
            return "DOWNTREND"
        else:
            return "NEUTRAL"

    @staticmethod
    def generate_signal(
        prices: List[float],
        short_ma_period: int = 20,
        long_ma_period: int = 50,
        rsi_period: int = 14
    ) -> Dict:
        """
        Generate a comprehensive trading signal based on multiple indicators.

        Args:
            prices: List of historical prices
            short_ma_period: Short-term MA period
            long_ma_period: Long-term MA period
            rsi_period: RSI period

        Returns:
            Dictionary with signal information
        """
        if len(prices) < long_ma_period:
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": "Insufficient data for analysis"
            }

        # Calculate indicators
        short_ma = TechnicalAnalysisService.calculate_sma(prices, short_ma_period)
        long_ma = TechnicalAnalysisService.calculate_sma(prices, long_ma_period)
        rsi = TechnicalAnalysisService.calculate_rsi(prices, rsi_period)
        macd_line, signal_line, histogram = TechnicalAnalysisService.calculate_macd(prices)
        upper_bb, middle_bb, lower_bb = TechnicalAnalysisService.calculate_bollinger_bands(prices)

        # Get latest values
        current_price = prices[-1]
        latest_short_ma = next((x for x in reversed(short_ma) if not np.isnan(x)), None)
        latest_long_ma = next((x for x in reversed(long_ma) if not np.isnan(x)), None)
        latest_rsi = next((x for x in reversed(rsi) if not np.isnan(x)), None)
        latest_macd = next((x for x in reversed(macd_line) if not np.isnan(x)), None)
        latest_signal = next((x for x in reversed(signal_line) if not np.isnan(x)), None)
        latest_upper_bb = next((x for x in reversed(upper_bb) if not np.isnan(x)), None)
        latest_lower_bb = next((x for x in reversed(lower_bb) if not np.isnan(x)), None)

        # Signal scoring
        buy_signals = 0
        sell_signals = 0
        reasons = []

        # 1. Moving Average Crossover
        if latest_short_ma and latest_long_ma:
            if latest_short_ma > latest_long_ma:
                buy_signals += 1
                reasons.append("Short MA > Long MA (bullish)")
            else:
                sell_signals += 1
                reasons.append("Short MA < Long MA (bearish)")

        # 2. RSI
        if latest_rsi:
            if latest_rsi < 30:
                buy_signals += 2  # Strong buy signal
                reasons.append(f"RSI oversold ({latest_rsi:.1f})")
            elif latest_rsi > 70:
                sell_signals += 2  # Strong sell signal
                reasons.append(f"RSI overbought ({latest_rsi:.1f})")
            elif latest_rsi < 50:
                buy_signals += 0.5
            else:
                sell_signals += 0.5

        # 3. MACD
        if latest_macd and latest_signal:
            if latest_macd > latest_signal:
                buy_signals += 1
                reasons.append("MACD bullish crossover")
            else:
                sell_signals += 1
                reasons.append("MACD bearish crossover")

        # 4. Bollinger Bands
        if latest_upper_bb and latest_lower_bb:
            if current_price < latest_lower_bb:
                buy_signals += 1.5
                reasons.append("Price below lower Bollinger Band")
            elif current_price > latest_upper_bb:
                sell_signals += 1.5
                reasons.append("Price above upper Bollinger Band")

        # Determine final signal
        total_signals = buy_signals + sell_signals
        if total_signals == 0:
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": "No clear signals",
                "indicators": {}
            }

        buy_strength = (buy_signals / total_signals) * 100
        sell_strength = (sell_signals / total_signals) * 100

        if buy_strength > 60:
            signal = "BUY"
            strength = buy_strength
        elif sell_strength > 60:
            signal = "SELL"
            strength = sell_strength
        else:
            signal = "HOLD"
            strength = 50

        return {
            "signal": signal,
            "strength": round(strength, 2),
            "reason": " | ".join(reasons),
            "indicators": {
                "current_price": current_price,
                "short_ma": latest_short_ma,
                "long_ma": latest_long_ma,
                "rsi": latest_rsi,
                "macd": latest_macd,
                "macd_signal": latest_signal,
                "upper_bb": latest_upper_bb,
                "lower_bb": latest_lower_bb
            },
            "buy_signals": buy_signals,
            "sell_signals": sell_signals
        }


# Singleton instance
technical_analysis = TechnicalAnalysisService()
