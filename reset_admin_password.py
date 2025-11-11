#!/usr/bin/env python3
"""
Quick admin password reset - sets a specific password
Usage: python3 reset_admin_password.py <new_password>
Or run without arguments for interactive mode
"""

import os
import sys

# Set required environment variables if not set
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'temp-secret-key-for-admin-change'
if 'DB_PASSWORD' not in os.environ:
    os.environ['DB_PASSWORD'] = 'change-this-password'

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from AssetManagement import InventorySystem
from werkzeug.security import generate_password_hash

def reset_password(username='admin', new_password=None):
    """Reset admin password"""
    
    if new_password is None:
        if len(sys.argv) > 1:
            new_password = sys.argv[1]
        else:
            print("ERROR: No password provided")
            print()
            print("Usage:")
            print("  python3 reset_admin_password.py <new_password>")
            print()
            print("Example:")
            print("  python3 reset_admin_password.py MyNewPassword@2025")
            print()
            print("For interactive password change with validation, use:")
            print("  python3 change_admin_password.py")
            sys.exit(1)
    
    try:
        system = InventorySystem()
        
        # Check if user exists
        if username not in system.users:
            print(f"ERROR: User '{username}' does not exist!")
            sys.exit(1)
        
        # Generate password hash
        pw_hash = generate_password_hash(new_password)
        
        # Update password in database
        system.cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (pw_hash, username)
        )
        system.conn.commit()
        
        print("✅ SUCCESS!")
        print(f"Password for user '{username}' has been updated.")
        print()
        print("New login credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {new_password}")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    reset_password()
