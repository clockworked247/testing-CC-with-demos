"""
Portfolio management service for tracking currency holdings.
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging

from database import Portfolio
from services.currency_service import currency_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for managing currency portfolio"""

    def add_position(
        self,
        db: Session,
        currency: str,
        amount: float,
        purchase_price_usd: float,
        notes: Optional[str] = None
    ) -> Portfolio:
        """
        Add a new currency position to the portfolio.

        Args:
            db: Database session
            currency: Currency code
            amount: Amount of currency
            purchase_price_usd: Purchase price in USD
            notes: Optional notes

        Returns:
            Created portfolio entry
        """
        position = Portfolio(
            currency=currency.upper(),
            amount=amount,
            purchase_price_usd=purchase_price_usd,
            purchase_date=datetime.utcnow(),
            notes=notes
        )

        db.add(position)
        db.commit()
        db.refresh(position)

        logger.info(f"Added position: {amount} {currency} @ ${purchase_price_usd}")
        return position

    def get_all_positions(self, db: Session) -> List[Portfolio]:
        """
        Get all portfolio positions.

        Args:
            db: Database session

        Returns:
            List of portfolio positions
        """
        return db.query(Portfolio).all()

    def get_positions_by_currency(self, db: Session, currency: str) -> List[Portfolio]:
        """
        Get all positions for a specific currency.

        Args:
            db: Database session
            currency: Currency code

        Returns:
            List of positions for that currency
        """
        return db.query(Portfolio).filter(
            Portfolio.currency == currency.upper()
        ).all()

    def delete_position(self, db: Session, position_id: int) -> bool:
        """
        Delete a portfolio position.

        Args:
            db: Database session
            position_id: Position ID

        Returns:
            True if deleted, False otherwise
        """
        position = db.query(Portfolio).filter(Portfolio.id == position_id).first()
        if position:
            db.delete(position)
            db.commit()
            logger.info(f"Deleted position: {position_id}")
            return True
        return False

    def calculate_portfolio_value(self, db: Session) -> Dict:
        """
        Calculate total portfolio value and P&L.

        Args:
            db: Database session

        Returns:
            Dictionary with portfolio metrics
        """
        positions = self.get_all_positions(db)

        if not positions:
            return {
                "total_value_usd": 0.0,
                "total_invested_usd": 0.0,
                "total_pnl_usd": 0.0,
                "total_pnl_percent": 0.0,
                "positions": []
            }

        total_value = 0.0
        total_invested = 0.0
        position_details = []

        for position in positions:
            # Get current exchange rate
            current_rate = currency_service.get_rate_for_pair(position.currency, "USD")

            if current_rate:
                current_value_usd = position.amount * current_rate
                invested_value = position.amount * position.purchase_price_usd
                pnl = current_value_usd - invested_value
                pnl_percent = (pnl / invested_value * 100) if invested_value > 0 else 0

                total_value += current_value_usd
                total_invested += invested_value

                position_details.append({
                    "id": position.id,
                    "currency": position.currency,
                    "amount": position.amount,
                    "purchase_price": position.purchase_price_usd,
                    "current_price": current_rate,
                    "current_value_usd": current_value_usd,
                    "invested_value_usd": invested_value,
                    "pnl_usd": pnl,
                    "pnl_percent": pnl_percent,
                    "purchase_date": position.purchase_date.isoformat(),
                    "notes": position.notes
                })
            else:
                logger.warning(f"Could not get rate for {position.currency}/USD")

        total_pnl = total_value - total_invested
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0

        return {
            "total_value_usd": round(total_value, 2),
            "total_invested_usd": round(total_invested, 2),
            "total_pnl_usd": round(total_pnl, 2),
            "total_pnl_percent": round(total_pnl_percent, 2),
            "positions": position_details
        }

    def get_currency_allocation(self, db: Session) -> Dict:
        """
        Get portfolio allocation by currency.

        Args:
            db: Database session

        Returns:
            Dictionary with allocation percentages
        """
        portfolio_value = self.calculate_portfolio_value(db)
        total_value = portfolio_value["total_value_usd"]

        if total_value == 0:
            return {}

        allocation = {}
        for position in portfolio_value["positions"]:
            currency = position["currency"]
            value = position["current_value_usd"]
            percentage = (value / total_value * 100) if total_value > 0 else 0

            if currency in allocation:
                allocation[currency]["value_usd"] += value
                allocation[currency]["percentage"] += percentage
            else:
                allocation[currency] = {
                    "value_usd": value,
                    "percentage": percentage
                }

        return allocation

    def get_position_history(self, db: Session, currency: Optional[str] = None) -> List[Dict]:
        """
        Get historical positions (all or for specific currency).

        Args:
            db: Database session
            currency: Optional currency filter

        Returns:
            List of position history
        """
        query = db.query(Portfolio)

        if currency:
            query = query.filter(Portfolio.currency == currency.upper())

        positions = query.order_by(Portfolio.purchase_date.desc()).all()

        return [{
            "id": pos.id,
            "currency": pos.currency,
            "amount": pos.amount,
            "purchase_price_usd": pos.purchase_price_usd,
            "purchase_date": pos.purchase_date.isoformat(),
            "notes": pos.notes
        } for pos in positions]


# Singleton instance
portfolio_service = PortfolioService()
