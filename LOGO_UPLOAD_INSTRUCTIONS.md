# Logo Upload Instructions

## Department of Local Authorities Logo

A placeholder logo (DLA) is currently displayed in the sidebar. To upload the actual Department of Local Authorities logo:

### Method 1: Via System Settings (Recommended)

1. **Access System Settings**
   - Navigate to: Setup/Configuration → System Settings
   - Or go directly to: https://asset.innovatelhubltd.com/settings/system

2. **Upload Logo**
   - Click on the "Choose File" button under "Organization Logo"
   - Select the Department of Local Authorities logo image (PNG, JPG, or SVG)
   - Click "Save Settings"

3. **Verify**
   - The new logo will appear immediately in the sidebar
   - Refresh the page if needed

### Method 2: Manual File Upload

1. **Prepare the Logo File**
   - Recommended format: PNG or SVG
   - Recommended size: 80x80 pixels or larger (will be auto-resized)
   - Name it: `dla-logo.png` or `dla-logo.svg`

2. **Upload via Server**
   ```bash
   # Upload the logo to the images directory
   scp your-logo.png root@149.28.183.0:/home/assetManagement/src/static/images/logo.png
   ```

3. **Update Database**
   ```sql
   mysql -u user_asset -p'AssetM@nage2024' db_asset -e "
   UPDATE system_settings 
   SET setting_value = '/static/images/logo.png' 
   WHERE setting_key = 'logo_path';
   "
   ```

### Logo File Location

- **Directory:** `/home/assetManagement/src/static/images/`
- **Current Placeholder:** `logo-placeholder.svg`
- **Recommended filename:** `logo.png` or `dla-logo.png`

### Supported Formats

- PNG (recommended for photos/complex graphics)
- JPEG/JPG
- SVG (recommended for vector graphics)
- GIF
- WebP
- BMP
- ICO

### Notes

- The logo will be displayed in the sidebar header
- Maximum file size: 5MB
- The image will be automatically resized to fit the sidebar
- For best results, use a square or circular logo
- Transparent backgrounds (PNG/SVG) work best

### Current Status

✅ Logo placeholder created
✅ Sidebar configured to display logo
✅ System ready to accept custom logo upload

Upload your Department of Local Authorities logo through the System Settings page to replace the placeholder!
