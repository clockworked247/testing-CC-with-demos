# 🔔 Notification System Setup Guide

Get automated alerts via **email** and **SMS** when trading opportunities arise!

## Overview

The notification system automatically monitors currency markets and sends you alerts when:
- **Strong buy/sell signals** are detected (based on your strength threshold)
- **Significant price changes** occur (exceeding your percentage threshold)
- **Portfolio changes** affect your holdings

Notifications run on a **scheduled basis** (hourly or daily) and respect your quiet hours.

---

## Quick Start

### 1. Email Notifications (Recommended First)

**Using Gmail (Easiest):**

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Create an App Password**
   - Visit https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → enter "Currency Trading App"
   - Click "Generate"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

3. **Add to `.env` file:**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # Your app password
   SMTP_FROM_EMAIL=your_email@gmail.com
   ```

4. **Restart the application** to load new settings

5. **Test it!**
   - Go to Notifications tab
   - Enter your email
   - Click "Test Email"
   - Check your inbox!

**Using Other Email Providers:**

**Outlook/Hotmail:**
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=your_email@outlook.com
```

**Yahoo Mail:**
```bash
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password  # Generate at Yahoo Account Security
SMTP_FROM_EMAIL=your_email@yahoo.com
```

**SendGrid (For Production Use):**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

---

### 2. SMS Notifications via Twilio

**Why Twilio?**
- Industry standard for SMS
- Free trial includes **$15 credit** (~500 SMS messages)
- Works globally
- Very reliable

**Setup Steps:**

1. **Create Twilio Account**
   - Visit https://www.twilio.com/try-twilio
   - Sign up (free trial, no credit card required initially)
   - Verify your phone number

2. **Get Your Credentials**
   - After signup, you'll see your Dashboard
   - Copy your **Account SID** (starts with `AC...`)
   - Copy your **Auth Token** (click to reveal)

3. **Get a Phone Number**
   - In Twilio Console, go to Phone Numbers → Get a Number
   - Choose a number (free on trial)
   - This is your "From" number

4. **Add to `.env` file:**
   ```bash
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your Account SID (starts with AC)
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_FROM_PHONE=+15551234567  # Your Twilio number
   ```

5. **Important - Trial Limitations:**
   - Free trial can only send to **verified phone numbers**
   - Verify your number at: https://www.twilio.com/console/phone-numbers/verified
   - Messages include "Sent from your Twilio trial account" prefix
   - Upgrade to remove limitations ($20 minimum)

6. **Test it!**
   - Go to Notifications tab
   - Enter your phone number (E.164 format: `+1234567890`)
   - Click "Test SMS"
   - Check your phone!

---

## Configuring Your Preferences

### Via Web Interface (Recommended)

1. Open the app: `http://localhost:8080`
2. Go to **Notifications** tab
3. Fill out the form:

**Contact Information:**
- Email address (for email notifications)
- Phone number (for SMS, E.164 format: `+1234567890`)

**Notification Methods:**
- ✅ Email Notifications
- ✅ SMS Notifications

**What to Notify About:**
- ✅ Buy Signals
- ✅ Sell Signals
- ✅ Significant Price Changes

**Thresholds:**
- **Minimum Signal Strength:** 70% (only notify for strong signals)
- **Price Change Threshold:** 2.0% (notify if price moves > 2%)

**Currency Pairs to Watch:**
- Leave empty to watch all major pairs
- Or specify: `EUR/USD,GBP/USD,USD/JPY`

**Schedule:**
- **Frequency:** Daily Summary (or Hourly Checks)
- **Quiet Hours:** 22:00 - 08:00 (no notifications during sleep)

4. Click **Save Preferences**

### Via API (For Automation)

```bash
curl -X POST "http://localhost:8000/api/notifications/preferences" \
  -d "email=your@email.com" \
  -d "phone_number=+1234567890" \
  -d "email_enabled=true" \
  -d "sms_enabled=true" \
  -d "notify_on_buy_signals=true" \
  -d "notify_on_sell_signals=true" \
  -d "min_signal_strength=70" \
  -d "watched_currencies=EUR/USD,GBP/USD"
```

---

## Notification Schedule

### Daily Notifications (Default)

Configure in `.env`:
```bash
NOTIFICATION_CHECK_INTERVAL=daily
NOTIFICATION_CHECK_TIME=09:00  # 9 AM check
```

The scheduler runs at 9 AM daily and:
1. Scans all major currency pairs (or your watched pairs)
2. Generates trading signals
3. Checks for significant price changes
4. Sends notifications if thresholds are met

### Hourly Notifications

