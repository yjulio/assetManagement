# Contract File Upload System Documentation

## Overview
Enhanced the Contracts/Licenses management system with comprehensive file upload capabilities for contract documents.

## New Features

### 1. **Add Contract Page Upload** (`/contracts/add`)

#### File Upload Section
- **Location:** Bottom of the Add Contract form
- **Features:**
  - Multiple file upload support
  - Drag-and-drop functionality
  - Visual file preview before submission
  - Individual file removal
  - Real-time file size display
  - Supported formats: PDF, Word (DOC/DOCX), Excel (XLS/XLSX), Images (JPG/JPEG/PNG)
  - Maximum file size: 10MB per file

#### User Interface
```
📎 Attach Contract Documents
[Drag & Drop Area]
Supported formats: PDF, Word, Excel, Images
Maximum file size: 10MB per file

[File List with Remove Buttons]
📄 contract_2024.pdf (2.5 MB) [✕ Remove]
📘 terms_and_conditions.docx (1.2 MB) [✕ Remove]
```

#### Technical Implementation
- **Form Encoding:** `multipart/form-data`
- **Input Name:** `contract_files` (multiple)
- **JavaScript:** 
  - Drag-and-drop event handlers
  - File preview rendering
  - File removal functionality
  - DataTransfer API for file management

---

### 2. **Bulk Upload Modal** (`/contracts/list`)

#### Upload Button
- **Location:** Contracts List page, filter section
- **Label:** "📤 Upload Existing"
- **Color:** Blue (#3498db)
- **Action:** Opens upload modal

#### Upload Modal Features
- **Modal Design:**
  - Professional centered modal with backdrop
  - Blue gradient header
  - Large drag-and-drop area
  - File list with icons
  - Ajax-based submission (no page reload)

- **Upload Area:**
  - Click to browse OR drag-and-drop
  - Visual feedback on hover
  - File type icons (📕 PDF, 📘 Word, 📗 Excel, 🖼️ Images)
  - File size display (KB/MB)
  - Remove individual files

- **File List Display:**
  ```
  📕 contract_microsoft.pdf (3.2 MB) [✕ Remove]
  📘 agreement_adobe.docx (1.8 MB) [✕ Remove]
  📗 pricing_2024.xlsx (450 KB) [✕ Remove]
  ```

- **Submit Button:**
  - Disabled until files selected
  - Shows "⏳ Uploading..." during upload
  - Success message on completion
  - Auto-close modal after upload

#### Modal Interactions
- Click outside modal to close
- Click "×" button to close
- Escape key closes modal (browser default)
- Files persist until manual removal or submission

---

## Backend Implementation

### Flask Routes

#### 1. `/contracts/add` (POST) - Enhanced
**Purpose:** Handle contract creation with file attachments

**Process:**
1. Extract form data (contract details)
2. Check for uploaded files (`contract_files`)
3. Create `uploads/contracts/` directory if not exists
4. Save each file with timestamp-prefixed unique name
5. Store contract data in database (TODO)
6. Flash success message with file count
7. Redirect to contracts list

**File Naming Convention:**
```
Format: YYYYMMDD_HHMMSS_original_filename.ext
Example: 20250102_143025_contract_microsoft.pdf
```

**Code:**
```python
@app.route('/contracts/add', methods=['GET', 'POST'])
@login_required
def contracts_add():
    if request.method == 'POST':
        # Extract form data
        contract_name = request.form.get('contract_name')
        # ... other fields ...
        
        # Handle file uploads
        uploaded_files = []
        if 'contract_files' in request.files:
            files = request.files.getlist('contract_files')
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'contracts')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, unique_filename)
                    file.save(filepath)
                    uploaded_files.append(unique_filename)
        
        flash(f'Contract "{contract_name}" added successfully! {len(uploaded_files)} file(s) uploaded.', 'success')
        return redirect('/contracts/list')
    return render_template('contracts_add.html', title='Add Contract')
```

---

#### 2. `/contracts/upload` (POST) - New Route
**Purpose:** Handle bulk contract file uploads via Ajax

**Request Format:**
- Method: POST
- Content-Type: multipart/form-data
- Files: `contract_files` array

**Response Format:**
```json
{
  "success": true,
  "message": "3 file(s) uploaded successfully",
  "files": [
    {
      "original_name": "contract.pdf",
      "saved_name": "20250102_143025_contract.pdf",
      "path": "/home/ubuntu/assetManagement/uploads/contracts/20250102_143025_contract.pdf"
    }
  ]
}
```

**Error Response:**
```json
{
  "error": "No files provided"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (no files)
- 500: Server error

**Code:**
```python
@app.route('/contracts/upload', methods=['POST'])
@login_required
def contracts_upload():
    try:
        if 'contract_files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('contract_files')
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'contracts')
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                uploaded_files.append({
                    'original_name': file.filename,
                    'saved_name': unique_filename,
                    'path': filepath
                })
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## File Storage

