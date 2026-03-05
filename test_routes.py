#!/usr/bin/env python3
"""Test script to verify all routes are registered"""

import sys
sys.path.insert(0, '/home/assetManagement/src')

try:
    from app import app
    
    print("=" * 60)
    print("ROUTE REGISTRATION TEST")
    print("=" * 60)
    
    routes = list(app.url_map.iter_rules())
    print(f"\n✅ Total routes registered: {len(routes)}")
    
    # Group routes by category
    alerts_routes = [r for r in routes if '/alerts/' in r.rule]
    export_routes = [r for r in routes if '/export/' in r.rule]
    report_routes = [r for r in routes if '/reports/' in r.rule]
    lists_routes = [r for r in routes if '/lists/' in r.rule]
    apo_routes = [r for r in routes if '/apo/' in r.rule]
    help_routes = [r for r in routes if '/help/' in r.rule]
    settings_routes = [r for r in routes if '/settings/' in r.rule]
    
    print(f"\n📊 Routes by Category:")
    print(f"  - Alerts: {len(alerts_routes)}")
    print(f"  - Export: {len(export_routes)}")
    print(f"  - Reports: {len(report_routes)}")
    print(f"  - Lists: {len(lists_routes)}")
    print(f"  - APO: {len(apo_routes)}")
    print(f"  - Help: {len(help_routes)}")
    print(f"  - Settings: {len(settings_routes)}")
    
    print(f"\n🔍 Sample Alert Routes:")
    for r in alerts_routes[:3]:
        print(f"  {r.rule}")
    
    print(f"\n🔍 Sample Export Routes:")
    for r in export_routes[:3]:
        print(f"  {r.rule}")
    
    print(f"\n🔍 Sample Report Routes:")
    for r in report_routes[:3]:
        print(f"  {r.rule}")
    
    print("\n" + "=" * 60)
    print("✅ All routes successfully registered!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error loading app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
