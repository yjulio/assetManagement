# Quick Reference Guide - Export, Report & Alert Features

## 📤 How to Use Export Features

### Export Assets
1. Navigate to **Navigation** → **Export Data** → **Export Assets**
2. Select format:
   - **CSV** - Opens in Excel/LibreOffice
   - **Excel** - Native .xlsx format with formatting
3. Click **"Export"** button
4. File downloads automatically (e.g., `assets_export_2026-02-09.csv`)

**Included Fields (19 total):**
- Basic: Asset Name, Asset Number, Serial Number, Model
- Financial: Purchase Price, Current Value, Depreciation
- Location: Location, Building, Floor, Room
- Dates: Purchase Date, Warranty Start/End
- **NEW:** Responsible Officer, Province, Island, Unit/Section
- **NEW:** Asset Category, LPO Number, Condition, Tag
- **NEW:** Image references (1-5)

---

### Export Users
1. Navigate to **Navigation** → **Export Data** → **Export Users**
2. Select CSV or Excel
3. Click **"Export"**

**Includes:** Username, Email, Group Memberships, Created Date, Updated Date

---

### Export Maintenance Records
1. Navigate to **Navigation** → **Export Data** → **Export Maintenance**
2. Select format
3. Click **"Export"**

**Includes:** Asset, Type, Scheduled Date, Status, Technician, Cost, Notes

---

### Export Transactions
1. Navigate to **Navigation** → **Export Data** → **Export Transactions**
2. Select format
3. Click **"Export"**

**Includes:** Asset, User, Transaction Type (Check-in/Check-out/Transfer), Date, Notes

---

### Export All Data
1. Navigate to **Navigation** → **Export Data** → **Export All**
2. Choose format:
   - **ZIP** - Multiple CSV files in one archive
   - **Excel** - Single file with multiple sheets
3. Click **"Export"**

**Includes:** Assets, Users, Maintenance, Transactions, Suppliers, Locations, Categories

---

## 📊 How to Use Reports

### Inventory Report
**Purpose:** See asset distribution by category, location, and status

1. Navigate to **Navigation** → **Reports** → **Inventory Report**
2. Select export format (CSV/Excel)
3. Click **"Generate Report"**

**Report Shows:**
- Total assets and total value
- Breakdown by category (count + value)
- Breakdown by location
- Breakdown by status (Active/Disposed/In Maintenance)
- Average asset value

---

### Depreciation Report
**Purpose:** Calculate current values and depreciation

1. Navigate to **Navigation** → **Reports** → **Depreciation Report**
2. Select format
3. Click **"Generate Report"**

**Report Shows:**
- Asset name and purchase info
- Original price
- Current depreciated value
- Depreciation amount
- Depreciation percentage
- Depreciation calculation (Straight-line method)

---

### Maintenance Report
**Purpose:** Analyze maintenance activities and costs

1. Navigate to **Navigation** → **Reports** → **Maintenance Report**
2. Select format
3. Click **"Generate Report"**

**Report Shows:**
- Maintenance by status (Pending/Completed/Cancelled)
- Maintenance by type (Preventive/Corrective/Emergency)
- Total maintenance costs
- Upcoming maintenance (next 30 days)
- Overdue maintenance

---

### Checkout Report
**Purpose:** Track asset usage and checkout patterns

1. Navigate to **Navigation** → **Reports** → **Checkout Report**
2. Select format
3. Click **"Generate Report"**

**Report Shows:**
- Assets currently checked out
- Checkout history by user
- Checkout frequency
- Asset utilization analysis

---

## 🚨 How to View Alerts

### Warranties Expiring
**Purpose:** See warranties expiring in next 30 days

1. Navigate to **Navigation** → **Alerts** → **Warranties Expiring**
2. View list of assets with expiring warranties

**Columns:**
- Asset Name
- Warranty Provider
- Warranty Start Date
- Warranty End Date
- Days Until Expiry (color-coded)

**Color Codes:**
- 🔴 Red: < 7 days
- 🟡 Yellow: 7-14 days
- 🟢 Green: 15-30 days

---

### Maintenance Due
**Purpose:** See scheduled maintenance in next 30 days

1. Navigate to **Navigation** → **Alerts** → **Maintenance Due**
2. View list of upcoming maintenance

**Columns:**
- Asset Name
- Maintenance Type
- Scheduled Date
- Assigned Technician
- Status

---

### Maintenance Overdue
**Purpose:** See overdue maintenance that hasn't been completed

1. Navigate to **Navigation** → **Alerts** → **Maintenance Overdue**
2. View list of overdue items

**Columns:**
- Asset Name
- Maintenance Type
- Scheduled Date
- Days Overdue (color-coded)
- Assigned Technician
- Status

**Color Codes:**
- 🔴 Red: > 14 days overdue
- 🟡 Yellow: 7-14 days overdue
- 🟢 Green: 1-7 days overdue

---

## 💡 Tips & Best Practices

### For Exports:
- **Excel files** preserve formatting but require openpyxl
- **CSV files** work everywhere but lose formatting
- Use **"Export All"** for backups
- Export data regularly for disaster recovery
- Large exports may take a few seconds

### For Reports:
- Run **Inventory Report** monthly for tracking
- Use **Depreciation Report** for accounting period end
- Check **Maintenance Report** weekly for cost control
- Review **Checkout Report** to identify most-used assets

### For Alerts:
- Check **Warranties Expiring** weekly to avoid lapses
- Review **Maintenance Due** daily to schedule technicians
- Address **Maintenance Overdue** immediately (escalate red items)
- Set calendar reminders to check alerts regularly

---

## 🔧 Troubleshooting

### Export Issues:

**Problem:** Excel export downloads as CSV
- **Solution:** Run `pip install openpyxl` or use CSV format

**Problem:** Large export times out
- **Solution:** Export by category or date range (contact support)

**Problem:** File doesn't download
- **Solution:** Allow downloads from your site in browser settings

---

### Report Issues:

**Problem:** Report shows "0 assets"
- **Solution:** Add assets via Inventory Management

**Problem:** Depreciation shows wrong values
- **Solution:** Update asset purchase date and salvage value

**Problem:** Report is empty
- **Solution:** Check date ranges and ensure data exists

---

### Alert Issues:

**Problem:** No alerts showing
- **Solution:** Good news! Nothing requires attention

**Problem:** Too many alerts
- **Solution:** Address overdue items or update schedules

**Problem:** Alert dates wrong
- **Solution:** Check server timezone settings

---

## 🎯 Quick Actions Checklist

### Daily Tasks:
- [ ] Check Maintenance Due
- [ ] Review Maintenance Overdue
- [ ] Address any red/critical alerts

### Weekly Tasks:
- [ ] Check Warranties Expiring
- [ ] Export Maintenance Records
- [ ] Review Maintenance Report

### Monthly Tasks:
- [ ] Run Inventory Report
- [ ] Run Depreciation Report
- [ ] Export All Data (backup)
- [ ] Review Checkout Report

### Quarterly Tasks:
- [ ] Full system backup (Export All)
- [ ] Audit asset locations
- [ ] Update maintenance schedules
- [ ] Review warranty renewals

---

**Last Updated:** February 9, 2026  
**Version:** 1.0  
**System:** Asset Management System