### Directory Structure
```
/home/ubuntu/assetManagement/
└── uploads/
    └── contracts/
        ├── 20250102_143025_contract_microsoft.pdf
        ├── 20250102_143130_agreement_adobe.docx
        └── 20250102_144520_pricing_2024.xlsx
```

### Configuration
- **Base Upload Folder:** Defined in `app.py`
  ```python
  UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
  app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
  ```
- **Contracts Subfolder:** `uploads/contracts/`
- **Auto-created:** Yes, on first upload

---

## Security Features

### 1. **Filename Security**
- Uses `werkzeug.utils.secure_filename()`
- Removes path traversal characters
- Sanitizes special characters
- Example: `../../../etc/passwd.pdf` → `etc_passwd.pdf`

### 2. **File Type Validation**
- Client-side: HTML5 `accept` attribute
  ```html
  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.xlsx,.xls"
  ```
- Server-side: TODO - Add MIME type validation

### 3. **File Size Limit**
- Client-side warning: 10MB per file
- Server-side: TODO - Add Flask upload size limit
  ```python
  app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
  ```

### 4. **Authentication**
- All routes protected with `@login_required`
- Only authenticated users can upload files

---

## JavaScript Implementation

### Add Contract Page (`contracts_add.html`)

#### File Input Handler
```javascript
const fileInput = document.getElementById('contract_files');
const uploadedFilesDiv = document.getElementById('uploadedFiles');

fileInput.addEventListener('change', function(e) {
    displayFiles(e.target.files);
});
```

#### Drag-and-Drop Handler
```javascript
fileUploadSection.addEventListener('drop', function(e) {
    e.preventDefault();
    const dt = new DataTransfer();
    
    // Add existing files
    for (let i = 0; i < fileInput.files.length; i++) {
        dt.items.add(fileInput.files[i]);
    }
    
    // Add new files
    for (let i = 0; i < e.dataTransfer.files.length; i++) {
        dt.items.add(e.dataTransfer.files[i]);
    }
    
    fileInput.files = dt.files;
    displayFiles(fileInput.files);
});
```

#### File Display Function
```javascript
function displayFiles(files) {
    uploadedFilesDiv.innerHTML = '';
    Array.from(files).forEach((file, index) => {
        const fileSize = (file.size / 1024).toFixed(2);
        const sizeUnit = fileSize > 1024 ? 
            ((file.size / 1024 / 1024).toFixed(2) + ' MB') : 
            (fileSize + ' KB');
        
        const fileItem = document.createElement('div');
        fileItem.innerHTML = `
            <span>📄 ${file.name}</span>
            <span>(${sizeUnit})</span>
            <button onclick="removeFile(${index})">✕ Remove</button>
        `;
        uploadedFilesDiv.appendChild(fileItem);
    });
}
```

---

### Contracts List Page (`contracts_list.html`)

#### Modal Functions
```javascript
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadedFilesList').innerHTML = '';
    document.getElementById('uploadSubmit').disabled = true;
}
```

#### Ajax Upload
```javascript
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const files = fileInput.files;
    
    for (let i = 0; i < files.length; i++) {
        formData.append('contract_files', files[i]);
    }
    
    uploadSubmit.innerHTML = '⏳ Uploading...';
    uploadSubmit.disabled = true;
    
    fetch('/contracts/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert('Files uploaded successfully!');
        closeUploadModal();
        window.location.reload();
    })
    .catch(error => {
        alert('Upload failed: ' + error.message);
        uploadSubmit.innerHTML = '📤 Upload Files';
        uploadSubmit.disabled = false;
    });
});
```

---

## Styling

### CSS Classes Added

#### contracts_add.html
- `.file-upload-section` - Upload area container
- `.file-label` - Upload button styling
- `.file-input` - Hidden file input
- `.file-info` - Help text styling
- `.uploaded-files` - File list container
- `.file-item` - Individual file item
- `.remove-file-btn` - Remove button styling

