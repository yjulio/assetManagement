# Database Configuration Guide

## Overview
The Asset Management System database is fully wired and configured with comprehensive backup, restore, and maintenance capabilities.

## Database Configuration

### Current Setup
```
Database Host: localhost
Database Name: db_asset
Database User: user_asset (for app) / root (for admin operations)
Database Type: MySQL 8.x
Connection Pool: 10 connections
Connection Timeout: 30 seconds
```

### Environment Variables
Required environment variables for production:
```bash
export DB_PASSWORD='your-secure-password'
export SECRET_KEY='your-secret-key-here'
export FLASK_DEBUG=false  # Set to true only for development
export DB_HOST='localhost'
export DB_USER='user_asset'
export DB_NAME='db_asset'
export DB_PORT='3306'
```

### Configuration Files

#### 1. `/root/assetManagement/src/config.py`
Central configuration file containing:
- **DB_CONFIG**: Database connection settings
- **FLASK_CONFIG**: Flask application settings
- **EMAIL_CONFIG**: Email notification settings
- **BACKUP_CONFIG**: Backup and restore settings
- **DATABASE_SETTINGS**: Database management settings

#### 2. `/root/assetManagement/src/db/db_utils.py`
Database utility functions module:
- `get_database_info()` - Get database statistics
- `create_sql_backup()` - Create SQL backup
- `restore_sql_backup()` - Restore from backup
- `optimize_database_tables()` - Optimize all tables
- `check_database_tables()` - Check table integrity
- `repair_database_tables()` - Repair corrupted tables
- `get_backup_settings()` - Retrieve backup configuration
- `update_backup_settings()` - Update backup configuration
- `log_backup_operation()` - Log backup operations

## Database Tables

### Core Tables (23+ tables)
- `users` - User accounts and authentication
- `groups` - User permission groups
- `assets` - Asset inventory
- `asset_transactions` - Asset transaction history
- `employees` - Employee records
- `departments` - Department structure
- `locations` - Asset locations
- `categories` - Asset categories
- `subcategories` - Asset subcategories
- `suppliers` - Supplier information
- `customers` - Customer records
- `maintenance` - Maintenance records
- `contracts` - Contract and license management
- ... and more

### Backup & Management Tables
- **`backup_history`** - Backup operation logs
  ```sql
  - id (INT, AUTO_INCREMENT, PRIMARY KEY)
  - backup_type (VARCHAR 50) - SQL, Excel, CSV, RESTORE
  - filename (VARCHAR 255) - Backup filename
  - file_size (BIGINT) - File size in bytes
  - created_by (VARCHAR 255) - Username
  - created_at (TIMESTAMP) - Operation timestamp
  - status (VARCHAR 50) - completed, failed
  - notes (TEXT) - Additional information
  ```

- **`database_settings`** - Database configuration
  ```sql
  - id (INT, AUTO_INCREMENT, PRIMARY KEY)
  - setting_key (VARCHAR 100, UNIQUE) - Setting identifier
  - setting_value (TEXT) - Setting value
  - description (TEXT) - Setting description
  - updated_by (VARCHAR 255) - Last updated by
  - updated_at (TIMESTAMP) - Last update time
  ```

### Current Database Settings
```
auto_backup_enabled: false
auto_backup_time: 02:00
backup_retention_days: 30
backup_location: /root/assetManagement/backups/
optimize_on_backup: true
```

## Backup Configuration

### Backup Storage
- **Directory**: `/root/assetManagement/backups/`
- **Permissions**: `700` (owner only)
- **Naming Convention**: `backup_db_asset_YYYYMMDD_HHMMSS.sql`
- **Max Size Limit**: 1000 MB (configurable)
- **Retention**: 30 days (configurable)

### Backup Types

#### 1. SQL Backup (Primary Method)
- **Format**: MySQL dump (.sql)
- **Contains**: Complete database structure + data
- **Best For**: Full restoration
- **Command**: `mysqldump -h localhost -u root -p db_asset > backup.sql`

#### 2. Excel Backup
- **Format**: XLSX spreadsheet
- **Contains**: All tables as separate sheets
- **Best For**: Data analysis and reporting
- **Route**: `/export/all` with `format=excel`

#### 3. CSV Backup
- **Format**: ZIP archive with CSV files
- **Contains**: One CSV per table
- **Best For**: Data portability
- **Route**: `/export/all` with `format=csv`

## Database Operations

### Backup Operations

#### Create SQL Backup
```bash
# Via Web Interface:
Navigate to: Setup/Configuration → Backup/Restore → Download SQL

# Via Command Line:
mysqldump -u root -p'8.RvT2qhPC#VQkrd' db_asset > /root/assetManagement/backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Restore from Backup
```bash
# Via Web Interface:
Navigate to: Setup/Configuration → Backup/Restore → Upload SQL file

# Via Command Line:
mysql -u root -p'8.RvT2qhPC#VQkrd' db_asset < /path/to/backup.sql
```

### Maintenance Operations

#### Optimize Tables
```bash
# Via Web Interface:
Navigate to: Setup/Configuration → Backup/Restore → Database Maintenance → Optimize Now

# Via Command Line:
mysql -u root -p'8.RvT2qhPC#VQkrd' db_asset -e "OPTIMIZE TABLE table_name;"
```

#### Check Table Integrity
```bash
# Via Web Interface:
Navigate to: Setup/Configuration → Backup/Restore → Database Maintenance → Check Now

# Via Command Line:
mysql -u root -p'8.RvT2qhPC#VQkrd' db_asset -e "CHECK TABLE table_name;"
```

#### Repair Tables
```bash
# Via Web Interface:
Navigate to: Setup/Configuration → Backup/Restore → Database Maintenance → Repair Now

