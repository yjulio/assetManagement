# Import Templates Documentation

## Overview
Professional import templates for bulk asset data import with comprehensive sample data, field descriptions, and instructions. Available in both CSV and Excel formats.

## Template Files

### 1. CSV Template
**File:** `src/static/asset_import_template.csv`  
**Size:** ~4.4 KB  
**Format:** Comma-separated values

#### Features:
- Universal compatibility (Excel, Google Sheets, text editors)
- 16 columns with all available fields
- 20 sample asset records
- Easy to edit and customize
- UTF-8 encoding for international characters

#### Use Cases:
- Quick imports with spreadsheet software
- Programmatic data generation
- Simple text-based editing
- Cross-platform compatibility

---

### 2. Excel Template
**File:** `src/static/asset_import_template.xlsx`  
**Size:** ~11 KB  
**Format:** Microsoft Excel (.xlsx)

#### Features:
- **3 Worksheets:**
  1. **Instructions Sheet:** Complete guide with step-by-step instructions
  2. **Template Sheet:** Blank template with headers and field descriptions
  3. **Sample Data Sheet:** 10 realistic sample records

#### Professional Formatting:
- Color-coded headers (blue background, white text)
- Field descriptions in second row
- Bordered cells for easy data entry
- Frozen header rows
- Proper column widths
- Number formatting (integers, decimals)
- Wrapped text for descriptions

#### Instructions Included:
1. How to use the template
2. Required vs optional fields
3. Data format guidelines
4. Import process steps
5. Best practice tips

---

## Field Specifications

### Complete Field List (16 Fields)

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| **name** | ✅ YES | Text | Unique asset identifier | Dell Latitude 5520 |
| **quantity** | ✅ YES | Integer | Number of items | 15 |
| **price** | ✅ YES | Decimal | Cost per unit | 1250.00 |
| **description** | No | Text | Detailed description | 15.6 inch business laptop |
| **low_stock_threshold** | No | Integer | Alert threshold (default: 5) | 3 |
| **category** | No | Text | Asset category | Electronics |
| **supplier** | No | Text | Supplier/vendor name | Tech Suppliers Inc |
| **department** | No | Text | Department assignment | IT Department |
| **location** | No | Text | Physical location | Building A - Floor 3 |
| **model** | No | Text | Model number | Latitude 5520 |
| **brand** | No | Text | Brand/manufacturer | Dell |
| **serial_number** | No | Text | Serial number | DL5520-2024-001 |
| **purchase_date** | No | Date | Purchase date (YYYY-MM-DD) | 2024-01-15 |
| **depreciation_method** | No | Text | straight_line or declining_balance | straight_line |
| **useful_life_years** | No | Integer | Years of useful life | 5 |
| **salvage_value** | No | Decimal | Residual value | 200.00 |

### Field Validation Rules

#### Required Fields:
- **name:** Must be unique, non-empty string
- **quantity:** Must be positive integer (≥ 0)
- **price:** Must be positive decimal (≥ 0.00)

#### Optional Fields:
- All other fields default to NULL or system defaults if not provided
- Empty cells are acceptable for optional fields

#### Data Types:
- **Text:** Any string value (max 255 characters for most fields)
- **Integer:** Whole numbers only (no decimals)
- **Decimal:** Numbers with up to 2 decimal places (e.g., 1250.00)
- **Date:** Must follow ISO format YYYY-MM-DD (e.g., 2024-01-15)

#### Special Formats:
- **depreciation_method:** Only accepts:
  - `straight_line` (default)
  - `declining_balance`
- **purchase_date:** Must be valid date, not future dates
- **useful_life_years:** Typically 1-20 years
- **salvage_value:** Should be less than price

---

## Sample Data Included