#### contracts_list.html
- `.action-buttons` - Button container
- `.btn-action` - Base button styling
- `.btn-upload` - Upload button specific
- `.modal` - Modal overlay
- `.modal-content` - Modal window
- `.modal-header` - Modal header with gradient
- `.upload-area` - Drag-drop area
- `.uploaded-files-list` - File list in modal
- `.uploaded-file-item` - File item in list

---

## User Workflow

### Adding Contract with Files
1. Navigate to Advanced → Contracts/Licenses → Add Contract
2. Fill in contract details (name, type, vendor, dates, etc.)
3. Scroll to "📎 Attach Contract Documents" section
4. Either:
   - Click "📎 Attach Contract Documents" button to browse
   - Drag files directly onto the upload area
5. Review uploaded files in list
6. Remove any unwanted files using "✕ Remove" button
7. Click "➕ Add Contract" to submit

### Bulk Uploading Existing Contracts
1. Navigate to Advanced → Contracts/Licenses → View All Contracts
2. Click "📤 Upload Existing" button
3. Modal opens with upload interface
4. Either:
   - Click drag-drop area to browse files
   - Drag multiple contract files onto the area
5. Review file list with icons and sizes
6. Remove any unwanted files
7. Click "📤 Upload Files" button
8. Files upload via Ajax
9. Success message appears
10. Page reloads to show updated contracts

---

## Future Enhancements (TODO)

### Database Integration
- [ ] Create `contract_files` table to store file metadata
- [ ] Link files to contract records (foreign key)
- [ ] Store original filename, saved filename, file size, upload date
- [ ] Track who uploaded each file

### File Management
- [ ] View/download uploaded contract files
- [ ] Delete contract files
- [ ] Replace/update contract files
- [ ] File versioning system
- [ ] Thumbnail preview for images/PDFs

### Advanced Features
- [ ] OCR/text extraction from PDFs
- [ ] Auto-populate contract fields from uploaded documents
- [ ] Contract expiration date extraction
- [ ] Email notifications with file attachments
- [ ] Zip multiple files for download
- [ ] File compression for large uploads
- [ ] Cloud storage integration (AWS S3, Azure Blob)

### Security Enhancements
- [ ] Server-side MIME type validation
- [ ] Virus scanning for uploaded files
- [ ] File size limit enforcement (Flask config)
- [ ] Rate limiting for uploads
- [ ] User upload quota management

### UI Improvements
- [ ] Progress bar for large file uploads
- [ ] Batch file processing status
- [ ] File preview modal (PDF viewer)
- [ ] Image thumbnail gallery
- [ ] File download counter/statistics

---

## Testing Checklist

- [ ] Upload single file via Add Contract form
- [ ] Upload multiple files via Add Contract form
- [ ] Drag-and-drop files on Add Contract page
- [ ] Remove files before submission
- [ ] Submit contract without files
- [ ] Open bulk upload modal
- [ ] Upload files via modal
- [ ] Drag-and-drop on modal
- [ ] Remove files in modal
- [ ] Close modal without uploading
- [ ] Verify files saved to uploads/contracts/
- [ ] Check filename security (special characters)
- [ ] Test file size display (KB/MB)
- [ ] Test unsupported file type rejection
- [ ] Test authentication requirement
- [ ] Verify success/error messages

---

## File Locations

### Modified Files
1. `src/templates/contracts_add.html` - Added file upload section (+180 lines)
2. `src/templates/contracts_list.html` - Added upload modal (+200 lines)
3. `src/app.py` - Enhanced routes with file handling (+70 lines)

### Upload Directory
- `uploads/contracts/` - Auto-created on first upload

---

## Dependencies

### Python Packages (Already Installed)
- `werkzeug` - For `secure_filename()` function
- `Flask` - Core framework with file upload support

### JavaScript APIs
- `DataTransfer` - For drag-and-drop file management
- `FormData` - For Ajax file uploads
- `Fetch API` - For modern Ajax requests

---

## Performance Considerations

### Client-Side
- File preview rendering may slow down with many files
- Consider pagination for file lists > 20 files
- Thumbnail generation can be CPU intensive

### Server-Side
- Large file uploads can timeout (increase nginx timeout)
- Multiple simultaneous uploads may impact server
- Disk space monitoring needed for uploads folder
- Consider async file processing for large files

### Recommendations
- Set nginx `client_max_body_size` to 50M or higher
- Add progress indicators for uploads > 5MB
- Implement file cleanup for orphaned uploads
- Monitor uploads folder disk usage

---

## Support

**Module:** Contract File Upload System  
**Developer:** Julio Yaruel  
**Date:** January 2025  
**Contact:** minomoya626@gmail.com  

---

**End of Documentation**
