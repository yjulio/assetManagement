#!/usr/bin/env python3
"""
Generate Reports - Command Line Utility
Easily generate any type of report from the command line
"""

import os
import sys
import json
from datetime import datetime

# Set environment variables
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'temp-key-for-reports'
if 'DB_PASSWORD' not in os.environ:
    os.environ['DB_PASSWORD'] = 'change-this-password'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from AssetManagement import InventorySystem
from utils.report_generators import (
    AutomatedReportGenerator,
    InventoryReportGenerator,
    AssetReportGenerator,
    AuditReportGenerator,
    DepreciationReportGenerator,
    MaintenanceReportGenerator,
    CheckoutReportGenerator
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n{title}")
    print("-" * 70)


def generate_automated_report(system):
    """Generate and display automated/dashboard report"""
    print_section("AUTOMATED DASHBOARD REPORT")
    
    generator = AutomatedReportGenerator(system)
    report = generator.generate()
    
    print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_subsection("Overview")
    print(f"Total Assets: {report['total_assets']}")
    print(f"Total Value: ${report['total_value']:,.2f}")
    
    print_subsection("Status Breakdown")
    for status, count in report['status_breakdown'].items():
        pct = (count / report['total_assets'] * 100) if report['total_assets'] > 0 else 0
        print(f"  {status.title():15} {count:4} ({pct:5.1f}%)")
    
    print_subsection("Top 5 Assets by Value")
    for i, asset in enumerate(report['top_assets'][:5], 1):
        print(f"{i}. {asset['name']:30} ${asset['total_value']:12,.2f} ({asset['quantity']} units)")
    
    print_subsection("Recent Activity (Last 30 Days)")
    for activity in report['recent_activity'][:10]:
        print(f"  {activity['date']} | {activity['type']:12} | {activity['asset']}")
    
    if report['maintenance_alerts']:
        print_subsection(f"⚠️  Maintenance Alerts ({len(report['maintenance_alerts'])})")
        for alert in report['maintenance_alerts'][:5]:
            print(f"  [{alert['severity'].upper()}] {alert['asset']}: {alert['reason']}")
    
    print(f"\n{report['summary']}")


def generate_inventory_report(system, filters=None):
    """Generate and display inventory report"""
    print_section("INVENTORY REPORT")
    
    generator = InventoryReportGenerator(system)
    report = generator.generate(filters)
    
    print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    if report['filters_applied']:
        print(f"Filters: {report['filters_applied']}")
    
    print_subsection("Summary")
    print(f"Total Items: {report['total_items']}")
    print(f"Total Units: {report['total_units']}")
    print(f"Total Value: ${report['total_value']:,.2f}")
    
    print_subsection("Category Breakdown")
    for category, data in sorted(report['category_breakdown'].items()):
        print(f"  {category:20} {data['count']:3} items  ${data['total_value']:12,.2f}")
    
    print_subsection("Location Breakdown")
    for location, data in sorted(report['location_breakdown'].items()):
        print(f"  {location:20} {data['count']:3} items  ${data['total_value']:12,.2f}")
    
    if report['low_stock_items']:
        print_subsection(f"⚠️  Low Stock Items ({len(report['low_stock_items'])})")
        for item in report['low_stock_items'][:10]:
            print(f"  {item['name']:30} Qty: {item['quantity']} ({item['stock_level']})")


def generate_asset_report(system, asset_name=None):
    """Generate and display asset report"""
    if asset_name:
        print_section(f"ASSET REPORT: {asset_name}")
    else:
        print_section("ALL ASSETS REPORT")
    
    generator = AssetReportGenerator(system)
    report = generator.generate(asset_name)
    
    if 'error' in report:
        print(f"\n❌ {report['error']}")
        return
    
    if asset_name:
        # Detailed single asset report
        print_subsection("Basic Information")
        for key, value in report['basic_info'].items():
            print(f"  {key.replace('_', ' ').title():20} {value}")
        
        print_subsection("Purchase Information")
        for key, value in report['purchase_info'].items():
            print(f"  {key.replace('_', ' ').title():20} {value}")
        
        print_subsection("Depreciation Information")
        for key, value in report['depreciation_info'].items():
            print(f"  {key.replace('_', ' ').title():20} {value}")
        
        if report['transaction_history']:
            print_subsection(f"Transaction History ({len(report['transaction_history'])} events)")
            for trans in report['transaction_history'][-10:]:
                print(f"  {trans.get('date', 'N/A')} | {trans.get('type', 'N/A'):12} | {trans.get('user', 'N/A')}")
        
        print_subsection("Usage Statistics")
        for key, value in report['usage_stats'].items():
            print(f"  {key.replace('_', ' ').title():20} {value}")
    else:
        # Summary of all assets
        print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Assets: {report['total_assets']}")
        
        print_subsection("Assets List")
        for asset in report['assets'][:20]:
            print(f"  {asset['name']:30} | {asset['category']:15} | Qty: {asset['quantity']:3} | ${asset['total_value']:10,.2f}")
        
        if len(report['assets']) > 20:
            print(f"\n  ... and {len(report['assets']) - 20} more assets")


def generate_audit_report(system):
    """Generate and display audit report"""
    print_section("AUDIT REPORT")
    
    generator = AuditReportGenerator(system)
    report = generator.generate()
    
    print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Assets Audited: {report['total_assets_audited']}")
    
    print_subsection(f"Health Score: {report['health_score']}/100 ({report['status'].upper()})")
    
    if report['health_score'] >= 90:
        print("  ✅ Excellent - Data quality is very good")
    elif report['health_score'] >= 75:
        print("  ✓ Good - Minor issues to address")
    elif report['health_score'] >= 60:
        print("  ⚠️  Fair - Several issues need attention")
    else:
        print("  ❌ Needs Attention - Significant issues found")
    
    print_subsection(f"Findings ({report['total_issues']} total issues)")
    
    for finding in report['findings']:
        print(f"\n  [{finding['severity'].upper()}] {finding['category']} ({finding['count']} items)")
        print(f"      {finding['recommendation']}")
        
        # Show first 3 items
        for item in finding['items'][:3]:
            if isinstance(item, dict):
                asset = item.get('asset', 'Unknown')
                issue = item.get('issue', 'No details')
                print(f"      - {asset}: {issue}")
        
        if len(finding['items']) > 3:
            print(f"      ... and {len(finding['items']) - 3} more")
    
    print(f"\n{report['summary']}")


def generate_depreciation_report(system):
    """Generate and display depreciation report"""
    print_section("DEPRECIATION REPORT")
    
    generator = DepreciationReportGenerator(system)
    report = generator.generate()
    
    print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_subsection("Financial Summary")
    print(f"Total Purchase Value:   ${report['total_purchase_value']:15,.2f}")
    print(f"Total Current Value:    ${report['total_current_value']:15,.2f}")
    print(f"Total Depreciation:     ${report['total_depreciation']:15,.2f}")
    print(f"Depreciation Rate:      {report['depreciation_rate']:15.2f}%")
    
    print_subsection("Depreciation by Method")
    for method, data in report['method_breakdown'].items():
        print(f"  {method.title():20} {data['count']:3} assets  ${data['total_depreciation']:12,.2f}")
    
    print_subsection("Depreciation by Category")
    for category, data in report['category_breakdown'].items():
        print(f"  {category:20} {data['count']:3} assets  ${data['total_depreciation']:12,.2f}  ({data['avg_depreciation_rate']:.1f}%)")
    
    print_subsection("Top 10 Depreciated Assets")
    for i, asset in enumerate(report['assets'][:10], 1):
        pct = asset['depreciation_percent']
        print(f"{i:2}. {asset['name']:25} ${asset['depreciation_amount']:10,.2f} ({pct:5.1f}%)")


def generate_maintenance_report(system):
    """Generate and display maintenance report"""
    print_section("MAINTENANCE REPORT")
    
    generator = MaintenanceReportGenerator(system)
    report = generator.generate()
    
    print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_subsection("Summary")
    print(f"Assets with Maintenance History: {report['total_assets_with_maintenance']}")
    print(f"Assets Needing Maintenance:      {len(report['needs_maintenance'])}")
    
    if report['maintenance_costs']['total'] > 0:
        print(f"Total Maintenance Costs:         ${report['maintenance_costs']['total']:,.2f}")
        print(f"Average Cost per Asset:          ${report['maintenance_costs']['average']:,.2f}")
    
    print_subsection("Top 10 High-Maintenance Assets")
    for i, record in enumerate(report['maintenance_records'][:10], 1):
        print(f"{i:2}. {record['asset']:30} {record['total_events']:3} events  Last: {record['last_maintenance']}")
    
    if report['needs_maintenance']:
        print_subsection(f"⚠️  Assets Needing Maintenance ({len(report['needs_maintenance'])})")
        for item in report['needs_maintenance'][:10]:
            print(f"  [{item['priority'].upper()}] {item['asset']:30} {item['reason']}")


def generate_checkout_report(system, period='month'):
    """Generate and display checkout report"""
    print_section(f"CHECKOUT REPORT ({period.upper()})")
    
    generator = CheckoutReportGenerator(system)
    report = generator.generate(period)
    
    print(f"\nGenerated: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Period: {report['start_date']} to {report['end_date']}")
    
    print_subsection("Summary")
    print(f"Total Checkouts: {report['total_checkouts']}")
    print(f"Assets Used:     {len(report['checkout_data'])}")
    
    print_subsection("Most Used Assets")
    for i, asset in enumerate(report['most_used_assets'], 1):
        print(f"{i:2}. {asset['asset']:30} {asset['total_checkouts']:3} checkouts")
    
    if report['user_statistics']:
        print_subsection("User Activity")
        sorted_users = sorted(
            report['user_statistics'].items(),
            key=lambda x: x[1]['total_checkouts'],
            reverse=True
        )
        for user, stats in sorted_users[:10]:
            print(f"  {user:20} {stats['total_checkouts']:3} checkouts, {len(stats['assets_checked_out'])} different assets")


def main():
    """Main entry point"""
    print("=" * 70)
    print("  ASSET MANAGEMENT REPORT GENERATOR")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\nUsage: python3 generate_reports.py <report_type> [options]")
        print("\nAvailable Reports:")
        print("  automated      - Dashboard with key metrics")
        print("  inventory      - Stock levels and valuations")
        print("  asset [name]   - Detailed asset information")
        print("  audit          - Data integrity and compliance")
        print("  depreciation   - Asset depreciation analysis")
        print("  maintenance    - Maintenance history and needs")
        print("  checkout       - Usage and checkout statistics")
        print("\nExamples:")
        print("  python3 generate_reports.py automated")
        print("  python3 generate_reports.py asset 'Laptop Dell XPS'")
        print("  python3 generate_reports.py checkout week")
        sys.exit(1)
    
    report_type = sys.argv[1].lower()
    
    try:
        # Initialize system
        print("\n🔄 Connecting to database...")
        system = InventorySystem()
        print("✅ Connected successfully\n")
        
        # Generate requested report
        if report_type == 'automated':
            generate_automated_report(system)
        
        elif report_type == 'inventory':
            filters = {}
            if len(sys.argv) > 2:
                # Parse filters (e.g., category=Electronics)
                for arg in sys.argv[2:]:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        filters[key] = value
            generate_inventory_report(system, filters if filters else None)
        
        elif report_type == 'asset':
            asset_name = sys.argv[2] if len(sys.argv) > 2 else None
            generate_asset_report(system, asset_name)
        
        elif report_type == 'audit':
            generate_audit_report(system)
        
        elif report_type == 'depreciation':
            generate_depreciation_report(system)
        
        elif report_type == 'maintenance':
            generate_maintenance_report(system)
        
        elif report_type == 'checkout':
            period = sys.argv[2] if len(sys.argv) > 2 else 'month'
            generate_checkout_report(system, period)
        
        else:
            print(f"\n❌ Unknown report type: {report_type}")
            print("Use 'python3 generate_reports.py' for usage information")
            sys.exit(1)
        
        print("\n" + "=" * 70)
        print("  REPORT COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
