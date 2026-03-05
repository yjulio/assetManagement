# System Branding Configuration Guide

## Overview
The Asset Management System now supports customizable branding including logo and titles throughout the application.

## Features
- **Editable Site Title**: Change the organization name displayed throughout the system
- **Editable Site Subtitle**: Customize the system name/subtitle
- **Custom Logo Upload**: Upload your organization's logo
- **Automatic Updates**: Changes apply immediately across all pages
- **Live Preview**: See changes before saving

## How to Access Settings

### For Admin Users:
1. Log in with an Admin account
2. Navigate to the sidebar menu
3. Go to **Settings** → **System Settings**
   - Or directly access: `https://your-domain.com/settings/system`

## Configuring Your Branding

### 1. Site Title (Organization Name)
- This appears as the main title throughout the system
- Default: "Vanuatu Bureau Of Statistics"
- Example: Your organization's official name

### 2. Site Subtitle (System Name)
- This appears as the system identifier in the sidebar and page titles
- Default: "Asset Management System"
- Example: "Asset Tracking", "Inventory Management", etc.

### 3. Logo Upload
- **Supported Formats**: PNG, JPG, GIF, SVG
- **Recommended Size**: 200x200 pixels or larger
- **Best Practices**:
  - Use transparent PNG for best results
  - Keep design simple and recognizable at small sizes
  - Square or horizontal orientation works best

### 4. Live Preview
- As you type titles, see the preview update in real-time
- When you select a logo file, preview shows immediately
- Helps ensure your branding looks correct before saving

## Where Branding Appears

Your customized branding will appear in:
- ✅ Login/Landing page
- ✅ Sidebar header
- ✅ Page titles (browser tab)
- ✅ Favicon (browser icon)
- ✅ All system pages

## Technical Details

### Database Storage
Settings are stored in the `system_settings` table:
- `setting_key`: Identifier (e.g., 'site_title', 'logo_path')
- `setting_value`: Current value
- `setting_type`: Type of setting (text, file)
- `updated_at`: Timestamp of last update
- `updated_by`: Username who made the change

### File Storage
- Uploaded logos are saved to: `/home/assetManagement/src/static/`
- Logos are renamed to: `logo.[extension]`
- Old logos are overwritten when new ones are uploaded

### Caching Considerations
- Browsers may cache logos
- To see logo changes immediately, force refresh: `Ctrl + F5` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- The system uses cache-busting for CSS, but images may still cache

## API/Programmatic Access

### Get a Setting Value
```python
from AssetManagement import InventorySystem
system = InventorySystem()
title = system.get_system_setting('site_title', default='Default Title')
```

### Update a Setting
```python
system.update_system_setting('site_title', 'New Organization Name', username='admin')
```

### Get All Settings
```python
all_settings = system.get_all_system_settings()
# Returns: {'site_title': {'value': '...', 'type': 'text'}, ...}
```

## Default Values

If no custom values are set, the system uses these defaults:
- **Site Title**: "Vanuatu Bureau Of Statistics"
- **Site Subtitle**: "Asset Management System"
- **Logo Path**: "/static/asset.png"
- **Favicon Path**: "/static/asset.png"

## Troubleshooting

### Logo Not Updating
1. Clear browser cache (Ctrl + F5)
2. Check file permissions on /home/assetManagement/src/static/
3. Verify file format is supported (PNG, JPG, GIF, SVG)
4. Check error logs: `/tmp/gunicorn_error.log`

### Settings Not Saving
1. Verify you're logged in as Admin
2. Check database connection
3. Review application logs for errors
4. Ensure CSRF token is valid (refresh page if needed)

### Titles Not Appearing
1. Verify database has the settings (check system_settings table)
2. Restart gunicorn: `sudo kill -HUP <gunicorn_master_pid>`
3. Check template cache

## Security

- **Access Control**: Only Admin users can modify system settings
- **CSRF Protection**: All form submissions require valid CSRF tokens
- **File Validation**: Only image files are accepted for logo uploads
- **Audit Trail**: Updates are tracked with username and timestamp

## Future Enhancements

Possible future additions:
- Color scheme customization
- Multiple logo variants (light/dark mode)
- Custom CSS injection
- Email template branding
- Report header/footer customization

## Support

For issues or questions:
1. Check application logs: `/tmp/gunicorn_error.log`
2. Verify database connectivity
3. Contact system administrator
