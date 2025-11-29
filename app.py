# app.py
"""
Loan Management App (Flask + MySQL)
- Single-template (templates/index.html) that renders different "pages" using a 'page' variable.
- Routes use kebab-case: /user-login, /admin-login, /register-borrower, /create-loan, /calculate-emi, /payment-entry
- Uses mysql-connector-python (pip package: mysql-connector-python)
- Passwords stored using werkzeug.security.generate_password_hash / check_password_hash
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import math
import json
import os
from twilio_config import send_loan_notification, send_payment_notification

# PDF generation
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Load credentials from credentials.json
def load_credentials():
    """Load credentials from credentials.json file"""
    cred_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"credentials.json not found at {cred_path}\n"
            "Please copy credentials.example.json to credentials.json and fill in your credentials."
        )
    with open(cred_path, 'r') as f:
        return json.load(f)

CREDENTIALS = load_credentials()

app = Flask(__name__)
app.secret_key = CREDENTIALS['flask']['secret_key']
app.config['DEBUG'] = CREDENTIALS['flask']['debug']

DB_CONFIG = CREDENTIALS['database']

# --------- Database helpers ----------
def get_db_connection():
    """
    Returns a live connection to the MySQL database.
    We use mysql.connector which follows the Python DB-API. 
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def init_db():
    """
    Create tables if they don't exist. Run once (or call at app start).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Users: stores both admins and borrowers (role column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(512) NOT NULL,
        role ENUM('admin','user') NOT NULL DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Loans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        borrower_id INT NOT NULL,
        principal DECIMAL(14,2) NOT NULL,
        annual_rate DECIMAL(5,3) NOT NULL,
        term_months INT NOT NULL,
        emi DECIMAL(14,2) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (borrower_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    # Payments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        loan_id INT NOT NULL,
        amount DECIMAL(14,2) NOT NULL,
        payment_date DATE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize DB on startup (safe: creates only if missing)
init_db()

# --------- Utility functions ----------
def calculate_emi(principal, annual_rate_percent, term_months):
    """
    EMI formula (reducing-balance):
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where r = monthly_rate (annual_rate_percent / 12 / 100)
    Source: standard EMI formula used widely. See references in docs.
    """
    P = float(principal)
    r = float(annual_rate_percent) / 12.0 / 100.0
    n = int(term_months)
    if r == 0:
        # zero-interest loan: straightforward division
        return round(P / n, 2)
    numerator = P * r * (1 + r) ** n
    denominator = (1 + r) ** n - 1
    emi = numerator / denominator
    return round(emi, 2)

def current_user():
    """
    Returns logged-in user record dict or None.
    """
    if 'user_id' not in session:
        return None
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, role FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# --------- Routes (kebab-case URLs) ----------
@app.route("/")
def home():
    """
    Renders the single index.html template with page='home'.
    The template will display navigation and forms depending on 'page' value.
    """
    user = current_user()
    return render_template("index.html", page="home", user=user)

# Registration for borrowers
@app.route("/register-borrower", methods=["GET", "POST"])
def register_borrower():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not (name and email and password):
            flash("All fields required.", "danger")
            return redirect(url_for("register_borrower"))
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'user')",
                (name, email, password_hash)
            )
            conn.commit()
            flash("Registration successful. You may login now.", "success")
        except mysql.connector.IntegrityError:
            flash("Email already registered.", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("home"))
    # GET: show registration form within index.html (page=register)
    return render_template("index.html", page="register")

# User login (borrower)
@app.route("/user-login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'user'", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash("Login successful.", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials.", "danger")
        return redirect(url_for("user_login"))
    return render_template("index.html", page="user-login")

# Admin login
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    # same as user login but role=admin
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin and check_password_hash(admin['password_hash'], password):
            session['user_id'] = admin['id']
            session['role'] = admin['role']
            flash("Admin login successful.", "success")
            return redirect(url_for("home"))
        flash("Invalid admin credentials.", "danger")
        return redirect(url_for("admin_login"))
    return render_template("index.html", page="admin-login")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

# Create Loan (only logged-in users or admins can create loans; borrowers create loans for themselves)
@app.route("/create-loan", methods=["GET", "POST"])
def create_loan():
    user = current_user()
    if not user:
        flash("Please log in to create a loan.", "warning")
        return redirect(url_for("user_login"))
    if request.method == "POST":
        principal = request.form.get("principal")
        annual_rate = request.form.get("annual_rate")
        term_months = request.form.get("term_months")
        phone_number = request.form.get("phone_number", "")  # Optional: get phone for SMS
        
        try:
            emi_value = calculate_emi(principal, annual_rate, term_months)
        except Exception as e:
            flash(f"Error calculating EMI: {e}", "danger")
            return redirect(url_for("create_loan"))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loans (borrower_id, principal, annual_rate, term_months, emi)
            VALUES (%s, %s, %s, %s, %s)
        """, (user['id'], principal, annual_rate, term_months, emi_value))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Send SMS notification if phone number is provided
        if phone_number and phone_number.strip():
            success, message = send_loan_notification(
                phone_number=phone_number,
                borrower_name=user['name'],
                principal=float(principal),
                annual_rate=float(annual_rate),
                term_months=int(term_months),
                emi=emi_value
            )
            if success:
                flash(f"Loan created. EMI = {emi_value}. {message}", "success")
            else:
                flash(f"Loan created. EMI = {emi_value}. (Note: {message})", "warning")
        else:
            flash(f"Loan created. EMI = {emi_value}", "success")
        
        return redirect(url_for("home"))
    return render_template("index.html", page="create-loan", user=user)

