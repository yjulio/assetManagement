# Report Generation Guide

## Overview

The Asset Management System now includes comprehensive report generation scripts that can be run from the command line or integrated into your application.

## Quick Start

```bash
cd /root/assetManagement

# Generate automated dashboard report
python3 generate_reports.py automated

# Generate audit report
python3 generate_reports.py audit

# Generate inventory report
python3 generate_reports.py inventory
```

---

## Available Reports

### 1. Automated Dashboard Report

**Command:** `python3 generate_reports.py automated`

**Description:** Comprehensive overview with key metrics and recent activity

**Includes:**
- Total assets and value
- Status breakdown (available, checked out, maintenance, retired)
- Top assets by value
- Recent activity (last 30 days)
- Depreciation summary
- Maintenance alerts

**Example Output:**
```
======================================================================
  AUTOMATED DASHBOARD REPORT
======================================================================

Generated: 2025-11-04 05:36:27

Overview
----------------------------------------------------------------------
Total Assets: 15
Total Value: $182,370.00

Status Breakdown
----------------------------------------------------------------------
  Available         15 (100.0%)
  Checked_Out        0 (  0.0%)
  Maintenance        0 (  0.0%)
  Retired            0 (  0.0%)

Top 5 Assets by Value
----------------------------------------------------------------------
1. Toyota Hilux                   $   70,000.00 (2 units)
2. Office Chair                   $   20,000.00 (25 units)
3. iPhone 14 Pro                  $   18,000.00 (15 units)
```

---

### 2. Inventory Report

**Command:** `python3 generate_reports.py inventory [filters]`

**Description:** Stock levels, valuations, and inventory breakdown

**Includes:**
- Total items, units, and value
- Category breakdown with values
- Location breakdown with values
- Low stock items alerts
- Stock level assessments

**Filters:**
```bash
# Filter by category
python3 generate_reports.py inventory category="Computer Equipment"

# Filter by status
python3 generate_reports.py inventory status="available"

# Filter by location
python3 generate_reports.py inventory location="Head Office"

# Multiple filters
python3 generate_reports.py inventory category="Computer Equipment" status="available"
```

**Example Output:**
```
======================================================================
  INVENTORY REPORT
======================================================================

Summary
----------------------------------------------------------------------
Total Items: 15
Total Units: 202
Total Value: $182,370.00

Category Breakdown
----------------------------------------------------------------------
  Computer Equipment     6 items  $   52,750.00
  Furniture              3 items  $   29,240.00
  Mobile Devices         1 items  $   18,000.00
```

---

### 3. Asset Report

**Command:** `python3 generate_reports.py asset [asset_name]`

**Description:** Detailed information for single asset or all assets

**Usage:**
```bash
# All assets summary
python3 generate_reports.py asset

# Specific asset details
python3 generate_reports.py asset "Dell Latitude 5520"

# Asset with spaces in name (use quotes)
python3 generate_reports.py asset "Office Chair"
```

**Single Asset Includes:**
- Basic information (name, category, quantity, value, status, location)
- Purchase information (date, age, vendor, PO number)
- Depreciation information (method, useful life, salvage value)
- Warranty information (expiration date, status)
- Transaction history (up to 50 recent events)
- Usage statistics (checkouts, check-ins, maintenance events)
- Assignment information
- Notes

**Example Output:**
```
======================================================================
  ASSET REPORT: Dell Latitude 5520
======================================================================

Basic Information
----------------------------------------------------------------------
  Name                 Dell Latitude 5520
  Category             Computer Equipment
  Quantity             10
  Total Value          $12,000.00
  Status               available
  Location             Head Office

Purchase Information
----------------------------------------------------------------------
  Purchase Date        2024-01-15
  Age                  9m
  Vendor               Dell Inc.

Transaction History (15 events)
----------------------------------------------------------------------
  2024-10-01 | checkout     | john.doe
  2024-09-25 | checkin      | john.doe
```

---

### 4. Audit Report

**Command:** `python3 generate_reports.py audit`

**Description:** Data integrity and compliance audit

**Includes:**
- Health score (0-100)
- Data quality assessment
- Issues by severity (high, medium, low)
- Categories of issues:
  - Negative quantities
  - Invalid prices
  - Missing required fields
  - Warranty issues
  - Inactive assets (no activity in 90 days)
- Recommendations

**Health Score Ratings:**
- 90-100: Excellent
- 75-89: Good
- 60-74: Fair
- <60: Needs Attention

**Example Output:**
```
======================================================================
  AUDIT REPORT
======================================================================

Generated: 2025-11-04 05:38:15
Assets Audited: 15

Health Score: 66.67/100 (FAIR)
----------------------------------------------------------------------
  ⚠️  Fair - Several issues need attention

Findings (15 total issues)
----------------------------------------------------------------------

  [LOW] Inactive Assets (15 items)
      Review unused assets for potential disposal
      - Canon ImageRunner: No transaction history
      - Cisco Router: No transaction history

Audit Summary:
Health Score: 66.67/100 (Fair)
Total Issues Found: 15
High Severity Issues: 0

Recommendations:
- No critical issues found
- Review and update incomplete asset records
- Establish regular audit schedule
```

