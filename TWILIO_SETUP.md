# Twilio SMS Notification System Setup Guide

## Overview
This Loan Management System now includes SMS notifications via Twilio. When users create loans or make payments, they receive SMS confirmations.

## Installation

### 1. Install Twilio Package
```powershell
pip install -r requirements.txt
```
Or manually:
```powershell
pip install twilio
```

### 2. Get Twilio Credentials

1. **Sign up for Twilio** (free trial available):
   - Go to https://www.twilio.com/try-twilio
   - Create a free account
   - Verify your email and phone number

2. **Get your credentials**:
   - After login, go to your Twilio Console: https://console.twilio.com
   - Find your **Account SID** and **Auth Token** on the main dashboard
   - Generate or find your **Phone Number** in the Phone Numbers section (e.g., +1234567890)

### 3. Set Environment Variables

Set these environment variables on your system:

**Windows PowerShell:**
```powershell
$env:TWILIO_ACCOUNT_SID = "your_account_sid"
$env:TWILIO_AUTH_TOKEN = "your_auth_token"
$env:TWILIO_PHONE_NUMBER = "+1234567890"
$env:SMS_NOTIFICATIONS_ENABLED = "True"
```

**Windows Command Prompt:**
```cmd
set TWILIO_ACCOUNT_SID=your_account_sid
set TWILIO_AUTH_TOKEN=your_auth_token
set TWILIO_PHONE_NUMBER=+1234567890
set SMS_NOTIFICATIONS_ENABLED=True
```

**Linux/Mac:**
```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="+1234567890"
export SMS_NOTIFICATIONS_ENABLED="True"
```

### 4. (Optional) Disable SMS for Testing

To test the system without sending actual SMS messages, set:

**PowerShell:**
```powershell
$env:SMS_NOTIFICATIONS_ENABLED = "False"
```

This will simulate SMS sending without making API calls to Twilio.

## Usage

### Creating a Loan with SMS Notification

1. **Login** as a user
2. **Go to "Create Loan"** page
3. **Fill in the form**:
   - Principal amount
   - Annual interest rate
   - Loan term (months)
   - **Phone Number** (for SMS notification) - This is optional but recommended
4. **Submit** - An SMS will be sent with loan details

### Recording a Payment with SMS Notification

1. **View a loan** you've created
2. **Enter payment details**:
   - Payment amount
   - Payment date
   - **Phone Number** (for SMS confirmation) - Optional
3. **Submit** - An SMS will be sent confirming the payment and remaining balance

## SMS Notification Examples

### Loan Creation SMS
```
Hello John Doe,

Your loan has been successfully created!

Loan Details:
- Principal: ₹50,000.00
- Interest Rate: 10.5% per annum
- Loan Term: 24 months
- Monthly EMI: ₹2,182.50

Thank you for using our Loan Management System.
```

### Payment Recording SMS
```
Hello John Doe,

Your payment has been recorded successfully!

Payment Details:
- Loan ID: 5
- Amount Paid: ₹5,000.00
- Remaining Balance: ₹45,000.00

Thank you!
```

## Files Modified/Added

- **`requirements.txt`** - Added `twilio` package
- **`twilio_config.py`** - New file with Twilio configuration and helper functions
- **`app.py`** - Modified to:
  - Import Twilio functions
  - Add phone_number field to loan creation form
  - Send SMS on loan creation
  - Send SMS on payment recording

## Troubleshooting

### "Twilio credentials not configured" error
- Make sure all three environment variables are set: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- Restart your Flask app after setting environment variables
- Verify variables are set correctly in your environment

### SMS not being sent
- Check if `SMS_NOTIFICATIONS_ENABLED` is set to "True" (case-sensitive)
- Verify phone numbers are in international format (e.g., +1234567890, not (123)456-7890)
- Check your Twilio account balance (free trial includes credits)
- Look at Flask debug logs for detailed error messages

### Invalid phone number error
- Phone numbers must include country code (e.g., +1 for USA, +91 for India)
- Ensure format is: +[country code][number] with no spaces or dashes

## Security Notes

⚠️ **Important**: Never hardcode credentials in the source code!
- Always use environment variables
- Never commit `.env` files to version control
- For production, use a `.env` file with a package like `python-dotenv` (not included by default to keep it simple)

## Testing Without Twilio

To test the application without Twilio setup:

```powershell
$env:SMS_NOTIFICATIONS_ENABLED = "False"
```

This allows you to test the entire flow without actually sending SMS messages. The app will log "SMS notifications disabled (test mode)" instead.

## Next Steps

1. Sign up for Twilio (free trial)
2. Get your credentials
3. Set environment variables
4. Restart the Flask app
5. Test by creating a loan with a phone number

For more information, visit: https://www.twilio.com/docs/sms
