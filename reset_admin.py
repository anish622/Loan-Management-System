#!/usr/bin/env python3
"""
reset_admin.py

Utility to update or create an admin user in the project's MySQL database.

Usage:
  python reset_admin.py            # interactive prompts
  python reset_admin.py --email admin@example.com --password secret123

This script imports DB_CONFIG from app.py (so it uses the same DB settings).
It will prompt for confirmation before making changes.
"""
import argparse
import sys
from getpass import getpass

try:
    from app import DB_CONFIG
except Exception as e:
    print(f"Failed to import DB_CONFIG from app.py: {e}")
    sys.exit(2)

import mysql.connector
from werkzeug.security import generate_password_hash


def prompt_confirm(msg: str) -> bool:
    ans = input(msg + " [y/N]: ").strip().lower()
    return ans == 'y' or ans == 'yes'


def main():
    parser = argparse.ArgumentParser(description="Reset or create admin user password")
    parser.add_argument("--email", help="email for the admin account (will update/create)")
    parser.add_argument("--password", help="new admin password (if omitted, prompted securely)")
    args = parser.parse_args()

    email = args.email or input("Admin email to update/create [admin@example.com]: ").strip() or "admin@example.com"
    if args.password:
        password = args.password
    else:
        password = getpass("Enter new admin password: ")
        password2 = getpass("Confirm new admin password: ")
        if password != password2:
            print("Passwords do not match. Aborting.")
            sys.exit(1)

    print(f"This will set the password for admin account with email: {email}")
    if not prompt_confirm("Proceed?"):
        print("Aborted by user.")
        sys.exit(0)

    # Hash password
    password_hash = generate_password_hash(password)

    # Connect and update/insert
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Failed to connect to MySQL using DB_CONFIG: {e}")
        sys.exit(3)

    cursor = conn.cursor(dictionary=True)
    try:
        # Try find any admin user
        cursor.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
        admin = cursor.fetchone()
        if admin:
            # Update admin
            cursor.execute(
                "UPDATE users SET password_hash = %s, email = %s WHERE id = %s",
                (password_hash, email, admin['id'])
            )
            conn.commit()
            print(f"Updated password for existing admin (id={admin['id']}, previous email={admin.get('email')}).")
        else:
            # Create a new admin
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'admin')",
                ("Administrator", email, password_hash)
            )
            conn.commit()
            print(f"Created new admin account with email={email}.")
    except mysql.connector.Error as exc:
        print(f"MySQL error while updating/creating admin: {exc}")
        sys.exit(4)
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
