# Backup & Restore System Documentation

## Overview
The Asset Management System includes a comprehensive backup, restore, and database management system accessible through the **Setup/Configuration → 💿 Backup/Restore** menu.

## Features

### 1. Database Backup Options

#### SQL Backup (Recommended for Restoration)
- **Format**: MySQL dump (.sql)
- **Contains**: Complete database structure and data
- **Best for**: Full system restoration
- **Storage**: Saved to `/root/assetManagement/backups/` and available for download
- **Naming**: `backup_db_asset_YYYYMMDD_HHMMSS.sql`

#### Excel Backup
- **Format**: XLSX spreadsheet
- **Contains**: All tables as separate sheets
- **Best for**: Data analysis and reporting
- **Limitations**: Structure information not included

#### CSV Backup
- **Format**: ZIP archive with CSV files
- **Contains**: One CSV file per table
- **Best for**: Data portability and analysis

### 2. Database Restore

#### SQL Restore
- Upload a `.sql` backup file
- Completely replaces current database
- All users are logged out after restoration
- Verification required before execution

**Important Warnings:**
- ⚠️ Restoring will replace ALL current data
- ⚠️ Only restore from trusted backup files
- ⚠️ Ensure backup compatibility with current version
- ⚠️ Process may take several minutes

### 3. Database Maintenance Tools

#### Optimize Tables (⚡)
- Defragments and optimizes all database tables
- Reclaims unused space
- Improves query performance
- **Recommended**: Run weekly or before major operations

#### Check Tables (🔍)
- Verifies table integrity
- Detects corruption or errors
- Non-destructive operation
- **Recommended**: Run monthly or when experiencing issues

#### Repair Tables (🔨)
- Repairs corrupted or damaged tables
- Should only be used when check detects issues
- May take several minutes
- **Recommended**: Only when necessary

### 4. Backup History

The system maintains a complete history of all backup operations:
- Backup date and time
- Backup type (SQL, Excel, CSV, or Restore)
- Filename
- File size (in MB)
- Created by user
- Status (completed/failed)

**Retention**: Last 10 backups displayed on main page

### 5. Database Settings

#### Automatic Backup Configuration
- **Enable Automatic Daily Backups**: Toggle on/off
- **Backup Time**: Set time for automatic backup (24-hour format)
- **Retention Period**: Number of days to keep backups (1-365)
- **Optimize on Backup**: Run optimization during backup

**Default Settings:**
```
Auto Backup: Disabled
Backup Time: 02:00 (2:00 AM)
Retention: 30 days
Optimize: Enabled
```

### 6. Database Information

Real-time database statistics:
- Database Name: `db_asset`
- Database Type: MySQL
- Total Size: Calculated in MB
- Total Tables: Number of tables in database

## Usage Guide

### Creating a Backup

1. Navigate to **Setup/Configuration → Backup/Restore**
2. Choose backup format:
   - Click **📥 Download SQL** for complete backup
   - Click **📥 Download Excel** for data analysis
   - Click **📥 Download CSV** for portable format
3. Save the downloaded file securely
4. Verify backup appears in Backup History

### Restoring from Backup

1. Navigate to **Setup/Configuration → Backup/Restore**
2. Scroll to **Restore Database** section
3. Click **Choose File** and select your `.sql` backup
4. Click **⏮️ Restore Database**
5. Confirm the warning dialog
6. Wait for restoration to complete
7. Log back in with your credentials

### Optimizing Database

1. Navigate to **Setup/Configuration → Backup/Restore**
2. Scroll to **Database Maintenance** section
3. Click **⚡ Optimize Now**
4. Wait for optimization to complete
5. Check success message for number of tables optimized

### Configuring Automatic Backups

1. Navigate to **Setup/Configuration → Backup/Restore**
2. Scroll to **Database Information** section
3. Check **Enable Automatic Daily Backups**
4. Set desired **Backup Time** (e.g., 02:00 for 2:00 AM)
5. Set **Retention Period** (recommended: 7-30 days)
6. Check **Optimize Tables During Backup** for best performance
7. Click **💾 Save Settings**

