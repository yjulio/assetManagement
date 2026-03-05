#!/usr/bin/env python3
"""Test if password verification works"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from werkzeug.security import check_password_hash
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'user_asset',
    'password': 'AssetM@nage2024',
    'database': 'db_asset'
}

def test_password(username, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
            
        pw_hash = user['password_hash']
        print(f"Testing password: '{password}'")
        print(f"Hash: {pw_hash[:60]}...")
        
        if check_password_hash(pw_hash, password):
            print(f"✅ Password MATCHES!")
            return True
        else:
            print(f"❌ Password DOES NOT MATCH")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    print("Testing: username='admin', password='Admin@2025'")
    test_password('admin', 'Admin@2025')
