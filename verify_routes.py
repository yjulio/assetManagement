#!/usr/bin/env python3
"""
Comprehensive Route Verification Script
Checks all navigation menu links have corresponding Flask routes
"""

import sys
import os
sys.path.insert(0, '/home/assetManagement/src')

def verify_routes():
    """Verify all routes are registered and accessible"""
    
    print("=" * 70)
    print("ROUTE VERIFICATION SYSTEM")
    print("=" * 70)
    
    # Critical navigation routes that must exist
    critical_routes = [
        '/',  # Dashboard
        '/login', '/logout', '/profile',  # Auth
        '/assets', '/add', '/update', '/delete',  # Assets
        '/checkout', '/checkin', '/reserve', '/maintenance',  # Operations
        '/lease', '/lease-return', '/move', '/dispose',  # Asset Management
        '/data-quality', '/import', '/export/assets',  # Data
        '/users', '/groups', '/employees', '/customers', '/suppliers',  # People
        '/company-info', '/locations', '/departments', '/categories',  # Setup
        '/contracts', '/database', '/backup', '/restore',  # System
        '/settings/email', '/settings/system',  # Settings
        '/help-support', '/help/user-guide', '/help/faq',  # Help
        
        # Alerts
        '/alerts/assets-past-due', '/alerts/contracts-expiring',
        '/alerts/leases-expiring', '/alerts/maintenance-due',
        '/alerts/maintenance-overdue', '/alerts/warranties-expiring',
        
        # Exports
        '/export/users', '/export/maintenance', '/export/transactions', '/export/all',
        
        # Galleries
        '/document-gallery', '/image-gallery',
        
        # Reports
        '/reports/automated', '/reports/custom', '/reports/inventory',
        '/reports/asset', '/reports/audit', '/reports/checkout',
        '/reports/contract', '/reports/depreciation', '/reports/funding',
        '/reports/lease-asset', '/reports/maintenance', '/reports/reservation',
        '/reports/status', '/reports/transaction', '/reports/other',
        
        # Lists
        '/lists/assets', '/lists/maintenances', '/lists/contracts',
        
        # APO
        '/apo/add', '/apo/list',
        
        # Customize Forms
        '/customize-assets-form', '/customize-maintenance-form',
        
        # Help
        '/help/documentation', '/help/video-tutorials',
        '/help/contact-support', '/help/system-info', '/help/release-notes',
    ]
    
    try:
        # Import app
        from app import app
        
        # Get all registered routes
        registered_routes = set()
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                registered_routes.add(rule.rule)
        
        print(f"\n✅ Total routes registered: {len(registered_routes)}")
        print(f"📋 Critical routes to verify: {len(critical_routes)}\n")
        
        # Check each critical route
        missing_routes = []
        found_routes = []
        
        for route in critical_routes:
            # Check if exact match exists
            if route in registered_routes:
                found_routes.append(route)
            else:
                # Check if route with parameters exists (e.g., /update/<id>)
                route_found = False
                for reg_route in registered_routes:
                    if reg_route.startswith(route.rstrip('/')) and (
                        reg_route == route or 
                        reg_route.startswith(route + '/') or
                        reg_route.startswith(route + '<')
                    ):
                        found_routes.append(route)
                        route_found = True
                        break
               
                if not route_found:
                    missing_routes.append(route)
        
        # Report results
        print("=" * 70)
        print("VERIFICATION RESULTS")
        print("=" * 70)
        print(f"\n✅ Found: {len(found_routes)} / {len(critical_routes)} routes")
        print(f"❌ Missing: {len(missing_routes)} routes\n")
        
        if missing_routes:
            print("⚠️  Missing Routes:")
            print("-" * 70)
            for route in sorted(missing_routes):
                print(f"  ❌ {route}")
        else:
            print("🎉 SUCCESS! All critical navigation routes are registered!")
        
        print("\n" + "=" * 70)
        print("ROUTE CATEGORIES")
        print("=" * 70)
        
        # Categorize routes
        categories = {
            'Alerts': [r for r in registered_routes if '/alerts/' in r],
            'Assets': [r for r in registered_routes if any(x in r for x in ['/assets', '/add', '/update', '/delete', '/checkout', '/checkin'])],
            'Reports': [r for r in registered_routes if '/reports/' in r],
            'Export': [r for r in registered_routes if '/export/' in r],
            'Lists': [r for r in registered_routes if '/lists/' in r],
            'Help': [r for r in registered_routes if '/help' in r],
            'Settings': [r for r in registered_routes if '/settings/' in r],
            'APO': [r for r in registered_routes if '/apo/' in r],
        }
        
        for category, routes in categories.items():
            if routes:
                print(f"\n{category}: {len(routes)} routes")
                for route in sorted(routes)[:5]:  # Show first 5
                    print(f"  ✓ {route}")
                if len(routes) > 5:
                    print(f"  ... and {len(routes) - 5} more")
        
        print("\n" + "=" * 70)
        
        return len(missing_routes) == 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_routes()
    sys.exit(0 if success else 1)
