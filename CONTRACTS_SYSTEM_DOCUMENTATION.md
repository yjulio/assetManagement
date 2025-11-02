# Contracts/Licenses Management System Documentation

## Overview
Complete contract and software license management system for tracking subscriptions, renewals, expirations, and license usage.

## System Components

### 1. **Add Contract Page** (`/contracts/add`)
**File:** `src/templates/contracts_add.html`

**Features:**
- Professional form with gradient purple header
- Comprehensive contract fields:
  - Contract Name
  - Contract Type (7 options: Software License, Service Contract, Maintenance Agreement, Support Contract, Lease Agreement, Warranty, Other)
  - Vendor Name
  - Contract Number
  - Start Date / End Date (date pickers)
  - Annual Cost
  - Number of Licenses
  - Auto-Renewal (dropdown: Yes/No/Contact Vendor)
  - Contact Person
  - Description/Notes (textarea)
- Form validation
- Responsive design
- Submit button with success/error handling

**Usage:**
```html
Accessible from: Advanced → Contracts/Licenses → Add Contract
Route: /contracts/add (GET/POST)
```

---

### 2. **View All Contracts** (`/contracts/list`)
**File:** `src/templates/contracts_list.html`

**Features:**
- Modern card-based layout with gradient green header
- Filter section with:
  - Contract Type filter (All Types, Software License, Service Contract, Maintenance Agreement)
  - Status filter (All Status, Active, Expiring Soon, Expired)
  - Search box
  - "Add New" button
- Contract cards displaying:
  - Contract name and status badge
  - Contract type, vendor, dates
  - Annual cost, license count
  - Action buttons (View/Edit/Renew)
- Color-coded status badges:
  - 🟢 Active (green)
  - 🟠 Expiring Soon (yellow)
  - 🔴 Expired (red)
- Hover effects and animations
- Empty state with illustration

**Sample Data Included:**
1. Microsoft Office 365 - Active
2. Adobe Creative Cloud - Expiring Soon
3. IT Support Services - Active

---

### 3. **Upcoming Renewals** (`/contracts/renewals`)
**File:** `src/templates/contracts_renewals.html`

**Features:**
- Pink/red gradient header emphasizing urgency
- Summary statistics cards:
  - Expiring in 30 Days (count)
  - Expiring in 60 Days (count)
  - Expiring in 90 Days (count)
  - Total Renewal Value (dollar amount)
- Tab system for filtering:
  - 🔴 Critical (30 Days)
  - 🟠 Warning (60 Days)
  - 🟡 Upcoming (90 Days)
- Renewal cards with:
  - Urgency badges (CRITICAL/WARNING/UPCOMING)
  - Days remaining countdown (large display)
  - Contract details (type, vendor, end date, cost, licenses)
  - Auto-renew status indicator
  - Action buttons (Start Renewal/Contact Vendor/View Details)
- Color-coded borders:
  - Red (30 days)
  - Orange (60 days)
  - Yellow (90 days)

**Sample Data:**
- Adobe Creative Cloud: 14 days remaining (CRITICAL)
- Antivirus Protection: 22 days remaining (CRITICAL)
- AWS Cloud Services: 45 days remaining (WARNING)
- Slack Business+: 75 days remaining (UPCOMING)

---

### 4. **Expired Contracts** (`/contracts/expired`)
**File:** `src/templates/contracts_expired.html`

**Features:**
- Purple gradient header
- Alert banner with warning message showing total expired count and value
- Summary statistics:
  - Total Expired count
  - Annual Value sum
  - Critical Systems count
  - Average Days Overdue
- Filter bar with type, sort, and search
- Expired contract cards with:
  - "EXPIRED" ribbon badge
  - Days overdue counter (prominent display)
  - Contract details
  - Impact Level indicator (Critical/High)
  - Business Impact section (dashed red border) explaining consequences
  - Action buttons (Renew Immediately/Contact Vendor/View Details/Archive)
- Red left border and red color theme
- Serious tone to emphasize urgency

**Sample Data:**
1. Network Security Monitoring - 67 days overdue (CRITICAL)
2. Zoom Business Plan - 34 days overdue (HIGH)
3. Backup & Disaster Recovery - 128 days overdue (CRITICAL)
4. SSL Certificate - 12 days overdue (CRITICAL)