# Via Command Line:
mysql -u root -p'8.RvT2qhPC#VQkrd' db_asset -e "REPAIR TABLE table_name;"
```

## Access Configuration

### Database Connection
The application uses connection pooling with the following configuration:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "user_asset",
    "password": environ['DB_PASSWORD'],
    "database": "db_asset",
    "port": 3306
}
```

### Admin Operations
Backup/restore operations require **Admin group** membership:
- Route decorator: `@require_group('Admin')`
- CSRF protection enabled
- All operations logged in `backup_history`

## Web Interface Routes

| Route | Method | Access | Function |
|-------|--------|--------|----------|
| `/backup-restore` | GET | Admin | Main backup/restore interface |
| `/backup/sql` | POST | Admin | Create SQL backup |
| `/restore/sql` | POST | Admin | Restore from SQL backup |
| `/database/optimize` | POST | Admin | Optimize all tables |
| `/database/check` | POST | Admin | Check table integrity |
| `/database/repair` | POST | Admin | Repair tables |
| `/database/settings` | POST | Admin | Update database settings |
| `/export/all` | POST | Admin | Export all data (Excel/CSV) |

## Database Monitoring

### Real-Time Statistics
Available on backup/restore page:
- Database Name
- Database Type (MySQL)
- Total Size (in MB)
- Total Tables Count
- Host and User information

### Backup History
View last 10 backup operations:
- Date/Time of operation
- Backup type (SQL, Excel, CSV, RESTORE)
- Filename
- File size (in MB)
- Created by (username)
- Status (completed/failed)

## Security Features

### Access Control
- ✅ Admin-only access to all backup/restore functions
- ✅ CSRF token validation on all POST requests
- ✅ Secure filename handling (werkzeug)
- ✅ File type validation
- ✅ File size limits enforced
- ✅ Confirmation dialogs for destructive operations

### Audit Trail
All operations logged with:
- Operation type
- Timestamp
- Username
- File details
- Status and notes

### Password Security
- Database passwords stored as environment variables
- No hardcoded credentials in source code
- Production mode requires environment variables
- Debug mode uses safe defaults

## Maintenance Schedule

### Recommended Schedule
```
Daily:
- Automatic backup (if enabled)
- Monitor backup logs

Weekly:
- Manual backup verification
- Run OPTIMIZE TABLE on all tables
- Check disk space in backup directory

Monthly:
- Run CHECK TABLE on all tables
- Review and clean old backups
- Verify restore procedures

Quarterly:
- Test full restore process
- Review and update backup retention
- Update documentation
```

### Disk Space Management
Monitor backup directory:
```bash
du -sh /root/assetManagement/backups/
df -h /root/assetManagement/
```

Clean old backups:
```bash
# Remove backups older than 30 days
find /root/assetManagement/backups/ -name "backup_*.sql" -mtime +30 -delete
```

## Troubleshooting

### Common Issues

#### 1. Backup Fails
**Problem**: mysqldump command fails
**Solutions**:
- Check MySQL is running: `systemctl status mysql`
- Verify credentials in config
- Check disk space: `df -h`
- Review permissions on backup directory

#### 2. Restore Fails
**Problem**: mysql import fails
**Solutions**:
- Verify backup file is valid SQL
- Check file size not corrupted
- Ensure sufficient disk space
- Review MySQL error log: `/var/log/mysql/error.log`

#### 3. Permission Denied
**Problem**: Cannot write to backup directory
**Solutions**:
```bash
sudo chown -R root:root /root/assetManagement/backups/
sudo chmod 700 /root/assetManagement/backups/
```

#### 4. Connection Timeout
**Problem**: Database connection timeout
**Solutions**:
- Increase timeout in config: `"connection_timeout": 60`
- Check MySQL max_connections
- Review connection pool size

### Debug Mode
Enable debug logging:
```bash
export FLASK_DEBUG=true
export ENABLE_QUERY_LOGGING=true
tail -f /root/assetManagement/app.log
```

## Performance Optimization

### Query Optimization
- Regular OPTIMIZE TABLE operations
- Index management
- Query caching enabled
- Connection pooling (10 connections)

### Backup Optimization
- Compress backups: `gzip backup.sql`
- Incremental backups (future feature)
- Parallel table dumps (future feature)
- Cloud storage integration (future feature)

## Backup Best Practices

1. **Regular Backups**: Enable automatic daily backups
2. **Offsite Storage**: Copy backups to external location
3. **Test Restores**: Verify backups work regularly
4. **Multiple Versions**: Keep 7-30 days of backups
5. **Monitor Size**: Watch backup file sizes for anomalies
6. **Document Changes**: Note major updates before backing up
7. **Secure Storage**: Protect backup files (700 permissions)
8. **Verify Integrity**: Check backup files after creation

## Future Enhancements

- [ ] Automated scheduled backups (cron integration)
- [ ] Cloud storage integration (S3, Google Drive)
- [ ] Backup compression (gzip)
- [ ] Incremental backups
- [ ] Email notifications
- [ ] Backup encryption
- [ ] Selective table restore
- [ ] Backup comparison tools
- [ ] Performance metrics dashboard
- [ ] Multi-database support

## Support and Documentation

### Related Documentation
- `BACKUP_RESTORE_DOCUMENTATION.md` - Detailed backup/restore guide
- `README.md` - General system documentation
- `DEPLOYMENT.md` - Deployment instructions

### Getting Help
1. Check this documentation
2. Review application logs: `tail -f /root/assetManagement/app.log`
3. Check MySQL logs: `sudo tail -f /var/log/mysql/error.log`
4. Contact system administrator

---

**Last Updated**: November 3, 2025  
**Version**: 1.0  
**Status**: ✅ Fully Configured and Operational
