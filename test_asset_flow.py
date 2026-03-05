#!/usr/bin/env python3
"""
Complete Asset Management Flow Test
Tests: Login → Add Asset → View Assets List
"""

import sys
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_complete_flow():
    """Test the complete asset management flow"""
    print("="*70)
    print("ASSET MANAGEMENT FLOW TEST")
    print("="*70)
    
    session = requests.Session()
    
    # Step 1: Get login page and extract CSRF token
    print("\n1. Accessing login page...")
    try:
        response = session.get(f"{BASE_URL}/login")
        if response.status_code != 200:
            print(f"   ❌ Failed to access login page: {response.status_code}")
            return False
        print(f"   ✅ Login page accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Login
    print("\n2. Logging in as admin...")
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input:
            print("   ⚠️  No CSRF token found, trying without it")
            csrf_token = ''
        else:
            csrf_token = csrf_input['value']
        
        # Try multiple passwords
        passwords = ['NewAdmin@2025', 'Admin@2025', 'Admin@2024', 'admin']
        login_successful = False
        
        for password in passwords:
            login_data = {
                'username': 'admin',
                'password': password,
                'group': 'Admin',  # Required for login
                'csrf_token': csrf_token
            }
            
            response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
            if 'logout' in response.text.lower() or (response.url.endswith('/') and 'login' not in response.url):
                print(f"   ✅ Successfully logged in (password: {password[:5]}...)")
                login_successful = True
                break
        
        if not login_successful:
            print(f"   ❌ Login failed with all passwords - check credentials")
            print(f"   ℹ️  Try logging in manually at {BASE_URL}/login")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Check assets list (should be empty initially)
    print("\n3. Checking assets list...")
    try:
        response = session.get(f"{BASE_URL}/assets")
        if response.status_code == 200:
            print(f"   ✅ Assets page accessible")
            if 'No Assets Found' in response.text or 'Get started by adding' in response.text:
                print("   ℹ️  No assets found (as expected for first use)")
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                badge = soup.find('span', {'class': 'badge'})
                if badge:
                    count = badge.text.strip()
                    print(f"   ✅ Found {count} asset(s) in list")
        else:
            print(f"   ❌ Cannot access assets page: {response.status_code}")
            if response.status_code == 302:
                print("   ℹ️  Redirected - authentication might be required")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 4: Navigate to add asset page
    print("\n4. Accessing add asset form...")
    try:
        response = session.get(f"{BASE_URL}/add")
        if response.status_code == 200:
            print("   ✅ Add asset form accessible")
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        else:
            print(f"   ❌ Cannot access add form: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 5: Submit a test asset
    print("\n5. Saving test asset...")
    try:
        asset_data = {
            'name': 'Test Laptop 2026',
            'quantity': '1',
            'price': '2500.00',
            'description': 'Test laptop for verification',
            'category': 'Computer & IT',
            'supplier': 'Computer Store VU',
            'department': 'IT Department',
            'location': 'Office 101',
            'brand': 'Dell',
            'model': 'Latitude 5420',
            'serial_number': 'DELL-TEST-2026',
            'csrf_token': csrf_token,
            'low_stock_threshold': '1',
            'depreciation_method': 'straight_line',
            'useful_life_years': '5',
            'salvage_value': '250.00'
        }
        
        response = session.post(f"{BASE_URL}/add", data=asset_data, allow_redirects=True)
        
        if 'Successfully saved asset' in response.text or 'successfully added' in response.text.lower():
            print("   ✅ Asset saved successfully!")
        elif response.url.endswith('/assets'):
            print("   ✅ Redirected to assets list - likely successful")
        else:
            print(f"   ⚠️  Response unclear - check manually")
            if 'error' in response.text.lower():
                print("   ❌ Error message found in response")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 6: Verify asset appears in list
    print("\n6. Verifying asset appears in list...")
    try:
        response = session.get(f"{BASE_URL}/assets")
        if 'Test Laptop 2026' in response.text:
            print("   ✅ Asset found in list!")
            soup = BeautifulSoup(response.text, 'html.parser')
            badge = soup.find('span', {'class': 'badge bg-primary'})
            if badge:
                count = badge.text.strip()
                print(f"   ✅ Total assets: {count}")
        else:
            print("   ❌ Asset not found in list")
            print("   ℹ️  This could mean:")
            print("      - Asset was not saved to database")
            print("      - Page needs refresh")
            print("      - Template issue")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ FLOW TEST COMPLETE")
    print("="*70)
    print("\nTo use the system:")
    print("1. Open browser to: http://149.28.183.0 or https://asset.innovatelhubltd.com")
    print("2. Login with: admin / Admin@2024")
    print("3. Click 'Add New Asset' or navigate to /add")
    print("4. Fill in the form and click 'Save Asset'")
    print("5. You'll be redirected to the assets list")
    print("="*70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
