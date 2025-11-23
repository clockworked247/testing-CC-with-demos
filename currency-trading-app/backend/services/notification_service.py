"""
Notification service for sending email and SMS alerts.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import config
from database import NotificationLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending email and SMS notifications"""

    def __init__(self):
        self.smtp_configured = bool(config.SMTP_USERNAME and config.SMTP_PASSWORD)
        self.twilio_configured = bool(config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN)

        if self.twilio_configured:
            self.twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        else:
            self.twilio_client = None

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Send an email notification.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML

        Returns:
            Tuple of (success, error_message)
        """
        if not self.smtp_configured:
            logger.warning("SMTP not configured. Cannot send email.")
            return False, "SMTP not configured"

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = config.SMTP_FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                server.starttls()
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True, None

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send an SMS notification via Twilio.

        Args:
            to_phone: Recipient phone number (E.164 format: +1234567890)
            message: SMS message text

        Returns:
            Tuple of (success, error_message)
        """
        if not self.twilio_configured:
            logger.warning("Twilio not configured. Cannot send SMS.")
            return False, "Twilio not configured"

        if not to_phone.startswith('+'):
            logger.warning(f"Phone number {to_phone} should be in E.164 format (+1234567890)")

        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=config.TWILIO_FROM_PHONE,
                to=to_phone
            )

            logger.info(f"SMS sent successfully to {to_phone}. SID: {message_obj.sid}")
            return True, None

        except TwilioRestException as e:
            error_msg = f"Twilio error: {e.msg}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Failed to send SMS: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def send_trading_signal_email(
        self,
        to_email: str,
        signal_data: dict
    ) -> tuple[bool, Optional[str]]:
        """
        Send a formatted trading signal notification email.

        Args:
            to_email: Recipient email
            signal_data: Signal dictionary with currency_pair, signal, strength, etc.

        Returns:
            Tuple of (success, error_message)
        """
        currency_pair = signal_data.get('currency_pair', 'Unknown')
        signal = signal_data.get('signal', 'HOLD')
        strength = signal_data.get('strength', 0)

        subject = f"🔔 {signal} Signal for {currency_pair} - {strength:.0f}% Strength"

        # Create HTML body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Trading Signal Alert</h2>

                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">{currency_pair}</h3>
                        <p style="font-size: 24px; margin: 10px 0;">
                            <strong style="color: {'#10b981' if signal == 'BUY' else '#ef4444' if signal == 'SELL' else '#f59e0b'};">
                                {signal}
                            </strong>
                        </p>
                        <p>Signal Strength: <strong>{strength:.1f}%</strong></p>
                    </div>

                    <h4>Analysis Details</h4>
        """

        # Add technical analysis
        if 'technical_analysis' in signal_data:
            tech = signal_data['technical_analysis']
            html_body += f"""
                    <div style="background: #fff; padding: 15px; border-left: 4px solid #2563eb; margin: 10px 0;">
                        <h5 style="margin-top: 0;">Technical Analysis</h5>
                        <p><strong>Signal:</strong> {tech.get('signal', 'N/A')}</p>
                        <p><strong>Reason:</strong> {tech.get('reason', 'N/A')}</p>
            """

            if 'indicators' in tech:
                indicators = tech['indicators']
                html_body += "<p><strong>Key Indicators:</strong></p><ul>"
                for key, value in indicators.items():
                    if value is not None:
                        html_body += f"<li>{key}: {value if isinstance(value, str) else f'{value:.4f}'}</li>"
                html_body += "</ul>"

            html_body += "</div>"

        # Add sentiment analysis
        if 'sentiment_analysis' in signal_data:
            sent = signal_data['sentiment_analysis']
            html_body += f"""
                    <div style="background: #fff; padding: 15px; border-left: 4px solid #10b981; margin: 10px 0;">
                        <h5 style="margin-top: 0;">Sentiment Analysis</h5>
                        <p>{sent.get('summary', 'No sentiment data available')}</p>
                    </div>
            """

        html_body += f"""
                    <p style="margin-top: 30px; font-size: 12px; color: #64748b;">
                        <strong>Disclaimer:</strong> This is an automated trading signal for informational purposes only.
                        Always do your own research before making trading decisions.
                    </p>

                    <p style="font-size: 12px; color: #64748b;">
                        Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_email(to_email, subject, html_body, html=True)

    def send_trading_signal_sms(
        self,
        to_phone: str,
        signal_data: dict
    ) -> tuple[bool, Optional[str]]:
        """
        Send a concise trading signal via SMS.

        Args:
            to_phone: Recipient phone number
            signal_data: Signal dictionary

        Returns:
            Tuple of (success, error_message)
        """
        currency_pair = signal_data.get('currency_pair', 'Unknown')
        signal = signal_data.get('signal', 'HOLD')
        strength = signal_data.get('strength', 0)

        message = f"🔔 Trading Alert: {signal} {currency_pair} | Strength: {strength:.0f}%"

        if 'technical_analysis' in signal_data:
            reason = signal_data['technical_analysis'].get('reason', '')
            if reason:
                # Truncate reason for SMS (max 160 chars total)
                message += f" | {reason[:80]}"

        return self.send_sms(to_phone, message)

    def send_price_change_notification(
        self,
        recipient_email: Optional[str],
        recipient_phone: Optional[str],
        currency_pair: str,
        change_percent: float,
        current_rate: float
    ) -> List[tuple[bool, Optional[str]]]:
        """
        Send price change notification via enabled methods.

        Args:
            recipient_email: Email (if email notifications enabled)
            recipient_phone: Phone (if SMS notifications enabled)
            currency_pair: Currency pair
            change_percent: Percentage change
            current_rate: Current exchange rate

        Returns:
            List of (success, error) tuples for each notification sent
        """
        results = []

        direction = "increased" if change_percent > 0 else "decreased"
        emoji = "📈" if change_percent > 0 else "📉"

        # Email notification
        if recipient_email:
            subject = f"{emoji} {currency_pair} {direction} by {abs(change_percent):.2f}%"

            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Price Change Alert</h2>

                        <div style="background: #f8fafc; padding: 20px; border-radius: 8px;">
                            <h3>{currency_pair}</h3>
                            <p style="font-size: 20px;">
                                Current Rate: <strong>{current_rate:.6f}</strong>
                            </p>
                            <p style="font-size: 18px; color: {'#10b981' if change_percent > 0 else '#ef4444'};">
                                Change: <strong>{change_percent:+.2f}%</strong>
                            </p>
                        </div>

                        <p style="margin-top: 20px; font-size: 12px; color: #64748b;">
                            This price change exceeded your threshold. Consider reviewing your positions.
                        </p>
                    </div>
                </body>
            </html>
            """

            results.append(self.send_email(recipient_email, subject, html_body, html=True))

        # SMS notification
        if recipient_phone:
            message = f"{emoji} {currency_pair} {direction} by {abs(change_percent):.2f}% | Rate: {current_rate:.6f}"
            results.append(self.send_sms(recipient_phone, message))

        return results

    def test_email_configuration(self, test_email: str) -> tuple[bool, Optional[str]]:
        """
        Test email configuration by sending a test email.

        Args:
            test_email: Email to send test to

        Returns:
            Tuple of (success, error_message)
        """
        subject = "Currency Trading Platform - Test Email"
        body = """
        <html>
            <body>
                <h2>Email Configuration Test</h2>
                <p>If you're reading this, your email notifications are configured correctly!</p>
                <p>You'll receive trading signals and alerts at this email address.</p>
            </body>
        </html>
        """

        return self.send_email(test_email, subject, body, html=True)

    def test_sms_configuration(self, test_phone: str) -> tuple[bool, Optional[str]]:
        """
        Test SMS configuration by sending a test message.

        Args:
            test_phone: Phone number to send test to

        Returns:
            Tuple of (success, error_message)
        """
        message = "Currency Trading Platform: SMS notifications configured successfully!"
        return self.send_sms(test_phone, message)


# Singleton instance
notification_service = NotificationService()