---

### 5. **Software Licenses** (`/contracts/licenses`)
**File:** `src/templates/contracts_licenses.html`

**Features:**
- Blue gradient header (tech-focused theme)
- Summary dashboard cards:
  - Active Licenses count
  - Total Users count
  - Expiring Soon count
  - Over Capacity count (licenses exceeded)
  - Annual Spend (total cost)
- Toolbar with:
  - Category filter (Productivity, Design, Development, Security, Collaboration)
  - Status filter
  - Search box
  - "Add License" button
- License cards displaying:
  - License title and vendor
  - Status badge (Active/Expiring Soon/Expired)
  - Purchase and expiration dates
  - Annual/monthly cost
  - Total licenses/users
  - **Usage bar** with percentage (color-coded):
    - Green: Normal usage (under 95%)
    - Red: Over capacity (>100%)
  - **License key section** with:
    - Masked license key display
    - Copy button
  - Action buttons (View Details/Edit/Renew/Manage Users)
- Color-coded left borders for visual distinction

**Sample Data:**
1. Microsoft Office 365 - 185/200 licenses (92%) - Active
2. Adobe Creative Cloud - 37/35 licenses (106% - OVER CAPACITY) - Expiring Soon
3. Slack Business+ - 87/100 users (87%) - Active
4. JetBrains All Products - 21/25 licenses (84%) - Active
5. GitHub Enterprise - 104/120 seats (87%) - Active

---

## Flask Routes Configuration

### Routes Added to `src/app.py`:

```python
@app.route('/contracts/add', methods=['GET', 'POST'])
@login_required
def contracts_add():
    if request.method == 'POST':
        # TODO: Handle contract creation
        flash('Contract added successfully!', 'success')
        return redirect('/contracts/list')
    return render_template('contracts_add.html', title='Add Contract')

@app.route('/contracts/list')
@login_required
def contracts_list():
    # TODO: Fetch contracts from database
    return render_template('contracts_list.html', title='All Contracts')

@app.route('/contracts/renewals')
@login_required
def contracts_renewals():
    # TODO: Fetch contracts expiring in 30/60/90 days
    return render_template('contracts_renewals.html', title='Upcoming Renewals')

@app.route('/contracts/expired')
@login_required
def contracts_expired():
    # TODO: Fetch expired contracts
    return render_template('contracts_expired.html', title='Expired Contracts')

@app.route('/contracts/licenses')
@login_required
def contracts_licenses():
    # TODO: Fetch software licenses
    return render_template('contracts_licenses.html', title='Software Licenses')
```

**Location:** Lines ~760-790 in `src/app.py`

---

## Menu Structure

### Sidebar Menu Path:
```
Advanced
  └── Contracts/Licenses
      ├── Add Contract
      ├── View All Contracts
      ├── Upcoming Renewals
      ├── Expired Contracts
      └── Software Licenses
```

**Updated in:** `src/templates/base.html`

---

## Database Schema (TODO - Implementation Needed)

### Recommended Table: `contracts`

