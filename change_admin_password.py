#!/usr/bin/env python3
"""
Change admin password for Asset Management System
Usage: python3 change_admin_password.py
"""

import os
import sys
import getpass
import re

# Set required environment variables if not set
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'temp-secret-key-for-admin-change'
if 'DB_PASSWORD' not in os.environ:
    os.environ['DB_PASSWORD'] = 'change-this-password'

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from AssetManagement import InventorySystem
from werkzeug.security import generate_password_hash

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

def change_admin_password():
    """Change admin password"""
    print("=" * 60)
    print("ADMIN PASSWORD CHANGE UTILITY")
    print("=" * 60)
    print()
    
    # Get username (default to admin)
    username = input("Enter username (default: admin): ").strip()
    if not username:
        username = 'admin'
    
    try:
        system = InventorySystem()
        
        # Check if user exists
        if username not in system.users:
            print(f"\n❌ ERROR: User '{username}' does not exist!")
            print("\nAvailable users:")
            for user in system.users:
                print(f"  - {user}")
            sys.exit(1)
        
        print(f"\n✓ User '{username}' found")
        print()
        
        # Get new password
        while True:
            password = getpass.getpass("Enter new password: ")
            password_confirm = getpass.getpass("Confirm new password: ")
            
            if password != password_confirm:
                print("❌ Passwords do not match. Please try again.\n")
                continue
            
            # Validate password strength
            is_valid, message = validate_password(password)
            if not is_valid:
                print(f"❌ {message}")
                print("Please try again.\n")
                continue
            
            print(f"✓ {message}")
            break
        
        # Generate password hash
        pw_hash = generate_password_hash(password)
        
        # Update password in database
        system.cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (pw_hash, username)
        )
        system.conn.commit()
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Password changed successfully.")
        print("=" * 60)
        print()
        print("New login credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password)}")
        print()
        print("⚠️  Please save your password securely!")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        change_admin_password()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
