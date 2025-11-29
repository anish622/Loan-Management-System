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

### 3. Configure Credentials

The system uses a `credentials.json` file to store sensitive information instead of environment variables.

**Step 1: Create credentials.json**

Copy the example file:
```powershell
Copy-Item credentials.example.json credentials.json
```

Or manually create `credentials.json` in the root directory of the project.

**Step 2: Edit credentials.json**

Open `credentials.json` and fill in your Twilio credentials:

```json
{
    "database": {
        "host": "localhost",
        "user": "root",
        "password": "your_mysql_password",
        "database": "loan_management"
    },
    "twilio": {
        "account_sid": "your_account_sid_here",
        "auth_token": "your_auth_token_here",
        "phone_number": "+1234567890"
    },
    "flask": {
        "secret_key": "your_secure_secret_key",
        "debug": true
    },
    "app": {
        "sms_notifications_enabled": true
    }
}
```

Replace the placeholder values with your actual credentials:
- `account_sid`: Found in your Twilio Console
- `auth_token`: Found in your Twilio Console
- `phone_number`: Your Twilio phone number (e.g., +1234567890)

### 4. (Optional) Disable SMS for Testing

To test the system without sending actual SMS messages, set `sms_notifications_enabled` to `false` in `credentials.json`:

```json
{
    "app": {
        "sms_notifications_enabled": false
    }
}
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

- **`credentials.json`** (NEW) - Your actual credentials (ignored by Git)
- **`credentials.example.json`** (NEW) - Template for credentials
- **`.gitignore`** - Updated to ignore `credentials.json`
- **`app.py`** - Modified to load credentials from `credentials.json`
- **`twilio_config.py`** - Updated to load Twilio credentials from `credentials.json`

## Credentials File Structure

### credentials.json

The `credentials.json` file contains all sensitive configuration for the application:

```json
{
    "database": {
        "host": "localhost",      // MySQL server hostname
        "user": "root",           // MySQL username
        "password": "password",   // MySQL password
        "database": "loan_management"  // Database name
    },
    "twilio": {
        "account_sid": "ACxxxxxx",           // Your Twilio Account SID
        "auth_token": "auth_token_here",     // Your Twilio Auth Token
        "phone_number": "+1234567890"        // Your Twilio phone number
    },
    "flask": {
        "secret_key": "secure_random_string", // Secret key for session management
        "debug": false                        // Enable/disable debug mode
    },
    "app": {
        "sms_notifications_enabled": true    // Enable/disable SMS notifications
    }
}
```

## Security

✅ **Best Practices Implemented:**
- Credentials are stored in `credentials.json` (not in version control)
- `credentials.json` is listed in `.gitignore` to prevent accidental commits
- `credentials.example.json` provides a template without sensitive data
- All sensitive data is loaded from the JSON file at runtime

⚠️ **Important Security Notes:**
- **NEVER commit `credentials.json` to Git** (it's in .gitignore)
- Keep `credentials.json` secure on your production server
- Use strong, unique values for `secret_key` in production
- Restrict file permissions: `chmod 600 credentials.json` on Linux/Mac

## Troubleshooting

### "credentials.json not found" error
- Ensure `credentials.json` exists in the project root directory
- Copy from `credentials.example.json` if it doesn't exist:
  ```powershell
  Copy-Item credentials.example.json credentials.json
  ```
- Fill in all required values in the JSON file

### "Twilio credentials not configured" error
- Check that all Twilio fields are filled in `credentials.json`:
  - `twilio.account_sid`
  - `twilio.auth_token`
  - `twilio.phone_number`
- Restart your Flask app after updating credentials
- Verify credentials are correct in Twilio Console

### SMS not being sent
- Check if `sms_notifications_enabled` is set to `true` in `credentials.json`
- Verify phone numbers are in international format (e.g., +1234567890, not (123)456-7890)
- Check your Twilio account balance (free trial includes credits)
- Look at Flask debug logs for detailed error messages

### Invalid phone number error
- Phone numbers must include country code (e.g., +1 for USA, +91 for India)
- Ensure format is: +[country code][number] with no spaces or dashes
- Test your phone number in Twilio Console first

### Database connection error
- Verify MySQL credentials in `credentials.json`:
  - `database.host`
  - `database.user`
  - `database.password`
  - `database.database`
- Ensure MySQL server is running
- Test connection manually:
  ```bash
  mysql -h localhost -u root -p
  ```

## Testing Without Twilio

To test the application without Twilio setup:

1. Set `sms_notifications_enabled` to `false` in `credentials.json`
2. Restart the Flask app
3. Create loans and make payments - SMS calls will be simulated

## Production Deployment

Before deploying to production:

1. **Generate a secure secret key:**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Update `flask.secret_key` in `credentials.json`

2. **Set `debug` to `false`:**
   ```json
   "flask": {
       "debug": false
   }
   ```

3. **Use secure database credentials:**
   - Create a dedicated MySQL user (not root)
   - Use a strong password
   - Restrict database access

4. **Secure the credentials.json file:**
   ```bash
   chmod 600 credentials.json
   ```

5. **Environment-specific configuration:**
   - Use different `credentials.json` for dev/staging/production
   - Keep production credentials secure and backed up

## Next Steps

1. Sign up for Twilio (free trial)
2. Get your credentials
3. Copy `credentials.example.json` to `credentials.json`
4. Fill in your credentials in `credentials.json`
5. Restart the Flask app
6. Test by creating a loan with a phone number

For more information, visit: https://www.twilio.com/docs/sms
