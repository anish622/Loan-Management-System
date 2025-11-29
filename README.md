# Loan Management System

A comprehensive Flask-based web application for managing loans, calculating EMI (Equated Monthly Installments), tracking payments, and managing borrower-lender relationships. The system supports both borrower and admin user roles with secure authentication and SMS notifications.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Setup Instructions](#setup-instructions)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Usage Guide](#usage-guide)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

The Loan Management System is a full-stack web application designed to streamline loan processing operations. It enables:

- **Borrowers** to register, create loans, view loan details, and track payments
- **Admins** to manage all loans across the system and oversee borrower activities
- **Automated calculations** of EMI using the standard reducing-balance formula
- **Payment tracking** with detailed records and PDF generation
- **SMS notifications** via Twilio for loan creation and payment updates

---

## Features

✅ **User Authentication**
  - Secure registration and login for borrowers
  - Admin login with role-based access control
  - Password hashing using Werkzeug security

✅ **Loan Management**
  - Create loans with custom principal, interest rate, and tenure
  - Automatic EMI calculation
  - Real-time EMI preview with AJAX

✅ **Payment Tracking**
  - Record payments against loans
  - View payment history and outstanding balance
  - Download loan details as PDF

✅ **Admin Dashboard**
  - View all loans in the system
  - Monitor borrower details and payment status
  - Access borrower contact information

✅ **Notifications**
  - SMS notifications on loan creation (via Twilio)
  - Payment confirmation messages
  - Remaining balance updates

✅ **Responsive UI**
  - Single-page template design with dynamic content switching
  - CSS-styled forms and tables
  - User-friendly navigation

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 2.0+ |
| **Database** | MySQL 8.0+ |
| **Python Version** | 3.7+ |
| **ORM/Driver** | mysql-connector-python |
| **Authentication** | Werkzeug (password hashing) |
| **PDF Generation** | ReportLab |
| **SMS Service** | Twilio |
| **Frontend** | HTML5, CSS3, Jinja2 Templates |

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Flask Web Application (app.py)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Routes (Authentication, Loans, Payments)           │
│         ↓                                           │
│  Database Helpers & Utility Functions               │
│         ↓                                           │
│  MySQL Database (users, loans, payments)            │
│                                                     │
│  [SMS Integration via Twilio API]                   │
│  [PDF Generation via ReportLab]                     │
└─────────────────────────────────────────────────────┘
```

---

## Setup Instructions

### Prerequisites

- **Python 3.7+** installed on your system
- **MySQL Server 8.0+** running locally
- **pip** (Python package manager)
- **Twilio Account** (optional, for SMS notifications)

### Step 1: Clone or Navigate to the Project

```bash
cd c:\Users\ASUS\OneDrive\Desktop\Loan-Management-System
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database

1. **Start MySQL Server:**
   ```bash
   mysql -u root -p
   ```

2. **Create the Database:**
   ```sql
   CREATE DATABASE loan_management;
   ```

3. **Update Database Credentials in `app.py`:**

   Open `app.py` and update the `DB_CONFIG` dictionary:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "YOUR_MYSQL_PASSWORD",  # Replace with your MySQL root password
       "database": "loan_management"
   }
   ```

4. **Initialize Database Tables:**

   The tables are created automatically when the app starts (via `init_db()` function).

### Step 5: Configure Credentials

All sensitive credentials (database and Twilio) are stored in a `credentials.json` file:

1. **Copy the example file:**
   ```powershell
   Copy-Item credentials.example.json credentials.json
   ```

2. **Update `credentials.json` with your actual values:**
   ```json
   {
       "database": {
           "host": "localhost",
           "user": "root",
           "password": "YOUR_MYSQL_PASSWORD",
           "database": "loan_management"
       },
       "twilio": {
           "account_sid": "your_account_sid",
           "auth_token": "your_auth_token",
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

⚠️ **Important:** Never commit `credentials.json` to Git (it's in `.gitignore` to keep sensitive data secure).

For detailed Twilio setup instructions, refer to `TWILIO_SETUP.md`.

### Step 6: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(512) NOT NULL,
    role ENUM('admin','user') NOT NULL DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Unique user identifier
- `name`: User's full name
- `email`: Unique email address (used for login)
- `password_hash`: Hashed password (using Werkzeug)
- `role`: Either 'admin' (system administrator) or 'user' (borrower)
- `created_at`: Account creation timestamp

### Loans Table
```sql
CREATE TABLE loans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    borrower_id INT NOT NULL,
    principal DECIMAL(14,2) NOT NULL,
    annual_rate DECIMAL(5,3) NOT NULL,
    term_months INT NOT NULL,
    emi DECIMAL(14,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (borrower_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Columns:**
- `id`: Unique loan identifier
- `borrower_id`: Foreign key referencing the borrower (user)
- `principal`: Loan amount
- `annual_rate`: Annual interest rate (percentage)
- `term_months`: Loan tenure in months
- `emi`: Calculated monthly EMI amount
- `created_at`: Loan creation timestamp

### Payments Table
```sql
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
    amount DECIMAL(14,2) NOT NULL,
    payment_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
);
```

**Columns:**
- `id`: Unique payment record identifier
- `loan_id`: Foreign key referencing the associated loan
- `amount`: Payment amount
- `payment_date`: Date of the payment (YYYY-MM-DD format)
- `created_at`: Record creation timestamp

---

## API Endpoints

### Authentication Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register-borrower` | Register a new borrower account |
| GET/POST | `/user-login` | Borrower login |
| GET/POST | `/admin-login` | Admin login |
| GET | `/logout` | Clear session and logout |

### Loan Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/create-loan` | Create a new loan |
| GET | `/loan/<loan_id>` | View loan details and payment history |
| GET | `/loan/<loan_id>/download` | Download loan details as PDF |
| GET | `/user_loans` | View all loans for logged-in borrower |
| GET | `/admin-dashboard` | Admin view of all system loans |

### Payment Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payment-entry` | Record a payment against a loan |

### AJAX Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calculate-emi` | Calculate EMI (returns JSON) |

---

## Configuration

All configuration is centralized in `credentials.json`, which is ignored by Git.

### credentials.json Structure

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

### Setup Instructions

1. **Copy the example file:**
   ```powershell
   Copy-Item credentials.example.json credentials.json
   ```

2. **Edit `credentials.json` and fill in your values:**
   - Database credentials (host, user, password, database name)
   - Twilio credentials (account SID, auth token, phone number)
   - Flask secret key (generate using `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Debug mode and SMS notifications settings

### Environment Variables (Legacy - No longer needed)

The app now loads all configuration from `credentials.json`. Environment variables are no longer required.

### Twilio Configuration

For SMS notifications, ensure you have a Twilio account and fill in:
- `twilio.account_sid`: Your Twilio Account SID from Console
- `twilio.auth_token`: Your Twilio Auth Token from Console
- `twilio.phone_number`: Your Twilio phone number (e.g., +1234567890)
- `app.sms_notifications_enabled`: Set to `true` to enable SMS, `false` to test without SMS

Refer to `TWILIO_SETUP.md` for detailed instructions.

---

## How It Works

### 1. **User Registration & Authentication**

- **Borrowers** can register with name, email, and password
- Passwords are hashed using `werkzeug.security.generate_password_hash()`
- Users login with email and password (verified using `check_password_hash()`)
- Sessions are managed using Flask's session object

### 2. **Loan Creation**

- Logged-in borrowers navigate to "Create Loan"
- Enter loan parameters:
  - **Principal**: Loan amount
  - **Annual Rate**: Interest rate (%)
  - **Term (Months)**: Loan tenure
  - **Phone Number** (optional): For SMS notifications

### 3. **EMI Calculation**

The application uses the **Reducing Balance Formula**:

$$\text{EMI} = \frac{P \times r \times (1+r)^n}{(1+r)^n - 1}$$

Where:
- **P** = Principal amount
- **r** = Monthly interest rate (annual_rate / 12 / 100)
- **n** = Number of months (term_months)

**Special Case:** If interest rate is 0%, EMI = Principal / Term

Example:
```
Principal: $10,000
Annual Rate: 12%
Term: 12 months

Monthly Rate (r) = 12 / 12 / 100 = 0.01
EMI = 10000 * 0.01 * (1.01)^12 / ((1.01)^12 - 1)
EMI ≈ $888.49
```

### 4. **Payment Recording**

- Users can record payments by entering:
  - **Loan ID**: Which loan to apply payment to
  - **Amount**: Payment amount
  - **Payment Date**: Date of payment
  - **Phone Number** (optional): For SMS confirmation

- System calculates remaining balance:
  ```
  Remaining = (EMI × Term) - Total Paid
  ```

### 5. **Admin Dashboard**

- Admins can view all loans and borrowers
- Monitor payment status across the system
- Access borrower contact details

### 6. **PDF Report Generation**

- Users can download loan details as PDF
- PDF includes:
  - Loan summary (principal, rate, term, EMI)
  - Complete payment history
  - Generated using ReportLab

### 7. **SMS Notifications** (Optional)

- Triggered on loan creation
- Triggered on payment recording
- Sends borrower name, loan details, and balance information
- Requires valid Twilio credentials

---

## Usage Guide

### For Borrowers

**Step 1: Register**
1. Click "Register as Borrower"
2. Enter name, email, and password
3. Submit registration

**Step 2: Login**
1. Click "Borrower Login"
2. Enter email and password
3. Click login

**Step 3: Create a Loan**
1. Click "Create Loan"
2. Enter principal, annual rate, and term
3. (Optional) Enter phone number for SMS notification
4. Click "Create Loan" button
5. System calculates and displays EMI

**Step 4: View Loans**
1. Click "My Loans" to see all your loans
2. Click on a loan to view details

**Step 5: Record Payment**
1. Navigate to the loan
2. Scroll to "Record Payment" section
3. Enter amount, payment date, and (optional) phone number
4. Click "Record Payment"
5. See updated remaining balance

**Step 6: Download Loan Details**
1. Go to loan view
2. Click "Download as PDF" button
3. PDF with loan summary and payment history is generated

### For Admins

**Step 1: Admin Login**
1. Click "Admin Login"
2. Enter admin credentials

**Step 2: View Dashboard**
1. Click "Admin Dashboard"
2. See all loans in the system
3. View borrower names and email addresses

**Step 3: Manage Loans**
1. Click on any loan to view its details
2. Add payments or download reports as needed

---

## Security Considerations

⚠️ **IMPORTANT: Before deploying to production:**

1. **Credentials Management**
   - Use `credentials.json` to store all sensitive information
   - Never commit `credentials.json` to Git (it's in `.gitignore`)
   - Copy `credentials.example.json` to `credentials.json` and fill in your values
   - Restrict file permissions: `chmod 600 credentials.json` on Linux/Mac

2. **Change Secret Key**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Update `flask.secret_key` in `credentials.json` with the generated value

3. **Update Database Credentials**
   - Never use hardcoded passwords
   - Create a dedicated MySQL user (not root)
   - Use strong, unique passwords
   - Store credentials only in `credentials.json`

4. **Set Debug Mode to False**
   ```json
   "flask": {
       "debug": false
   }
   ```

5. **Use HTTPS in Production**
   - Deploy on HTTPS only
   - Protect all API endpoints with authentication

6. **Input Validation**
   - All inputs are validated before database insertion
   - SQL injection prevented using parameterized queries

7. **Password Hashing**
   - Passwords are never stored in plain text
   - Uses Werkzeug's strong hashing algorithms

8. **Environment-Specific Configuration**
   - Use different `credentials.json` for dev/staging/production
   - Keep production credentials secure and backed up

---

## Troubleshooting

### Database Connection Error

**Error:** `mysql.connector.errors.ProgrammingError`

**Solution:**
1. Ensure MySQL server is running
2. Verify credentials in `DB_CONFIG`
3. Check if database `loan_management` exists
4. Test connection: `mysql -u root -p loan_management`

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Twilio SMS Not Working

**Error:** SMS not received on phone

**Solutions:**
1. Verify Twilio credentials in `twilio_config.py`
2. Check if phone number format is correct (with country code, e.g., +1...)
3. Ensure Twilio account has sufficient credits
4. Check Twilio logs for error messages

### Session Issues (Not Staying Logged In)

**Solution:**
- Clear browser cookies and cache
- Restart the Flask application
- Ensure browser allows cookies

---

## Project Structure

```
Loan-Management-System/
├── app.py                      # Main Flask application
├── config.py                   # Legacy config file (replaced by credentials.json)
├── twilio_config.py            # Twilio SMS configuration and functions
├── requirements.txt            # Python dependencies
├── schema.sql                  # Database schema (optional reference)
├── reset_admin.py              # Script to reset admin user
├── credentials.json            # ⚠️ Sensitive credentials (NOT in Git, use .gitignore)
├── credentials.example.json    # Template for credentials (safe to commit)
├── static/
│   └── css/
│       └── styles.css          # CSS styling
├── templates/
│   └── index.html              # Single template file (dynamic pages)
├── README.md                   # This file
├── LICENSE                     # Project license
├── TWILIO_SETUP.md             # Twilio integration guide
└── .gitignore                  # Git ignore file (includes credentials.json)
```

---

## License

See `LICENSE` file for details.

---

## Support & Contact

For issues, questions, or contributions, please refer to the documentation or contact the project maintainer.

**Last Updated:** November 2025