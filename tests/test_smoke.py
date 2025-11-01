"""
Smoke tests for the Inventory Management System
Run with: python tests/test_smoke.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

def test_routes():
    """Test that all public routes respond with 200 or redirect appropriately."""
    app.config['TESTING'] = True
    client = app.test_client()
    
    tests = [
        ('/', 200, 'Dashboard should load'),
        ('/login', 200, 'Login page should load'),
        ('/static/asset.png', 200, 'Logo should be served'),
        ('/static/css/styles.css', 200, 'CSS should be served'),
        ('/static/template.csv', 200, 'CSV template should be served'),
    ]
    
    print("Running smoke tests...\n")
    passed = 0
    failed = 0
    
    for route, expected_status, description in tests:
        try:
            response = client.get(route, follow_redirects=False)
            if response.status_code == expected_status:
                print(f"✓ {description} (GET {route} -> {response.status_code})")
                passed += 1
            else:
                print(f"✗ {description} (GET {route} -> {response.status_code}, expected {expected_status})")
                failed += 1
        except Exception as e:
            print(f"✗ {description} (GET {route} -> ERROR: {e})")
            failed += 1
    
    # Test that protected routes redirect to login
    protected_routes = ['/add', '/update', '/suppliers', '/import', '/assign-group']
    print("\nTesting protected routes redirect when not logged in...")
    for route in protected_routes:
        try:
            response = client.get(route, follow_redirects=False)
            if response.status_code in [302, 303]:
                print(f"✓ {route} redirects when not authenticated")
                passed += 1
            else:
                print(f"✗ {route} did not redirect (got {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"✗ {route} -> ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"{'='*50}")
    
    return failed == 0

if __name__ == '__main__':
    success = test_routes()
    sys.exit(0 if success else 1)