## Database Tables

### backup_history
Stores complete backup operation history:
```sql
CREATE TABLE backup_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,      -- SQL, Excel, CSV, RESTORE
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT,                      -- Size in bytes
    created_by VARCHAR(255),               -- Username
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'completed', -- completed, failed
    notes TEXT
);
```

### database_settings
Stores database configuration:
```sql
CREATE TABLE database_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Security Features

- **Admin-Only Access**: Only users in Admin group can access
- **CSRF Protection**: All forms protected with CSRF tokens
- **File Validation**: Only `.sql` files accepted for restore
- **Secure Filenames**: Uses werkzeug's secure_filename()
- **Confirmation Dialogs**: Required for destructive operations
- **Session Management**: Users logged out after restore
- **Audit Trail**: All operations logged in backup_history

## File Locations

- **Backup Storage**: `/root/assetManagement/backups/`
- **Permissions**: `drwx------` (700) - Owner only
- **Temporary Files**: `/tmp/` (cleaned up after operations)

## Best Practices

### Backup Strategy
1. **Create regular backups**: Daily or before major changes
2. **Store offsite**: Copy backups to secure external location
3. **Test restores**: Verify backups work periodically
4. **Keep multiple versions**: Maintain at least 7-30 days of backups
5. **Document changes**: Note major updates before backing up

### Maintenance Schedule
- **Daily**: Automatic backup (if enabled)
- **Weekly**: Manual backup + optimize tables
- **Monthly**: Check tables integrity
- **As Needed**: Repair tables only when issues detected

### Before Major Operations
1. Create a SQL backup
2. Verify backup file size is reasonable
3. Store backup in safe location
4. Proceed with operation
5. Verify system functionality after changes

### Restore Procedure
1. Download current backup (safety measure)
2. Notify all users of upcoming maintenance
3. Upload and restore backup file
4. Verify system functionality
5. Notify users of completion

## Troubleshooting

### Backup Fails
- Check disk space: `df -h /root/assetManagement/backups/`
- Verify MySQL is running: `systemctl status mysql`
- Check permissions on backup directory
- Review error message in flash notification

### Restore Fails
- Verify backup file is valid SQL
- Check file size (not corrupted)
- Ensure sufficient disk space
- Verify MySQL credentials are correct
- Check error logs: `tail -f /root/assetManagement/app.log`

### Optimize/Check/Repair Issues
- Verify database connection
- Check table permissions
- Review MySQL error log: `sudo tail -f /var/log/mysql/error.log`
- Try individual table operations in MySQL console

### Automatic Backups Not Running
- Verify settings are saved: Check database_settings table
- Implement cron job for automation (future enhancement)
- Check system time is correct
- Review application logs

## API Endpoints

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/backup-restore` | GET | Admin | Main backup/restore page |
| `/backup/sql` | POST | Admin | Create SQL backup |
| `/restore/sql` | POST | Admin | Restore from SQL backup |
| `/database/optimize` | POST | Admin | Optimize all tables |
| `/database/check` | POST | Admin | Check table integrity |
| `/database/repair` | POST | Admin | Repair tables |
| `/database/settings` | POST | Admin | Update database settings |

## Future Enhancements

1. **Scheduled Backups**: Implement cron job for automatic backups
2. **Cloud Storage**: Upload backups to S3/Google Drive
3. **Backup Compression**: Gzip compression for smaller files
4. **Incremental Backups**: Only backup changed data
5. **Email Notifications**: Notify admins of backup status
6. **Backup Verification**: Automatic integrity checks
7. **Restore Preview**: View backup contents before restore
8. **Selective Restore**: Restore individual tables
9. **Backup Encryption**: Encrypt sensitive backups
10. **Backup Comparison**: Compare two backup files

## Support

For issues or questions:
1. Check this documentation
2. Review application logs
3. Verify MySQL status
4. Contact system administrator
5. Refer to Help & Support in application

---

**Last Updated**: November 3, 2025  
**Version**: 1.0  
**System**: Asset Management System - Vanuatu Bureau of Statistics