For more frequent updates:
```bash
NOTIFICATION_CHECK_INTERVAL=hourly
```

Runs every hour on the hour.

### Manual Check

Trigger an immediate check anytime:
- Web UI: Notifications tab → "Trigger Manual Check"
- API: `POST /api/notifications/trigger-check`

---

## What Notifications Look Like

### Email Notification Example

**Subject:** 🔔 BUY Signal for EUR/USD - 85% Strength

**Body:**
```
Trading Signal Alert

EUR/USD
BUY
Signal Strength: 85.0%

Analysis Details

Technical Analysis
Signal: BUY
Reason: Short MA > Long MA (bullish) | RSI oversold (28.5)

Key Indicators:
- Current Price: 1.0842
- Short MA: 1.0856
- Long MA: 1.0821
- RSI: 28.5
- MACD: 0.0023

Sentiment Analysis
Euro has more news coverage (3 vs 1)

Disclaimer: This is an automated trading signal for informational
purposes only. Always do your own research before making trading decisions.

Generated at 2025-01-15 09:00:00 UTC
```

### SMS Notification Example

```
🔔 Trading Alert: BUY EUR/USD | Strength: 85% | Short MA > Long MA (bullish) | RSI oversold
```

---

## Troubleshooting

### Email Not Sending

**Gmail "Less secure app" error:**
- ✅ Solution: Use App Password (not regular password)
- See setup instructions above

**"Authentication failed" error:**
- ❌ Wrong username/password
- ✅ Double-check credentials in `.env`
- ✅ For Gmail, ensure App Password is correct (no spaces)

**Emails going to Spam:**
- Check spam folder
- Mark as "Not Spam"
- Add sender to contacts

**Connection timeout:**
- Check firewall settings
- Ensure port 587 is not blocked
- Try port 465 with SSL (update config)

### SMS Not Sending

**"Phone number not verified" (Twilio Trial):**
- ✅ Verify your number at https://www.twilio.com/console/phone-numbers/verified
- Or upgrade account ($20 minimum)

**Invalid phone number format:**
- ❌ Wrong: `1234567890`
- ❌ Wrong: `(123) 456-7890`
- ✅ Correct: `+1234567890` (E.164 format)

**Twilio authentication error:**
- Double-check Account SID and Auth Token
- Ensure no extra spaces in `.env`

**"From number not valid":**
- Verify TWILIO_FROM_PHONE is your Twilio number
- Include country code: `+1...` for US

### No Notifications Received

**Check scheduler is running:**
```bash
# In the backend logs, you should see:
"Starting notification scheduler..."
"Scheduled daily notifications at 09:00"
```

**Check notification preferences:**
- Go to Notifications tab
- Click "Load Preferences"
- Verify your settings are saved

**Check notification logs:**
- Notifications tab → "Load Logs"
- Look for sent notifications and any errors

**Manually trigger a check:**
- Notifications tab → "Trigger Manual Check"
- Check logs for results

**Verify you have trading signals:**
- Trading Signals tab → "Scan for Opportunities"
- If no opportunities found, adjust your thresholds

### Scheduler Not Starting

**Check configuration:**
```bash
# Valid values:
NOTIFICATION_CHECK_INTERVAL=daily  # or hourly
NOTIFICATION_CHECK_TIME=09:00      # HH:MM format
```

**Check logs for errors:**
```bash
# Look in terminal for:
"Scheduler started successfully"
# Or error messages
```

**Restart application:**
```bash
# Stop with Ctrl+C
# Restart
python backend/app.py
```

---

## Cost Considerations

### Email (Free)
- Gmail, Outlook, Yahoo: **Free** for personal use
- SendGrid Free Tier: **100 emails/day**
- Completely free for daily notifications

### SMS Costs

**Twilio Pricing (Pay-as-you-go):**
- US/Canada: **$0.0079 per SMS** (~$0.01)
- International: **$0.045 - $0.10 per SMS**
- Free Trial: **$15 credit** (1,500-1,900 messages)

**Daily Notifications Cost:**
- 1 SMS/day = ~$0.01/day = **$3.65/year**
- Very affordable for critical alerts!

**Hourly Notifications Cost:**
- 24 SMS/day = ~$0.24/day = **$87.60/year**
- Consider email for hourly checks

**Recommendation:**
- Use **email for daily summaries** (free)
- Use **SMS for critical high-strength signals only** (low cost)

---

## Best Practices

