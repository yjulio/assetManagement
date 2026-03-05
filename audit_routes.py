#!/usr/bin/env python3
"""Route audit script - checks all navigation links against registered routes"""

import sys
import re
sys.path.insert(0, '/home/assetManagement/src')

from app import app

# Get all registered routes
registered_routes = set()
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        registered_routes.add(rule.rule)

# Parse navigation from base.html
navigation_links = set()
with open('/home/assetManagement/src/templates/base.html', 'r') as f:
    content = f.read()
    # Find all href attributes
    href_pattern = r"href=['\"]([^'\"]+)['\"]"
    matches = re.findall(href_pattern, content)
    for match in matches:
        if match.startswith('/') and not match.startswith('{{') and match != '#':
            navigation_links.add(match)

print("=" * 80)
print("ROUTE AUDIT REPORT")
print("=" * 80)
print(f"\nTotal registered routes: {len(registered_routes)}")
print(f"Total navigation links: {len(navigation_links)}")

# Find missing routes
missing_routes = []
for link in sorted(navigation_links):
    # Check exact match or dynamic route pattern
    found = False
    for route in registered_routes:
        if link == route or route.replace('<', '').replace('>', '').startswith(link.split('?')[0]):
            found = True
            break
    if not found:
        missing_routes.append(link)

if missing_routes:
    print(f"\n⚠️  MISSING ROUTES ({len(missing_routes)}):")
    print("-" * 80)
    for route in sorted(missing_routes):
        print(f"  ✗ {route}")
else:
    print("\n✅ All navigation links have corresponding routes!")

print("\n" + "=" * 80)
