#!/usr/bin/env python3
"""
Create admin user for Asset Management System
Username: admin
Password: Admin@2025
"""

import os
import sys

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from AssetManagement import InventorySystem
from werkzeug.security import generate_password_hash

def create_admin():
    """Create admin user with predefined credentials"""
    username = 'admin'
    email = 'minomoya626@gmail.com'
    password = 'Admin@2025'  # Strong default password
    
    print("Creating admin user...")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print("-" * 50)
    
    try:
        system = InventorySystem()
        
        # Create Admin group if not exists
        try:
            system.add_group('Admin', 'Administrator group with full access')
            print("✓ Admin group created")
        except Exception as e:
            print(f"Admin group may already exist: {e}")
        
        # Generate password hash
        pw_hash = generate_password_hash(password)
        
        # Check if user exists
        if username in system.users:
            print(f"User '{username}' already exists. Updating password...")
            # Update password
            system.cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (pw_hash, username)
            )
            system.conn.commit()
            print("✓ Password updated")
        else:
            # Add new user
            system.add_user(username, email, pw_hash)
            print("✓ Admin user created")
        
        # Assign to Admin group
        try:
            system.assign_user_to_group(username, 'Admin')
            print("✓ User assigned to Admin group")
        except Exception as e:
            print(f"Group assignment may already exist: {e}")
        
        print("-" * 50)
        print("SUCCESS! Admin user is ready.")
        print("\nLogin credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print("\nPlease change the password after first login!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_admin()
