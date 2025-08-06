# SMS Alert Setup Guide

## Overview
Your expense tracking app now includes SMS alert functionality that will notify you when you reach a certain percentage of your spending limits.

## Current Implementation
- **Demo Mode**: Currently prints SMS messages to the console for testing
- **Production Ready**: Includes Twilio integration code (commented out)

## How It Works
1. Set spending limits with phone numbers and alert thresholds
2. When you add transactions, the app checks if you've reached your threshold
3. If threshold is reached, an SMS alert is sent to your phone
4. Alerts are sent only once per threshold per month to avoid spam

## Setting Up Real SMS (Twilio)

### Step 1: Get Twilio Account
1. Sign up at [twilio.com](https://www.twilio.com)
2. Get your Account SID and Auth Token from the dashboard
3. Get a Twilio phone number for sending SMS

### Step 2: Install Twilio
```bash
pip install twilio
```

### Step 3: Configure the App
1. Uncomment the Twilio code in `app.py` (lines 35-45 in the `send_sms_alert` function)
2. Replace the placeholder values:
   - `your_account_sid` → Your Twilio Account SID
   - `your_auth_token` → Your Twilio Auth Token
   - `your_twilio_number` → Your Twilio phone number

### Step 4: Test
1. Set a limit with your phone number
2. Add transactions to reach the threshold
3. You should receive an SMS alert

## Phone Number Format
- Use international format: `+1234567890`
- Include country code
- No spaces or special characters

## Alert Message Format
```
🚨 SPENDING ALERT 🚨

Category: Food
Current Spending: $180.00
Limit: $200.00
Threshold: 80%

You've reached 80% of your Food spending limit!
```

## Testing
- Use the "Test SMS Alert" button on the limits page
- Check the console for demo messages
- Monitor the `sent_alerts.json` file to see alert history

## Troubleshooting
- **No alerts**: Check if phone number is entered correctly
- **Multiple alerts**: The system prevents duplicate alerts per month
- **Twilio errors**: Verify your credentials and phone number format

## Security Notes
- Never commit your Twilio credentials to version control
- Use environment variables for production
- Consider rate limiting for SMS alerts 