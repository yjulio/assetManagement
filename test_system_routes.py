#!/usr/bin/env python3
"""
Complete System Configuration & Route Test
Tests all major routes and navigation for proper wiring
"""

import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Critical routes to test
CRITICAL_ROUTES = {
    'Public': [
        ('Landing Page', '/landing'),
        ('Login Page', '/login'),
    ],
    'Dashboard': [
        ('Main Dashboard', '/'),
        ('Manage Dashboard', '/manage-dashboard'),
    ],
    'Assets': [
        ('Asset List', '/assets'),
        ('Add Asset', '/add'),
        ('Update Quantity', '/update'),
        ('Checkout', '/checkout'),
        ('Checkin', '/checkin'),
       ('Maintenance', '/maintenance'),
        ('Dispose', '/dispose'),
    ],
    'Setup': [
        ('Users', '/users'),
        ('Groups', '/groups'),
        ('Suppliers', '/suppliers'),
        ('Company Info', '/company-info'),
        ('Locations', '/locations'),
    ],
    'Tools': [
        ('Data Quality', '/data-quality'),
        ('Import', '/import'),
    ],
    'Database': [
        ('Database Management', '/database'),
        ('Backup & Restore', '/backup-restore'),
    ],
}

def login():
    """Login to system"""
    try:
        resp = session.get(f"{BASE_URL}/login")
        soup = BeautifulSoup(resp.text, 'html.parser')
        csrf = soup.find('input', {'name': 'csrf_token'})
        
        data = {
            'username': 'admin',
            'password': 'Admin@2024',
            'group': 'Admin',
            'csrf_token': csrf['value'] if csrf else ''
        }
        
        resp = session.post(f"{BASE_URL}/login", data=data, allow_redirects=True)
        return 'logout' in resp.text.lower()
    except:
        return False

def test_route(name, path):
    """Test if route is accessible"""
    try:
        resp = session.get(f"{BASE_URL}{path}", allow_redirects=True, timeout=5)
        
        if resp.status_code == 200:
            return '✅', 'OK'
        elif resp.status_code == 302:
            return '🔄', 'Redirect'
        elif resp.status_code == 404:
            return '❌', '404 Not Found'
        elif resp.status_code == 403:
            return '🔒', '403 Forbidden'
        elif resp.status_code == 500:
            return '💥', '500 Server Error'
        else:
            return '⚠️', f'{resp.status_code}'
    except requests.Timeout:
        return '⏱️', 'Timeout'
    except Exception as e:
        return '❌', f'Error: {str(e)[:30]}'

def main():
    print("="*80)
    print("COMPLETE SYSTEM CONFIGURATION TEST")
    print("="*80)
    
    # Test server
    print("\n🔧 Testing Server Connection...")
    try:
        resp = session.get(BASE_URL, timeout=5)
        print(f"   ✅ Server responding (Status: {resp.status_code})")
    except:
        print(f"   ❌ Server not accessible at {BASE_URL}")
        print("   💡 Start server: cd /home/assetManagement && source venv/bin/activate && cd src && python3 app.py")
        return False
    
    # Login
    print("\n🔐 Logging in...")
    if login():
        print("   ✅ Successfully logged in as admin")
    else:
        print("   ⚠️ Login failed - testing public routes only")
    
    # Test all routes
    print("\n📍 Testing Routes...")
    print("="*80)
    
    total = 0
    passed = 0
    
    for category, routes in CRITICAL_ROUTES.items():
        print(f"\n📂 {category}")
        print("-" * 80)
        
        for name, path in routes:
            status, message = test_route(name, path)
            print(f"   {status} {name:30} {path:35} {message}")
            total += 1
            if status == '✅' or status == '🔄':
                passed += 1
    
    # Summary
    print("\n" + "="*80)
    print(f"📊 TEST SUMMARY")
    print("="*80)
    print(f"   Total Routes Tested: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total*100):.1f}%")
    print("="*80)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