### 1. Start with Email Only
- Set up email first (it's free!)
- Test thoroughly before adding SMS
- SMS should be for critical alerts

### 2. Set Appropriate Thresholds
- **Too Low:** Notification fatigue, wasted SMS credits
- **Too High:** Miss opportunities
- **Recommended:** 70-75% signal strength

### 3. Choose Your Pairs Wisely
- Watching all pairs = more notifications
- Focus on 3-5 pairs you actively trade
- Example: `EUR/USD,GBP/USD,USD/JPY`

### 4. Use Quiet Hours
- Set quiet hours during sleep: `22:00 - 08:00`
- Markets are global, but you need rest!

### 5. Monitor Notification Logs
- Regularly check logs for delivery issues
- Adjust thresholds based on signal quality

### 6. Test Regularly
- Test email monthly to ensure it's working
- Test SMS quarterly (costs a few cents)

---

## Security Recommendations

### Protect Your Credentials

**`.env` File Security:**
- ✅ NEVER commit `.env` to git
- ✅ Use App Passwords (not real passwords)
- ✅ Rotate credentials every 90 days
- ❌ Never share your `.env` file

**Twilio Security:**
- ✅ Use Auth Tokens (not API keys for sensitive operations)
- ✅ Set up IP whitelisting in Twilio Console
- ✅ Monitor usage for unexpected spikes

### Email Security

**App Passwords:**
- Specific to this app
- Can be revoked without changing main password
- Recommended for all SMTP authentication

**2-Factor Authentication:**
- Required for Gmail App Passwords
- Highly recommended for all email accounts

---

## Advanced Configuration

### Custom SMTP Ports

For SSL instead of TLS:
```bash
SMTP_PORT=465  # SSL
# Update code to use smtplib.SMTP_SSL instead of SMTP
```

### Multiple Recipients

To notify multiple people:
1. Create separate notification preferences for each
2. Or use a distribution list in your email provider

### Webhook Integration

For advanced users, you can extend the notification service:

```python
# In services/notification_service.py
def send_webhook_notification(url, data):
    requests.post(url, json=data)
```

### Database Cleanup

Notification logs grow over time. Clean up old logs:

```sql
-- Delete logs older than 90 days
DELETE FROM notification_log
WHERE sent_at < DATE('now', '-90 days');
```

Or add to your cron:
```bash
# Clean up quarterly
0 0 1 */3 * sqlite3 data/trading.db "DELETE FROM notification_log WHERE sent_at < DATE('now', '-90 days');"
```

---

## API Reference

### Create/Update Preferences
```http
POST /api/notifications/preferences
?email=your@email.com
&phone_number=+1234567890
&email_enabled=true
&sms_enabled=false
&notify_on_buy_signals=true
&notify_on_sell_signals=true
&min_signal_strength=70
&watched_currencies=EUR/USD,GBP/USD
```

### Get Preferences
```http
GET /api/notifications/preferences
```

### Delete Preference
```http
DELETE /api/notifications/preferences/{id}
```

### Test Email
```http
POST /api/notifications/test-email?email=test@email.com
```

### Test SMS
```http
POST /api/notifications/test-sms?phone=+1234567890
```

### Trigger Manual Check
```http
POST /api/notifications/trigger-check
```

### Get Notification Logs
```http
GET /api/notifications/logs?limit=50
```

---

## FAQ

**Q: Can I get notifications without running the app 24/7?**
A: For scheduled notifications, yes, the app must be running. Consider deploying to a cloud server (AWS, Heroku, DigitalOcean) for 24/7 operation.

**Q: How do I stop receiving notifications?**
A: Go to Notifications tab → Load Preferences → Delete your preference. Or uncheck email/SMS enabled and save.

**Q: Can I get notifications for portfolio changes?**
A: Yes! Enable "Portfolio Changes" in your preferences. You'll be notified when positions hit certain P/L levels.

**Q: What if I want different thresholds for different pairs?**
A: Create multiple notification preferences with different watched currencies and thresholds.

**Q: Are notifications sent in real-time?**
A: Depends on your frequency setting. "Instant" sends when signals are generated. "Hourly" and "Daily" run on schedule.

**Q: Can I forward notifications to Slack/Discord/Telegram?**
A: Not directly, but you can set up email forwarding rules in your email provider to forward to these services.

---

## Support

Having issues? Check:
1. **Application Logs:** Look for errors in terminal
2. **Notification Logs:** Notifications tab → Load Logs
3. **Test Functions:** Use Test Email/SMS to isolate issues
4. **Configuration:** Verify `.env` settings are correct

Still stuck? The notification system is modular and well-commented - check the code in `backend/services/notification_service.py` and `backend/services/scheduler_service.py`.

---

**Happy Trading! 📈📧📱**

Remember: Notifications are tools to help you, not replace your judgment. Always verify signals before trading!