# Loan detail + payment list + payment form
@app.route("/loan/<int:loan_id>")
def loan_view(loan_id):
    user = current_user()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # fetch loan
    cursor.execute("SELECT l.*, u.name as borrower_name FROM loans l JOIN users u ON l.borrower_id = u.id WHERE l.id = %s", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        cursor.close()
        conn.close()
        flash("Loan not found.", "danger")
        return redirect(url_for("home"))
    # fetch payments
    cursor.execute("SELECT * FROM payments WHERE loan_id = %s ORDER BY payment_date DESC", (loan_id,))
    payments = cursor.fetchall()
    # compute totals
    total_paid = sum([float(p['amount']) for p in payments]) if payments else 0.0
    total_payable = float(loan['emi']) * int(loan['term_months'])
    remaining = round(total_payable - total_paid, 2)
    cursor.close()
    conn.close()
    return render_template("index.html", page="loan-view", loan=loan, payments=payments, total_paid=round(total_paid,2), remaining=remaining, user=user)


@app.route("/loan/<int:loan_id>/download")
def loan_download(loan_id):
    """Generate and return a PDF containing loan details and payments."""
    user = current_user()
    if not user:
        flash("Please log in to download loan details.", "warning")
        return redirect(url_for("user_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT l.*, u.name as borrower_name FROM loans l JOIN users u ON l.borrower_id = u.id WHERE l.id = %s", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        cursor.close()
        conn.close()
        flash("Loan not found.", "danger")
        return redirect(url_for("home"))

    # Authorization: allow owner or admin
    if (loan['borrower_id'] != user['id']) and (user['role'] != 'admin'):
        cursor.close()
        conn.close()
        flash("You are not authorized to download this loan.", "danger")
        return redirect(url_for("home"))

    cursor.execute("SELECT * FROM payments WHERE loan_id = %s ORDER BY payment_date DESC", (loan_id,))
    payments = cursor.fetchall()

    # Build PDF
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    margin_x = 50
    y = page_height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin_x, y, f"Loan Details - #{loan['id']}")
    y -= 30

    c.setFont("Helvetica", 11)
    lines = [
        f"Borrower: {loan.get('borrower_name')}",
        f"Principal: {loan.get('principal')}",
        f"Annual Rate (%): {loan.get('annual_rate')}",
        f"Term (months): {loan.get('term_months')}",
        f"EMI: {loan.get('emi')}",
        f"Created at: {loan.get('created_at')}",
    ]

    for line in lines:
        c.drawString(margin_x, y, line)
        y -= 18

    y -= 6
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin_x, y, "Payments:")
    y -= 20
    c.setFont("Helvetica", 10)

    if payments:
        # Header
        c.drawString(margin_x, y, "Date")
        c.drawString(margin_x + 120, y, "Amount")
        c.drawString(margin_x + 220, y, "Recorded At")
        y -= 14
        c.line(margin_x, y, page_width - margin_x, y)
        y -= 10
        for p in payments:
            # page break
            if y < 80:
                c.showPage()
                y = page_height - 50
                c.setFont("Helvetica", 10)
            payment_date = p.get('payment_date')
            amount = p.get('amount')
            created_at = p.get('created_at')
            c.drawString(margin_x, y, str(payment_date))
            c.drawString(margin_x + 120, y, f"{amount}")
            c.drawString(margin_x + 220, y, str(created_at))
            y -= 14
    else:
        c.drawString(margin_x, y, "No payments recorded.")

    c.showPage()
    c.save()

    buffer.seek(0)
    cursor.close()
    conn.close()

    return send_file(buffer, as_attachment=True, download_name=f"loan_{loan_id}.pdf", mimetype="application/pdf")

# Payment entry (POST)
@app.route("/payment-entry", methods=["POST"])
def payment_entry():
    user = current_user()
    if not user:
        flash("Please login to enter payments.", "warning")
        return redirect(url_for("user_login"))
    loan_id = request.form.get("loan_id")
    amount = request.form.get("amount")
    payment_date = request.form.get("payment_date")  # expected YYYY-MM-DD
    phone_number = request.form.get("phone_number", "")  # Optional: for SMS notification
    
    if not (loan_id and amount and payment_date):
        flash("All payment fields are required.", "danger")
        return redirect(url_for("home"))
    # Optional: check loan belongs to user or user is admin
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loans WHERE id = %s", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        cursor.close()
        conn.close()
        flash("Loan not found.", "danger")
        return redirect(url_for("home"))
    if (loan['borrower_id'] != user['id']) and (user['role'] != 'admin'):
        cursor.close()
        conn.close()
        flash("You are not authorized to add payment for this loan.", "danger")
        return redirect(url_for("home"))
    # Insert payment
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (loan_id, amount, payment_date) VALUES (%s, %s, %s)", (loan_id, amount, payment_date))
    conn.commit()
    cursor.close()
    
    # Calculate remaining balance for SMS notification
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payments WHERE loan_id = %s", (loan_id,))
    payments = cursor.fetchall()
    total_paid = sum([float(p['amount']) for p in payments]) if payments else 0.0
    total_payable = float(loan['emi']) * int(loan['term_months'])
    remaining = round(total_payable - total_paid, 2)
    cursor.close()
    
    # Send SMS notification if phone number is provided
    if phone_number and phone_number.strip():
        success, message = send_payment_notification(
            phone_number=phone_number,
            borrower_name=user['name'],
            loan_id=int(loan_id),
            amount=float(amount),
            remaining_balance=remaining
        )
        if success:
            flash(f"Payment recorded. {message}", "success")
        else:
            flash(f"Payment recorded. (Note: {message})", "warning")
    else:
        flash("Payment recorded.", "success")
    
    conn.close()
    return redirect(url_for("loan_view", loan_id=loan_id))

# AJAX endpoint to calculate EMI (returns JSON)
@app.route("/calculate-emi", methods=["POST"])
def ajax_calculate_emi():
    principal = request.form.get("principal")
    annual_rate = request.form.get("annual_rate")
    term_months = request.form.get("term_months")
    try:
        emi_value = calculate_emi(principal, annual_rate, term_months)
        return jsonify({"emi": emi_value})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Admin dashboard (simple)
@app.route("/admin-dashboard")
def admin_dashboard():
    user = current_user()
    if not user or user['role'] != 'admin':
        flash("Admin access required.", "danger")
        return redirect(url_for("admin_login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT l.*, u.name as borrower_name, u.email FROM loans l JOIN users u ON l.borrower_id = u.id ORDER BY l.created_at DESC")
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", page="admin-dashboard", loans=loans, user=user)

@app.route("/user_loans")
def user_loans():
    user = current_user()
    if not user:
        flash("Please log in to view your loans.", "warning")
        return redirect(url_for("user_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, principal, annual_rate, term_months, emi, created_at
        FROM loans
        WHERE borrower_id = %s
        ORDER BY created_at DESC
    """, (user['id'],))
    loans = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", page="user_loans", loans=loans, user=user)


if __name__ == "__main__":
    # Run in debug mode for development; set debug=False in production
    app.run(debug=True)