---

### 5. Depreciation Report

**Command:** `python3 generate_reports.py depreciation`

**Description:** Asset depreciation analysis and financial overview

**Includes:**
- Total purchase value
- Total current value
- Total depreciation amount
- Overall depreciation rate
- Depreciation by method (straight_line, declining_balance)
- Depreciation by category
- Top depreciated assets
- Asset age and remaining value

**Example Output:**
```
======================================================================
  DEPRECIATION REPORT
======================================================================

Financial Summary
----------------------------------------------------------------------
Total Purchase Value:   $      182,370.00
Total Current Value:    $      145,896.00
Total Depreciation:     $       36,474.00
Depreciation Rate:                20.00%

Depreciation by Method
----------------------------------------------------------------------
  Straight Line         12 assets  $   30,120.00
  Declining Balance      3 assets  $    6,354.00

Top 10 Depreciated Assets
----------------------------------------------------------------------
 1. Toyota Hilux                  $ 14,000.00 (20.0%)
 2. Dell Latitude 5520            $  2,400.00 (20.0%)
```

---

### 6. Maintenance Report

**Command:** `python3 generate_reports.py maintenance`

**Description:** Maintenance history and upcoming needs

**Includes:**
- Assets with maintenance history
- Total maintenance events
- Assets needing maintenance
- Last maintenance dates
- High-maintenance assets
- Maintenance costs (if available)

**Example Output:**
```
======================================================================
  MAINTENANCE REPORT
======================================================================

Summary
----------------------------------------------------------------------
Assets with Maintenance History: 8
Assets Needing Maintenance:      12

Top 10 High-Maintenance Assets
----------------------------------------------------------------------
 1. Cisco Router                       5 events  Last: 2024-10-01
 2. Canon ImageRunner                  4 events  Last: 2024-09-15

⚠️  Assets Needing Maintenance (12)
----------------------------------------------------------------------
  [MEDIUM] Dell Latitude 5520          Last maintenance: 2024-05-01
  [LOW] Office Chair                   No maintenance history
```

---

### 7. Checkout Report

**Command:** `python3 generate_reports.py checkout [period]`

**Description:** Usage and checkout statistics

**Periods:**
- `today` - Today's checkouts
- `week` - Current week
- `month` - Current month (default)
- `quarter` - Current quarter
- `year` - Current year

**Usage:**
```bash
# Current month (default)
python3 generate_reports.py checkout

# This week
python3 generate_reports.py checkout week

# This year
python3 generate_reports.py checkout year
```

**Includes:**
- Total checkouts in period
- Assets used
- Most checked-out assets
- User activity statistics
- Checkout trends

**Example Output:**
```
======================================================================
  CHECKOUT REPORT (MONTH)
======================================================================

Period: 2024-11-01 to 2024-11-04

Summary
----------------------------------------------------------------------
Total Checkouts: 45
Assets Used:     12

Most Used Assets
----------------------------------------------------------------------
 1. Dell Latitude 5520                  8 checkouts
 2. iPhone 14 Pro                       7 checkouts
 3. Canon ImageRunner                   6 checkouts

User Activity
----------------------------------------------------------------------
  john.doe             12 checkouts, 5 different assets
  jane.smith            8 checkouts, 4 different assets
```

---

## Report Output Formats

### Console Output
All reports output formatted text to console by default, perfect for:
- Quick checks
- Scheduled cron jobs
- Terminal viewing
- Email reports (pipe output)

### Redirecting to File
```bash
# Save report to file
python3 generate_reports.py automated > automated_report.txt

# Append to log file with timestamp
python3 generate_reports.py audit >> audit_log_$(date +%Y%m%d).txt

# Email report
python3 generate_reports.py inventory | mail -s "Inventory Report" admin@example.com
```

---

## Scheduling Reports

### Cron Jobs

**Daily automated report at 8 AM:**
```cron
0 8 * * * cd /root/assetManagement && python3 generate_reports.py automated > /var/log/asset_reports/daily_$(date +\%Y\%m\%d).txt
```

**Weekly inventory report (Mondays at 9 AM):**
```cron
0 9 * * 1 cd /root/assetManagement && python3 generate_reports.py inventory > /var/log/asset_reports/weekly_inventory.txt
```

**Monthly audit report (1st of month):**
```cron
0 10 1 * * cd /root/assetManagement && python3 generate_reports.py audit > /var/log/asset_reports/monthly_audit_$(date +\%Y\%m).txt
```

