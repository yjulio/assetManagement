# Mobile Features User Guide

## Overview
The VBOS Asset Management System now includes comprehensive mobile features designed for field use in remote areas of Vanuatu. These features enable offline functionality, QR code scanning, photo management, document uploads, and digital signatures.

## Features Implemented

### 1. QR Code / Barcode Scanning
**Purpose:** Quickly identify and access asset information using mobile devices.

**How to Use:**
1. Navigate to **Mobile Features → QR Code Scanner** (`/mobile/qr-scanner`)
2. Click "Start Scanner" to activate your device's camera
3. Point the camera at any asset QR code or barcode
4. The system automatically redirects to the asset details page
5. View asset information, perform actions, or capture photos

**Generate QR Codes:**
- Go to **Mobile Features → Generate QR Codes** (`/mobile/asset-qr-codes`)
- Select assets to generate QR codes for
- Print the QR code sheet for labeling physical assets

### 2. Asset Photo Gallery
**Purpose:** Maintain visual records of assets with mobile camera uploads.

**How to Use:**
1. Scan an asset QR code or navigate to the asset details page
2. Click on **"Photo Gallery"** button
3. Use **"Take Photo"** button to capture with your device camera
4. Or use **"Upload Photos"** to select from your device
5. Photos are automatically associated with the asset
6. View, download, or delete photos as needed

**Supported Formats:** JPG, JPEG, PNG, GIF (max 16MB per photo)

### 3. Document Uploads
**Purpose:** Attach invoices, warranties, manuals, and certificates to assets.

**How to Use:**
1. Navigate to **Tools → Document Gallery** (`/document-gallery`)
2. Click **"Upload Document"**
3. Select document type:
   - Invoice
   - Warranty
   - Manual
   - Certificate
   - Other
4. Choose file and add optional description
5. Upload to associate with the asset

**Supported Formats:** PDF, DOC, DOCX, XLS, XLSX, JPG, PNG (max 16MB)

### 4. Digital Signature for Asset Handover
**Purpose:** Capture digital signatures when transferring assets between staff or departments.

**How to Use:**
1. Navigate to **Mobile Features → Asset Handover** 
2. Or from asset details page, click **"Digital Handover"**
3. Fill in handover details:
   - Asset being transferred
   - From (current holder)
   - To (new recipient)
   - Handover notes
4. Capture signatures:
   - **From signature:** Current holder signs first
   - **To signature:** Recipient signs to accept
5. Click **"Complete Handover"** to save
6. Signatures are stored securely with timestamp

**Signature Features:**
- Touch/stylus drawing on mobile devices
- Mouse drawing on desktop
- "Clear" button to reset signature
- Validation ensures both signatures are captured

### 5. Offline Mode (PWA)
**Purpose:** Continue working in remote areas without internet connectivity.

**How It Works:**
The system is a Progressive Web App (PWA) that caches essential data for offline use.

**Installation:**
1. Open the system in Chrome, Edge, or Safari on mobile
2. Look for the "Install App" prompt or click the install button in the address bar
3. Add to home screen for native app-like experience
4. The app icon appears on your device like any other app

**Offline Capabilities:**
- ✅ View recently accessed assets
- ✅ Browse cached asset lists
- ✅ View asset details
- ✅ Capture photos (stored locally until online)
- ✅ Record handover signatures (synced when online)
- ✅ Scan QR codes
- ❌ Cannot create new assets offline
- ❌ Cannot perform database write operations

**Background Sync:**
When you return to an area with internet:
1. The app automatically detects connectivity
2. Queued photos and handovers upload in the background
3. You receive notifications when sync completes
4. Data is merged with the live database

**Offline Indicator:**
- A red "Offline" banner appears at the top when disconnected
- A green "Online" banner appears when connection is restored

## Technical Details

### Database Tables Created
The mobile features use the following database tables:

1. **asset_handovers**
   - Records all digital signature handovers
   - Stores signature paths and timestamps
   - Tracks from/to personnel

2. **asset_photos**
   - Stores asset-specific photo metadata
   - Links to physical photo files
   - Tracks upload date and file size

3. **asset_documents**
   - Manages document uploads
   - Tracks document type and expiry dates
   - Links documents to specific assets

4. **qr_code_scans**
   - Analytics for QR code usage
   - Tracks scan timestamps and locations
   - Monitors which assets are scanned most