```sql
CREATE TABLE contracts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_name VARCHAR(255) NOT NULL,
    contract_type ENUM('Software License', 'Service Contract', 'Maintenance Agreement', 
                       'Support Contract', 'Lease Agreement', 'Warranty', 'Other') NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    contract_number VARCHAR(100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    annual_cost DECIMAL(10,2),
    license_count INT,
    auto_renew ENUM('Yes', 'No', 'Contact Vendor') DEFAULT 'No',
    contact_person VARCHAR(255),
    description TEXT,
    license_key VARCHAR(500),  -- For software licenses
    status ENUM('active', 'expiring', 'expired') GENERATED ALWAYS AS (
        CASE
            WHEN end_date < CURDATE() THEN 'expired'
            WHEN DATEDIFF(end_date, CURDATE()) <= 30 THEN 'expiring'
            ELSE 'active'
        END
    ) STORED,
    days_until_expiry INT GENERATED ALWAYS AS (DATEDIFF(end_date, CURDATE())) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Indexes for Performance:
```sql
CREATE INDEX idx_end_date ON contracts(end_date);
CREATE INDEX idx_status ON contracts(status);
CREATE INDEX idx_contract_type ON contracts(contract_type);
CREATE INDEX idx_vendor ON contracts(vendor);
```

---

## Key Features Implemented

### 1. **Visual Design**
- Gradient headers with unique colors per page
- Card-based layouts with hover effects
- Status badges with color coding
- Responsive grid systems
- Professional typography

### 2. **User Experience**
- Intuitive navigation through submenu
- Clear action buttons on every card
- Search and filter capabilities
- Visual indicators for urgency (colors, badges, countdown)
- Empty states for guidance

### 3. **Data Presentation**
- Summary statistics at top of pages
- Detailed card views with all relevant information
- Progress bars for license usage
- Days remaining/overdue counters
- Business impact explanations

### 4. **Business Logic Ready**
- Contract type categorization
- Auto-renewal tracking
- License capacity monitoring (over/under usage)
- Expiration alerts (30/60/90 day windows)
- Cost tracking and totals

---

## Next Steps for Full Implementation

### 1. **Database Integration**
- Create `contracts` table using schema above
- Update routes to fetch real data from database
- Implement POST handler for contract creation

### 2. **CRUD Operations**
- **Create:** Complete form submission handler in `/contracts/add`
- **Read:** Implement database queries in list/renewals/expired/licenses pages
- **Update:** Add edit functionality with pre-populated forms
- **Delete:** Add archive/delete capability with confirmation

### 3. **Advanced Features**
- **Email Notifications:** Send alerts for upcoming renewals
- **Calendar Integration:** Export renewal dates to calendar
- **File Attachments:** Store contract documents (PDFs)
- **Renewal History:** Track past renewals and amendments
- **Cost Analytics:** Dashboard showing spending trends
- **Vendor Management:** Link to vendor database
- **License Key Encryption:** Secure storage of license keys
- **Usage Tracking:** Record actual license usage over time
- **Contract Templates:** Pre-defined templates for common contract types
- **Approval Workflow:** Multi-stage approval for new contracts

### 4. **Reporting**
- Renewal forecast reports
- Spending by vendor/category
- License utilization reports
- Compliance reports
- Expiration calendar view

### 5. **API Integration**
- Integrate with vendor APIs for auto-renewal
- Fetch license usage data automatically
- Sync with accounting systems

---

## Testing Checklist

- [ ] All 5 routes accessible and rendering correctly
- [ ] Login required for all contract pages
- [ ] Form validation working on Add Contract page
- [ ] Filters and search functional
- [ ] Responsive design on mobile/tablet
- [ ] Action buttons perform expected operations
- [ ] Status badges display correctly
- [ ] Usage bars calculate percentages accurately
- [ ] Days remaining/overdue calculations correct
- [ ] Copy license key button functional

---

## Maintenance Notes

### Files Created:
1. `src/templates/contracts_add.html` - 7.4 KB
2. `src/templates/contracts_list.html` - 8.2 KB
3. `src/templates/contracts_renewals.html` - 11.8 KB
4. `src/templates/contracts_expired.html` - 13.5 KB
5. `src/templates/contracts_licenses.html` - 16.2 KB

### Files Modified:
1. `src/templates/base.html` - Added Contracts/Licenses submenu structure
2. `src/app.py` - Added 5 new routes

### Total Lines Added: ~2,096 lines

---

## Developer Information

**System:** Asset Management Platform  
**Module:** Contracts/Licenses Management  
**Developer:** Julio Yaruel  
**Date:** January 2025  
**Version:** 1.0  
**License:** Proprietary  

---

## Support

For questions or issues with the Contracts/Licenses module:
- Check Help & Support section in the application
- Review this documentation
- Contact: minomoya626@gmail.com

---

## Screenshots Reference

### Page Layouts:
1. **Add Contract:** Single-column form with gradient header
2. **View All:** Grid of contract cards with filters
3. **Renewals:** Tabbed interface with urgency levels
4. **Expired:** List with impact warnings
5. **Licenses:** Detailed cards with usage tracking

### Color Scheme:
- Add: Purple gradient (#667eea → #764ba2)
- List: Green gradient (#11998e → #38ef7d)
- Renewals: Pink gradient (#f093fb → #f5576c)
- Expired: Purple gradient (#667eea → #764ba2)
- Licenses: Blue gradient (#4facfe → #00f2fe)

---

**End of Documentation**
