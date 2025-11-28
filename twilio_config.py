"""
twilio_config.py

Twilio SMS notification configuration and helper functions.
Set your Twilio credentials as environment variables or hardcode them below.

Environment variables:
- TWILIO_ACCOUNT_SID: Your Twilio Account SID
- TWILIO_AUTH_TOKEN: Your Twilio Auth Token
- TWILIO_PHONE_NUMBER: Your Twilio phone number (e.g., +1234567890)
"""

import os
from twilio.rest import Client

# Twilio credentials - Set these in environment variables for production
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Flag to enable/disable SMS notifications (useful for testing)
SMS_NOTIFICATIONS_ENABLED = os.getenv("SMS_NOTIFICATIONS_ENABLED", "True").lower() == "true"


def send_loan_notification(phone_number, borrower_name, principal, annual_rate, term_months, emi):
    """
    Send an SMS notification when a loan is created.
    
    Args:
        phone_number (str): Recipient's phone number (e.g., +1234567890)
        borrower_name (str): Name of the borrower
        principal (float): Loan principal amount
        annual_rate (float): Annual interest rate (percentage)
        term_months (int): Loan term in months
        emi (float): Calculated EMI amount
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not SMS_NOTIFICATIONS_ENABLED:
        return True, "SMS notifications disabled (test mode)"
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return False, "Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_text = f"""
Hello {borrower_name},

Your loan has been successfully created!

Loan Details:
- Principal: ₹{principal:,.2f}
- Interest Rate: {annual_rate}% per annum
- Loan Term: {term_months} months
- Monthly EMI: ₹{emi:,.2f}

Thank you for using our Loan Management System.
        """.strip()
        
        message = client.messages.create(
            body=message_text,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        return True, f"SMS sent successfully (SID: {message.sid})"
    
    except Exception as e:
        return False, f"Failed to send SMS: {str(e)}"


def send_payment_notification(phone_number, borrower_name, loan_id, amount, remaining_balance):
    """
    Send an SMS notification when a payment is made.
    
    Args:
        phone_number (str): Recipient's phone number
        borrower_name (str): Name of the borrower
        loan_id (int): Loan ID
        amount (float): Payment amount
        remaining_balance (float): Remaining balance after payment
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not SMS_NOTIFICATIONS_ENABLED:
        return True, "SMS notifications disabled (test mode)"
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return False, "Twilio credentials not configured."
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_text = f"""
Hello {borrower_name},

Your payment has been recorded successfully!

Payment Details:
- Loan ID: {loan_id}
- Amount Paid: ₹{amount:,.2f}
- Remaining Balance: ₹{remaining_balance:,.2f}

Thank you!
        """.strip()
        
        message = client.messages.create(
            body=message_text,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        return True, f"SMS sent successfully (SID: {message.sid})"
    
    except Exception as e:
        return False, f"Failed to send SMS: {str(e)}"
