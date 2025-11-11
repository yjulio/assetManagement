# Asset Purchase Order (APO) System Documentation

## Overview
Complete Asset Purchase Order management system with file upload capabilities for the Asset Management System.

## Features

### 1. **Add APO Page** (`/apo/add`)

#### Form Fields
- **APO Number** (Required) - Unique identifier for the purchase order
- **Supplier** (Required) - Select from existing suppliers or specify "Other"
- **Department** - Department making the purchase
- **Status** (Required) - Pending, Approved, Processing, Delivered, Cancelled
- **APO Date** (Required) - Date of the purchase order
- **Expected Delivery Date** - When items are expected to arrive
- **Total Amount** (Required) - Total cost of the purchase order
- **Description** - Details about items being purchased
- **Additional Notes** - Special instructions or information

#### File Upload Section
- **Multiple file upload** - Attach APO documents, invoices, quotes, etc.
- **Drag-and-drop support** - Drag files directly into the upload area
- **File preview** - See all attached files before submitting
- **Individual file removal** - Remove unwanted files before upload
- **Supported formats**: PDF, Word (DOC/DOCX), Excel (XLS/XLSX), Images (JPG/JPEG/PNG)
- **File size display** - Shows size in KB or MB

#### User Interface
```
📄 Add Asset Purchase Order
Create a new APO record with file attachments

[Form Fields]
- APO Number, Supplier
- Department, Status
- APO Date, Expected Delivery Date
- Total Amount
- Description
- Additional Notes

📎 Attach APO Documents
[Drag & Drop Area]
📄 quote_2025.pdf (1.2 MB) [✕ Remove]
📘 vendor_proposal.docx (850 KB) [✕ Remove]

[➕ Create APO] [Cancel]
```

---

### 2. **View All APOs** (`/apo/list`)

#### Features
- **Card-based layout** - Modern, visual display of APOs
- **Status filtering** - Filter by Pending, Approved, Processing, Delivered, Cancelled
- **Search functionality** - Search by APO number or supplier name
- **Status badges** - Color-coded visual indicators
- **File count display** - Shows number of attached documents
- **Click to view** - Click any card to view full details

#### Filter Section
```
[All Status ▼] [🔍 Search by APO number, supplier...] [📤 Upload Files] [➕ Add APO]
```

#### APO Cards Display
```
┌─────────────────────────────┐
│ APO-2025-001               │
│ Tech Suppliers Inc          │
├─────────────────────────────┤
│ Status: PENDING             │
│ Department: IT Department   │
│ Date: 2025-01-15           │
│ Amount: $5,250.00          │
│ Files Attached: 3 file(s)  │
└─────────────────────────────┘
```

#### Bulk Upload Modal
- Click "📤 Upload Files" to open modal
- Upload multiple documents at once
- Drag-and-drop support
- File type icons (PDF, Word, Excel, Images)
- Ajax-based upload (no page reload)
- Success/error notifications

---

### 3. **View APO Details** (`/apo/view/<id>`)

#### Information Displayed
- **APO Number** and basic details
- **Supplier, Status, Department**
- **Dates** - APO date and expected delivery
- **Total Amount**
- **Description and Notes**
- **Attached Documents** with download links

#### File Display
```
📕 purchase_order.pdf
Uploaded: January 15, 2025 at 02:30 PM by john.doe
[⬇️ Download]

📘 vendor_quote.docx
Uploaded: January 15, 2025 at 02:31 PM by john.doe
[⬇️ Download]
```

---

## Database Schema

### APO Table
```sql
CREATE TABLE IF NOT EXISTS lpo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apo_number VARCHAR(100) UNIQUE NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    apo_date DATE NOT NULL,
    delivery_date DATE,
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    description TEXT,
    notes TEXT,
    uploaded_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier) REFERENCES suppliers(name) ON DELETE RESTRICT
);
```

### APO Files Table
```sql
CREATE TABLE IF NOT EXISTS apo_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apo_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    saved_filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (apo_id) REFERENCES lpo(id) ON DELETE CASCADE
);
```

### APO Items Table (Future Enhancement)
```sql
CREATE TABLE IF NOT EXISTS apo_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apo_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (apo_id) REFERENCES lpo(id) ON DELETE CASCADE
);
```

---

## Backend Routes

### 1. `/apo/add` (GET, POST)
**Purpose:** Create new APO with file attachments

**POST Process:**
1. Extract form data (APO details)
2. Insert APO record into database
3. Get inserted APO ID
4. Process file uploads
5. Save files to `uploads/apo/` directory
6. Store file metadata in `apo_files` table
7. Commit transaction
8. Flash success message
9. Redirect to `/apo/list`

**File Naming Convention:**
```
Format: YYYYMMDD_HHMMSS_original_filename.ext
Example: 20250115_143025_purchase_order.pdf
```

---

### 2. `/apo/list` (GET)
**Purpose:** Display all APOs with filtering and search

**Process:**
1. Query all APOs from database
2. Join with `apo_files` to get file count
3. Order by date (newest first)
4. Pass data to template
5. Render card-based list view

---

### 3. `/apo/upload` (POST)
**Purpose:** Handle bulk file uploads via Ajax

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Files: `apo_files` array
- Optional: `apo_id` to associate with specific APO

**Response (JSON):**
```json
{
  "success": true,
  "message": "3 file(s) uploaded successfully",
  "files": [
    {
      "original_name": "quote.pdf",
      "saved_name": "20250115_143025_quote.pdf",
      "path": "/uploads/apo/20250115_143025_quote.pdf"
    }
  ]
}
```

---