**Setup:**
```bash
# Create log directory
sudo mkdir -p /var/log/asset_reports
sudo chown $USER:$USER /var/log/asset_reports

# Edit crontab
crontab -e

# Add your cron jobs (see examples above)
```

---

## Integration with Web Application

### Import Report Generators

```python
from utils.report_generators import (
    AutomatedReportGenerator,
    InventoryReportGenerator,
    AssetReportGenerator,
    AuditReportGenerator,
    DepreciationReportGenerator,
    MaintenanceReportGenerator,
    CheckoutReportGenerator
)

# Initialize system
system = InventorySystem()

# Generate automated report
generator = AutomatedReportGenerator(system)
report_data = generator.generate()

# Access report data
print(f"Total Assets: {report_data['total_assets']}")
print(f"Total Value: ${report_data['total_value']:,.2f}")

# Pass to template
return render_template('report.html', report=report_data)
```

### Example Flask Route

```python
@app.route('/api/reports/automated')
@login_required
def api_automated_report():
    """API endpoint for automated report"""
    generator = AutomatedReportGenerator(system)
    report = generator.generate()
    
    # Convert datetime objects to strings for JSON
    report['generated_at'] = report['generated_at'].isoformat()
    
    return jsonify(report)
```

---

## Report Generator Classes

### Base Class: ReportGenerator

**Methods:**
- `format_currency(value)` - Format as currency
- `format_date(date_obj)` - Format date as string
- `format_percentage(value)` - Format as percentage
- `calculate_age(purchase_date)` - Calculate asset age
- `get_date_range(period)` - Get start/end dates for period

### Specific Generators

Each report type has its own generator class:

1. **AutomatedReportGenerator** - Dashboard metrics
2. **InventoryReportGenerator** - Stock and valuations
3. **AssetReportGenerator** - Detailed asset info
4. **AuditReportGenerator** - Data integrity
5. **DepreciationReportGenerator** - Financial analysis
6. **MaintenanceReportGenerator** - Maintenance tracking
7. **CheckoutReportGenerator** - Usage statistics

---

## Customization

### Create Custom Report

```python
from utils.report_generators import ReportGenerator

class CustomReportGenerator(ReportGenerator):
    """Your custom report generator"""
    
    def generate(self):
        """Generate your custom report"""
        # Your custom logic here
        data = []
        
        for name, item in self.system.inventory.items():
            # Process items
            data.append({
                'name': name,
                'custom_field': item.get('custom_field')
            })
        
        return {
            'generated_at': datetime.now(),
            'data': data,
            'summary': self._generate_summary(data)
        }
    
    def _generate_summary(self, data):
        """Generate summary text"""
        return f"Custom Report: {len(data)} items processed"
```

---

## Troubleshooting

### Error: Database Connection Failed

```bash
# Check MySQL is running
sudo systemctl status mysql

# Verify database exists
mysql -u user_asset -p'change-this-password' -e "SHOW DATABASES;"

# Check credentials in config.py
cat src/config.py | grep DB_CONFIG
```

### Error: Module Not Found

```bash
# Ensure you're in the right directory
cd /root/assetManagement

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Install dependencies
pip3 install -r requirements.txt
```

### Error: Permission Denied

```bash
# Make script executable
chmod +x generate_reports.py

# Run with python explicitly
python3 generate_reports.py automated
```

---

## Best Practices

1. **Schedule Regular Reports:**
   - Daily: Automated dashboard
   - Weekly: Inventory levels
   - Monthly: Audit and depreciation
   - Quarterly: Comprehensive review

2. **Archive Reports:**
   ```bash
   # Create archive directory
   mkdir -p ~/asset_reports_archive
   
   # Archive with timestamp
   python3 generate_reports.py automated > ~/asset_reports_archive/automated_$(date +%Y%m%d_%H%M%S).txt
   ```

3. **Monitor Data Quality:**
   - Run audit reports regularly
   - Address high-severity issues immediately
   - Maintain health score above 75

4. **Review Trends:**
   - Compare monthly reports
   - Track depreciation over time
   - Monitor checkout patterns
   - Identify maintenance needs

5. **Automate Notifications:**
   ```bash
   # Email report if health score is low
   HEALTH=$(python3 generate_reports.py audit | grep "Health Score" | awk '{print $3}' | cut -d'/' -f1)
   if [ $(echo "$HEALTH < 60" | bc) -eq 1 ]; then
       python3 generate_reports.py audit | mail -s "ALERT: Low Asset Health Score" admin@example.com
   fi
   ```

---

## Files Created

- **`src/utils/report_generators.py`** - Report generator classes
- **`generate_reports.py`** - Command-line report tool
- **`REPORT_GENERATION_GUIDE.md`** - This guide

---

## Support

For issues or questions:
1. Check this documentation
2. Review code comments in `report_generators.py`
3. Check Flask app logs
4. Verify database connectivity

---

**Last Updated:** November 4, 2025  
**Version:** 1.0.0
