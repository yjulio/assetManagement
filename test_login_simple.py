#!/usr/bin/env python3
import requests
import re

# Start a session
session = requests.Session()

# Get the login page to retrieve CSRF token
response = session.get('http://localhost:5000/login')
print(f"Login page status: {response.status_code}")

# Extract CSRF token using regex
csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', response.text)

if csrf_match:
    csrf_value = csrf_match.group(1)
    print(f"CSRF token found: {csrf_value[:20]}...")
else:
    print("ERROR: No CSRF token found in login page")
    print("Searching for csrf_token in page...")
    if 'csrf_token' in response.text:
        print("csrf_token string appears in page")
    print("First 1000 chars of page:")
    print(response.text[:1000])
    exit(1)

# Attempt login with admin credentials
login_data = {
    'username': 'admin',
    'password': 'NewAdmin@2025',
    'group': 'Admin',
    'csrf_token': csrf_value
}

print("\nAttempting login...")
response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
print(f"Login response status: {response.status_code}")

if response.status_code in [301, 302, 303, 307, 308]:
    print(f"✓ Login successful! Redirect to: {response.headers.get('Location')}")
elif response.status_code == 200:
    print("✗ Login failed - page returned without redirect")
    # Try to extract error message
    error_match = re.search(r'class="alert[^"]*alert-danger[^"]*"[^>]*>([^<]+)', response.text)
    if error_match:
        print(f"Error message: {error_match.group(1).strip()}")
    else:
        print("No clear error message found")
        # Check for specific text patterns
        if 'Invalid username or password' in response.text:
            print("Found: Invalid username or password")
        if 'privileges' in response.text:
            print("Found: privilege error")
        if 'security token' in response.text:
            print("Found: CSRF token error")