5. **offline_sync_queue**
   - Manages offline operation queue
   - Stores pending uploads and actions
   - Ensures data integrity during sync

### File Storage Locations
- **Asset Photos:** `/uploads/assets/{asset_name}/photos/`
- **Asset Documents:** `/uploads/assets/{asset_name}/documents/`
- **Signatures:** `/uploads/signatures/{timestamp}_{from}_{to}.png`
- **QR Codes:** `/src/static/qrcodes/{asset_name}.png`

### Browser Compatibility
- ✅ Chrome (mobile & desktop)
- ✅ Edge (mobile & desktop)
- ✅ Safari (iOS & macOS)
- ✅ Firefox (mobile & desktop)
- ❌ Internet Explorer (not supported)

### Camera Permissions
The QR scanner and photo upload require camera access:
1. Browser prompts for camera permission on first use
2. Grant permission to enable scanning and photos
3. Permissions are remembered for future visits
4. Check browser settings if camera doesn't work

## Use Cases for Vanuatu Context

### Scenario 1: Remote Asset Verification
**Problem:** Field staff in outer islands need to verify asset condition without internet.

**Solution:**
1. Before traveling, open the app while online to cache asset data
2. Install PWA on mobile device
3. Travel to remote location without internet
4. Scan asset QR codes to view details
5. Capture condition photos offline
6. Record handover signatures offline
7. When back online, photos and signatures sync automatically

### Scenario 2: Asset Transfer Documentation
**Problem:** Need proof of asset transfers between departments.

**Solution:**
1. Scan asset QR code
2. Click "Digital Handover" button
3. Fill in transfer details
4. Both parties sign digitally
5. Handover record stored with timestamps
6. Audit trail maintained for accountability

### Scenario 3: Maintenance Documentation
**Problem:** Need visual records of asset condition before/after maintenance.

**Solution:**
1. Scan asset QR code before maintenance
2. Take "before" photos
3. Perform maintenance work
4. Take "after" photos
5. Upload maintenance invoice/receipt
6. Complete photo gallery shows maintenance history

## Troubleshooting

### QR Scanner Not Working
- **Issue:** Camera doesn't activate
- **Solutions:**
  - Check browser camera permissions
  - Try refreshing the page
  - Ensure no other app is using the camera
  - Use a different browser (Chrome recommended)

### Photos Not Uploading
- **Issue:** Upload fails or hangs
- **Solutions:**
  - Check file size (max 16MB)
  - Verify file format (JPG, PNG, GIF only)
  - Ensure stable internet connection
  - Try compressing large photos
  - Check available server storage

### Offline Mode Not Working
- **Issue:** App doesn't work offline
- **Solutions:**
  - Reinstall PWA (remove and add to home screen again)
  - Clear browser cache and revisit while online
  - Ensure you visited pages while online first (to cache them)
  - Check browser PWA support (use Chrome/Edge)

### Signature Pad Not Responding
- **Issue:** Can't draw signature
- **Solutions:**
  - Try different finger/stylus pressure
  - Use mouse if on desktop
  - Refresh page and try again
  - Check if touch events are blocked

## Best Practices

1. **Before Field Work:**
   - Install PWA while connected to WiFi
   - Visit key asset pages to cache data
   - Test camera and signature functionality

2. **QR Code Management:**
   - Print QR codes on durable labels
   - Place codes in visible but protected locations
   - Generate backup QR codes for critical assets
   - Keep a printed QR code directory

3. **Photo Management:**
   - Capture photos in good lighting
   - Take multiple angles of assets
   - Compress photos before upload if on slow connection
   - Delete blurry or unnecessary photos

4. **Document Organization:**
   - Use consistent naming for documents
   - Add descriptions to make documents searchable
   - Track expiry dates for warranties and certificates
   - Upload original documents when possible

5. **Signature Captures:**
   - Ensure signers understand what they're signing
   - Verify signatures are clear before submitting
   - Use landscape orientation on mobile for larger signature pad
   - Keep mobile device steady while signing

## Support and Updates

For technical support or feature requests:
- Contact IT Department: support@vbos.gov.vu
- Report bugs through the system feedback form
- Check for system updates regularly

## Version Information
- **Implementation Date:** February 2026
- **Version:** 1.0.0
- **Last Updated:** February 9, 2026
- **Supported Devices:** iOS 12+, Android 8+, Modern Browsers

---

*This guide is part of the VBOS Asset Management System mobile features implementation.*
