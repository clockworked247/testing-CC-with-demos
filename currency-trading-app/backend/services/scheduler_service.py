"""
Scheduler service for automated notifications and alerts.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, time
from sqlalchemy.orm import Session
import logging

from config import config
from database import SessionLocal, NotificationPreference, NotificationLog
from services.signals_service import signals_service
from services.historical_service import historical_service
from services.notification_service import notification_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Scheduler for automated trading notifications"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.started = False

    def start(self):
        """Start the scheduler"""
        if self.started:
            logger.warning("Scheduler already started")
            return

        logger.info("Starting notification scheduler...")

        # Schedule based on configuration
        interval = config.NOTIFICATION_CHECK_INTERVAL.lower()

        if interval == "hourly":
            # Run every hour
            self.scheduler.add_job(
                self.check_and_notify,
                IntervalTrigger(hours=1),
                id="hourly_notifications",
                name="Hourly Trading Notifications"
            )
            logger.info("Scheduled hourly notifications")

        elif interval == "daily":
            # Run once per day at specified time
            check_time = config.NOTIFICATION_CHECK_TIME.split(':')
            hour = int(check_time[0])
            minute = int(check_time[1]) if len(check_time) > 1 else 0

            self.scheduler.add_job(
                self.check_and_notify,
                CronTrigger(hour=hour, minute=minute),
                id="daily_notifications",
                name="Daily Trading Notifications"
            )
            logger.info(f"Scheduled daily notifications at {hour:02d}:{minute:02d}")

        else:
            logger.warning(f"Invalid notification interval: {interval}. Using daily.")
            self.scheduler.add_job(
                self.check_and_notify,
                CronTrigger(hour=9, minute=0),
                id="daily_notifications",
                name="Daily Trading Notifications"
            )

        self.scheduler.start()
        self.started = True
        logger.info("Scheduler started successfully")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.started = False
            logger.info("Scheduler stopped")

    def is_quiet_hours(self, pref: NotificationPreference) -> bool:
        """
        Check if current time is within user's quiet hours.

        Args:
            pref: Notification preference

        Returns:
            True if in quiet hours, False otherwise
        """
        if not pref.quiet_hours_start or not pref.quiet_hours_end:
            return False

        try:
            now = datetime.now().time()
            start = datetime.strptime(pref.quiet_hours_start, "%H:%M").time()
            end = datetime.strptime(pref.quiet_hours_end, "%H:%M").time()

            if start < end:
                return start <= now <= end
            else:
                # Quiet hours cross midnight
                return now >= start or now <= end

        except ValueError:
            logger.error(f"Invalid quiet hours format for pref {pref.id}")
            return False

    def check_and_notify(self):
        """
        Main function to check for trading opportunities and send notifications.
        This is called by the scheduler at configured intervals.
        """
        logger.info("Running scheduled notification check...")

        db = SessionLocal()
        try:
            # Get all active notification preferences
            preferences = db.query(NotificationPreference).filter(
                (NotificationPreference.email_enabled == True) |
                (NotificationPreference.sms_enabled == True)
            ).all()

            if not preferences:
                logger.info("No notification preferences configured")
                return

            logger.info(f"Found {len(preferences)} active notification preferences")

            for pref in preferences:
                try:
                    # Skip if in quiet hours
                    if self.is_quiet_hours(pref):
                        logger.info(f"Skipping {pref.email or pref.phone_number} - quiet hours")
                        continue

                    # Process notifications for this user
                    self.process_user_notifications(db, pref)

                except Exception as e:
                    logger.error(f"Error processing notifications for pref {pref.id}: {e}")
                    continue

            logger.info("Scheduled notification check complete")

        except Exception as e:
            logger.error(f"Error in scheduled notification check: {e}")

        finally:
            db.close()

    def process_user_notifications(self, db: Session, pref: NotificationPreference):
        """
        Process notifications for a single user.

        Args:
            db: Database session
            pref: User's notification preferences
        """
        logger.info(f"Processing notifications for {pref.email or pref.phone_number}")

        notifications_sent = 0

        # Determine which currency pairs to check
        if pref.watched_currencies:
            pairs_to_check = [p.strip() for p in pref.watched_currencies.split(',')]
        else:
            # Use major pairs by default
            pairs_to_check = config.MAJOR_CURRENCY_PAIRS

        # Check for trading signals
        if pref.notify_on_buy_signals or pref.notify_on_sell_signals:
            notifications_sent += self.check_trading_signals(db, pref, pairs_to_check)

        # Check for price changes
        if pref.notify_on_price_changes:
            notifications_sent += self.check_price_changes(db, pref, pairs_to_check)

        logger.info(f"Sent {notifications_sent} notifications to {pref.email or pref.phone_number}")

    def check_trading_signals(
        self,
        db: Session,
        pref: NotificationPreference,
        pairs: list
    ) -> int:
        """
        Check for trading signals and send notifications.

        Args:
            db: Database session
            pref: User preferences
            pairs: Currency pairs to check

        Returns:
            Number of notifications sent
        """
        notifications_sent = 0

        for pair in pairs:
            try:
                # Parse pair (e.g., "EUR/USD" -> "EUR", "USD")
                parts = pair.split('/')
                if len(parts) != 2:
                    continue

                base, quote = parts[0].strip(), parts[1].strip()

                # Generate signal
                signal = signals_service.generate_signal(db, base, quote, use_llm=False)

                # Check if signal meets criteria
                if signal['strength'] < pref.min_signal_strength:
                    continue

                # Check if user wants this type of signal
                if signal['signal'] == 'BUY' and not pref.notify_on_buy_signals:
                    continue
                if signal['signal'] == 'SELL' and not pref.notify_on_sell_signals:
                    continue
                if signal['signal'] == 'HOLD':
                    continue  # Don't notify on HOLD signals

                # Send notification
                success = False
                error_msg = None

                if pref.email_enabled and pref.email:
                    success, error_msg = notification_service.send_trading_signal_email(
                        pref.email,
                        signal
                    )
                    self.log_notification(
                        db, pref.id, "signal", "email", pref.email,
                        f"{signal['signal']} signal for {pair}", signal, success, error_msg
                    )
                    if success:
                        notifications_sent += 1

                if pref.sms_enabled and pref.phone_number:
                    success, error_msg = notification_service.send_trading_signal_sms(
                        pref.phone_number,
                        signal
                    )
                    self.log_notification(
                        db, pref.id, "signal", "sms", pref.phone_number,
                        f"{signal['signal']} signal for {pair}", signal, success, error_msg
                    )
                    if success:
                        notifications_sent += 1

            except Exception as e:
                logger.error(f"Error checking signal for {pair}: {e}")
                continue

        return notifications_sent

    def check_price_changes(
        self,
        db: Session,
        pref: NotificationPreference,
        pairs: list
    ) -> int:
        """
        Check for significant price changes and send notifications.

        Args:
            db: Database session
            pref: User preferences
            pairs: Currency pairs to check

        Returns:
            Number of notifications sent
        """
        notifications_sent = 0

        for pair in pairs:
            try:
                # Parse pair
                parts = pair.split('/')
                if len(parts) != 2:
                    continue

                base, quote = parts[0].strip(), parts[1].strip()

                # Get 24-hour price change
                change_data = historical_service.calculate_price_change(db, base, quote, 24)

                if not change_data:
                    continue

                change_percent = abs(change_data['change_percent'])

                # Check if change exceeds threshold
                if change_percent < pref.price_change_threshold:
                    continue

                # Send notification
                email = pref.email if pref.email_enabled else None
                phone = pref.phone_number if pref.sms_enabled else None

                results = notification_service.send_price_change_notification(
                    email,
                    phone,
                    pair,
                    change_data['change_percent'],
                    change_data['current_rate']
                )

                # Log each notification
                for i, (success, error_msg) in enumerate(results):
                    method = "email" if i == 0 and email else "sms"
                    recipient = email if method == "email" else phone

                    self.log_notification(
                        db, pref.id, "price_change", method, recipient,
                        f"Price change for {pair}", change_data, success, error_msg
                    )

                    if success:
                        notifications_sent += 1

            except Exception as e:
                logger.error(f"Error checking price change for {pair}: {e}")
                continue

        return notifications_sent

    def log_notification(
        self,
        db: Session,
        pref_id: int,
        notification_type: str,
        method: str,
        recipient: str,
        subject: str,
        data: dict,
        success: bool,
        error_msg: str = None
    ):
        """
        Log a sent notification to the database.

        Args:
            db: Database session
            pref_id: Notification preference ID
            notification_type: Type of notification
            method: email or sms
            recipient: Recipient address
            subject: Notification subject/summary
            data: Notification data
            success: Whether sending succeeded
            error_msg: Error message if failed
        """
        try:
            log_entry = NotificationLog(
                preference_id=pref_id,
                notification_type=notification_type,
                method=method,
                recipient=recipient,
                subject=subject,
                message=str(data),
                success=success,
                error_message=error_msg
            )

            db.add(log_entry)
            db.commit()

        except Exception as e:
            logger.error(f"Error logging notification: {e}")
            db.rollback()

    def trigger_manual_check(self):
        """Trigger a manual notification check (for testing or on-demand)"""
        logger.info("Triggering manual notification check...")
        self.check_and_notify()


# Singleton instance
scheduler = NotificationScheduler()