### 4. `/apo/view/<id>` (GET)
**Purpose:** Display detailed APO information

**Process:**
1. Query APO by ID
2. Query associated files
3. Render detailed view template
4. Show download links for files

---

## File Storage

### Directory Structure
```
/root/assetManagement/
└── uploads/
    └── apo/
        ├── 20250115_143025_purchase_order.pdf
        ├── 20250115_143130_vendor_quote.docx
        └── 20250115_144520_invoice.xlsx
```

### Security
- **Filename sanitization** - Uses `werkzeug.utils.secure_filename()`
- **Authentication required** - All routes protected with `@login_required`
- **File type validation** - Client-side accept attribute
- **Unique filenames** - Timestamp prefix prevents overwrites

---

## Installation & Setup

### 1. Run Database Migration
```bash
cd /root/assetManagement
mysql -u root -p db_asset < sql/create_apo_table.sql
```

### 2. Create Upload Directory
```bash
mkdir -p uploads/lpo
chmod 755 uploads/lpo
```

### 3. Verify Routes
Routes are already added to `src/app.py`:
- `/apo/add` - Add new APO
- `/apo/list` - View all APOs
- `/apo/upload` - Bulk file upload
- `/apo/view/<id>` - View APO details

### 4. Access the System
- Navigate to **Advanced → Asset Purchase Orders** in the menu
- Or directly access: `http://your-domain/apo/list`

---

## User Workflow

### Creating an APO with Documents
1. Click **Advanced → Asset Purchase Orders → Add APO**
2. Fill in required fields (APO Number, Supplier, Amount, Date, Status)
3. Add optional information (Department, Delivery Date, Description, Notes)
4. Click "📎 Choose Files or Drag & Drop" or drag files into the area
5. Review attached files in the list
6. Remove any unwanted files
7. Click "➕ Create APO" to submit
8. View success message and redirect to list

### Uploading Files to Existing APO
1. Go to **Asset Purchase Orders** list page
2. Click "📤 Upload Files" button
3. Modal opens with upload interface
4. Select or drag multiple files
5. Review file list with icons and sizes
6. Click "📤 Upload Files"
7. Files upload via Ajax
8. Success notification appears
9. Page refreshes automatically

### Viewing APO Details
1. Click any APO card from the list
2. View complete APO information
3. See all attached documents
4. Download files individually
5. Click "← Back to List" to return

---

## Status Values

| Status | Description | Badge Color |
|--------|-------------|-------------|
| **Pending** | APO created, awaiting approval | Yellow |
| **Approved** | APO approved, ready to process | Green |
| **Processing** | Order being fulfilled | Blue |
| **Delivered** | Items delivered | Light Blue |
| **Cancelled** | APO cancelled | Red |

---

## Files Created

### Templates
1. `src/templates/apo_add.html` - Add APO form with file upload
2. `src/templates/apo_list.html` - APO list with bulk upload modal
3. `src/templates/apo_view.html` - Detailed APO view

### SQL
1. `sql/create_apo_table.sql` - Database schema

### Routes (Modified)
1. `src/app.py` - Added APO routes (lines ~906-1080)

### Navigation (Modified)
1. `src/templates/base.html` - Added APO menu under Advanced

---

## Future Enhancements

### Line Items Management
- [ ] Add/edit individual line items per APO
- [ ] Automatic amount calculation from items
- [ ] Item quantity and unit price tracking

### Approval Workflow
- [ ] Multi-level approval system
- [ ] Email notifications for approvals
- [ ] Approval history tracking
- [ ] Digital signatures

### Reporting & Analytics
- [ ] APO reports by date range
- [ ] Supplier spending analysis
- [ ] Department budget tracking
- [ ] Export to Excel/PDF

### Integration
- [ ] Link APOs to asset purchases
- [ ] Automatic asset creation from delivered APOs
- [ ] Inventory replenishment tracking
- [ ] Supplier performance metrics

### Advanced Features
- [ ] APO templates for recurring purchases
- [ ] Bulk APO creation from CSV
- [ ] OCR for automatic data extraction from PDFs
- [ ] Budget allocation and tracking
- [ ] Payment status tracking
- [ ] Delivery confirmation system

---

## Testing Checklist

- [x] Create APO without files
- [x] Create APO with single file
- [x] Create APO with multiple files
- [x] Drag-and-drop file upload
- [x] Remove file before submission
- [x] View APO list
- [x] Filter APOs by status
- [x] Search APOs
- [x] View APO details
- [x] Download attached files
- [x] Bulk file upload modal
- [ ] Test all file types (PDF, Word, Excel, Images)
- [ ] Test with large files
- [ ] Test file security (filename sanitization)
- [ ] Test authentication requirements

---

## Troubleshooting

### Issue: Files not uploading
**Solution:** 
- Check `uploads/apo/` directory exists and is writable
- Verify Flask `UPLOAD_FOLDER` config is set correctly
- Check file size limits in nginx/Flask config

### Issue: Database errors
**Solution:**
- Verify APO tables exist: `SHOW TABLES LIKE 'lpo%';`
- Run migration script: `mysql -u root -p db_asset < sql/create_apo_table.sql`
- Check foreign key constraints (supplier must exist in suppliers table)

### Issue: Files not showing in list
**Solution:**
- Check file path: `/uploads/apo/`
- Verify `apo_files` table has records
- Ensure web server can serve files from uploads directory

---

## Support

**Module:** Asset Purchase Order System  
**Developer:** Julio Yaruel  
**Date:** January 2025  
**Version:** 1.0  
**Contact:** minomoya626@gmail.com  

---

**End of Documentation**
