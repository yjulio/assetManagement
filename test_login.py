#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# Start a session
session = requests.Session()

# Get the login page to retrieve CSRF token
response = session.get('http://localhost:5000/login')
print(f"Login page status: {response.status_code}")

# Parse CSRF token from the page
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})

if csrf_token:
    csrf_value = csrf_token.get('value')
    print(f"CSRF token found: {csrf_value[:20]}...")
else:
    print("ERROR: No CSRF token found in login page")
    print("First 500 chars of page:")
    print(response.text[:500])
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
print(f"Response headers: {dict(response.headers)}")

if response.status_code in [301, 302, 303, 307, 308]:
    print(f"Redirect to: {response.headers.get('Location')}")
    # Follow redirect
    response = session.get(response.headers.get('Location'), allow_redirects=False)
    print(f"After redirect status: {response.status_code}")
elif response.status_code == 200:
    print("Login page returned (likely error)")
    soup = BeautifulSoup(response.text, 'html.parser')
    error = soup.find('div', class_='alert-danger') or soup.find('div', class_='error')
    if error:
        print(f"Error message: {error.get_text(strip=True)}")
    else:
        print("No error message found in response")
        print("First 500 chars:")
        print(response.text[:500])