### CSV Template - 20 Sample Records:
1. Dell Latitude 5520 (Laptop)
2. HP LaserJet Pro M404dn (Printer)
3. Herman Miller Aeron Chair (Furniture)
4. iPhone 14 Pro (Mobile Device)
5. Cisco Catalyst 2960 (Network Equipment)
6. Dell OptiPlex 7090 (Desktop)
7. Samsung 27" 4K Monitor (Display)
8. Logitech MX Master 3 (Mouse)
9. APC Smart-UPS 1500VA (Power Equipment)
10. Microsoft Surface Pro 9 (Tablet)
11. Canon imageCLASS MF445dw (Multifunction Printer)
12. FlexiSpot Standing Desk (Furniture)
13. Polycom VVX 450 (IP Phone)
14. Western Digital 4TB NAS (Storage)
15. Epson PowerLite Projector (Presentation)
16. Steelcase File Cabinet (Furniture)
17. Jabra Evolve2 75 (Headset)
18. HP Color LaserJet Pro M454dw (Color Printer)
19. LG UltraWide 34" Monitor (Display)
20. Netgear Nighthawk Router (Network)

### Excel Template - 10 Sample Records:
Subset of the above data for easier review and learning

### Sample Data Categories:
- **Electronics:** Laptops, desktops, monitors, tablets
- **Office Equipment:** Printers, scanners, multifunction devices
- **Furniture:** Chairs, desks, file cabinets
- **Mobile Devices:** Smartphones, tablets
- **Network Equipment:** Switches, routers, access points
- **Computer Accessories:** Mice, keyboards, headsets
- **Power Equipment:** UPS units, surge protectors
- **Communication:** IP phones, headsets
- **Storage Devices:** NAS, external drives
- **Presentation Equipment:** Projectors, screens

---

## Import Process

### Step-by-Step Guide:

#### 1. Download Template
- Navigate to **Tools → Import Data**
- Click **"Download CSV Template"** or **"Download Excel Template"**
- Save file to your computer

#### 2. Prepare Data
- Open template in Excel, Google Sheets, or text editor
- **If using Excel template:**
  - Review Instructions sheet
  - Use Template sheet for blank import
  - Use Sample Data sheet as reference
- **If using CSV template:**
  - Keep headers in first row
  - Fill data starting from row 2
- Remove or replace sample data with your actual data

#### 3. Fill Required Fields
- **name:** Enter unique asset name
- **quantity:** Enter number of items
- **price:** Enter cost (use decimal format)

#### 4. Fill Optional Fields
- Complete any additional fields as needed
- Leave empty cells for fields you don't need
- Ensure dates follow YYYY-MM-DD format

#### 5. Save File
- **CSV:** Save as .csv (UTF-8 encoding recommended)
- **Excel:** Save as .xlsx or .xls

#### 6. Upload & Import
- Go to **Tools → Import Data**
- Click **"Choose File"** and select your file
- Click **"Upload and Import Assets"**
- Wait for processing (may take time for large files)
- Check success message or error details

#### 7. Verify Import
- Navigate to **Assets** page
- Review imported assets
- Check for any missing or incorrect data
- Make manual corrections if needed

---

## Best Practices

### Before Import:
1. ✅ **Backup existing data** - Export current assets
2. ✅ **Review template** - Understand all fields
3. ✅ **Validate data** - Check for duplicates, errors
4. ✅ **Test with small file** - Import 5-10 items first
5. ✅ **Remove sample data** - Don't import examples

### Data Quality:
1. **Unique Names:** Each asset must have unique name
2. **Consistent Formatting:** Use same format for similar data
3. **Complete Information:** Fill as many fields as possible
4. **Valid Values:** Check dates, numbers, decimals
5. **Clean Data:** Remove extra spaces, special characters

### Common Mistakes to Avoid:
- ❌ Modifying column headers
- ❌ Using duplicate asset names
- ❌ Wrong date format (use YYYY-MM-DD)
- ❌ Text in number fields
- ❌ Future purchase dates
- ❌ Negative quantities or prices
- ❌ Invalid depreciation method names
- ❌ Salvage value greater than price

### Optimization Tips:
1. **Large Imports:** Break into smaller batches (100-500 items)
2. **Speed:** CSV files import faster than Excel
3. **Memory:** Close other applications for large imports
4. **Validation:** Use Excel data validation before import
5. **Backup:** Keep original import file for reference

---

## Troubleshooting

### Common Import Errors:

#### "No file provided"
**Solution:** Ensure you selected a file before clicking import

#### "Error processing file"
**Causes:**
- Invalid file format
- Corrupted file
- Missing required fields
- Wrong column headers

**Solutions:**
1. Re-download template
2. Check file isn't corrupted
3. Verify all required fields have data
4. Don't modify column headers

#### "Duplicate asset name"
**Solution:** Asset names must be unique. Check for duplicates in your file

#### "Invalid date format"
**Solution:** Use YYYY-MM-DD format (e.g., 2024-01-15)

#### "Excel import requires pandas"
**Solution:** CSV files work without pandas. Use CSV if Excel fails

#### "Invalid depreciation method"
**Solution:** Only use 'straight_line' or 'declining_balance'

---

## Template Generation Script

The Excel template is generated using Python script:
**File:** `generate_excel_template.py`

### Features:
- Automatic template creation
- Professional formatting
- Sample data generation
- Instructions page
- Field descriptions

### Regenerate Template:
```bash
cd /home/ubuntu/assetManagement
source venv/bin/activate
python generate_excel_template.py
```

### Customization:
Edit `generate_excel_template.py` to:
- Change sample data
- Modify instructions
- Update field descriptions
- Adjust formatting/colors
- Add more sample records

---

## Enhanced Import Page

### New Features (v1.0):
1. **Professional UI:**
   - Gradient header design
   - Card-based layout
   - Modern, clean interface
   - Mobile-responsive

2. **Template Download Section:**
   - Prominent template cards
   - Visual icons
   - Download buttons
   - Format descriptions

3. **Upload Section:**
   - Drag-and-drop style file input
   - Clear submission button
   - Visual feedback

4. **Field Reference Table:**
   - Complete field list
   - Required/optional indicators
   - Type specifications
   - Examples for each field

5. **Help Integration:**
   - Links to User Guide
   - Contact Support button
   - Tips and best practices

### Route:
`/import` - Import page (Admin only)

### Access Control:
`@require_group('Admin')` - Only administrators can import

---

## File Locations

```
assetManagement/
├── generate_excel_template.py          # Template generator script
├── src/
│   ├── static/
│   │   ├── asset_import_template.csv   # CSV template
│   │   ├── asset_import_template.xlsx  # Excel template
│   │   └── template.csv                # Legacy template (deprecated)
│   └── templates/
│       └── import.html                 # Import page UI
```

---

## Migration from Old Template

### Old Template (`template.csv`):
- Only 7 fields
- Basic format
- Limited sample data

### New Templates:
- 16 fields (complete)
- Professional formatting
- Rich sample data
- Instructions included

### Backward Compatibility:
✅ Old imports still work - system uses defaults for missing fields

### Recommendation:
Use new templates for all future imports for complete asset data

---

## Future Enhancements

### Planned Features:
1. **Template Builder:** Custom template generator in UI
2. **Field Mapping:** Map custom headers to system fields
3. **Validation Preview:** Check data before import
4. **Import History:** Track all imports with logs
5. **Scheduled Imports:** Automatic imports from FTP/Cloud
6. **Template Versioning:** Track template changes
7. **Multi-sheet Import:** Import from multiple Excel sheets
8. **Image Import:** Bulk upload asset images
9. **Update Import:** Update existing assets via import
10. **Import Rollback:** Undo recent imports

---

## Support

### Getting Help:
- **User Guide:** `/help/user-guide`
- **Documentation:** `/help/documentation`
- **FAQ:** `/help/faq`
- **Contact:** minomoya626@gmail.com

### Reporting Issues:
If you encounter import problems:
1. Save error message
2. Keep original import file
3. Note number of records
4. Contact support with details

---

**Template Version:** 1.0  
**Last Updated:** January 2, 2025  
**Developed By:** Julio Yaruel  
**Status:** ✅ Production Ready  
**Downloads:** Available at vbosasset.innovatelhubltd.com/import
