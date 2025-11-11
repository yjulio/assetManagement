"""
Database Utilities for Asset Management System
Provides helper functions for database operations, backup, restore, and maintenance.
"""

import subprocess
import os
import sys
from datetime import datetime

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, BACKUP_CONFIG


def get_database_info():
    """
    Get database information including size and table count.
    Returns dict with name, size, tables count.
    """
    import mysql.connector
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Get database size
        cursor.execute("""
            SELECT table_schema AS 'name', 
                   ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'size' 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            GROUP BY table_schema
        """, (DB_CONFIG['database'],))
        db_size = cursor.fetchone()
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, (DB_CONFIG['database'],))
        db_tables = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'name': DB_CONFIG['database'],
            'size': f"{db_size['size']} MB" if db_size else 'N/A',
            'tables': db_tables['count'] if db_tables else 'N/A',
            'host': DB_CONFIG['host'],
            'user': DB_CONFIG['user']
        }
    except Exception as e:
        return {
            'name': DB_CONFIG['database'],
            'size': 'Error',
            'tables': 'Error',
            'error': str(e)
        }


def create_sql_backup(username='System'):
    """
    Create a SQL backup of the database.
    Returns tuple: (success: bool, message: str, filepath: str or None, file_size: int or None)
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{DB_CONFIG['database']}_{timestamp}.sql"
        backup_dir = BACKUP_CONFIG['backup_dir']
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        filepath = os.path.join(backup_dir, filename)
        
        # Build mysqldump command
        cmd = [
            'mysqldump',
            f'-h{DB_CONFIG["host"]}',
            f'-u{DB_CONFIG["user"]}',
            f'-p{DB_CONFIG["password"]}',
            DB_CONFIG['database']
        ]
        
        # Execute mysqldump
        with open(filepath, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(filepath)
            size_mb = file_size / 1024 / 1024
            
            # Check size limit
            if size_mb > BACKUP_CONFIG['max_backup_size_mb']:
                message = f"Warning: Backup created but size ({size_mb:.2f} MB) exceeds recommended limit"
            else:
                message = f"Backup created successfully! Size: {size_mb:.2f} MB"
            
            return (True, message, filepath, file_size)
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            return (False, f"Backup failed: {error_msg}", None, None)
            
    except Exception as e:
        return (False, f"Backup error: {str(e)}", None, None)


def restore_sql_backup(filepath, username='System'):
    """
    Restore database from SQL backup file.
    Returns tuple: (success: bool, message: str)
    """
    try:
        # Verify file exists
        if not os.path.exists(filepath):
            return (False, "Backup file not found")
        
        # Verify file size
        file_size = os.path.getsize(filepath)
        max_size_bytes = BACKUP_CONFIG['max_backup_size_mb'] * 1024 * 1024
        if file_size > max_size_bytes:
            return (False, f"File too large! Maximum size: {BACKUP_CONFIG['max_backup_size_mb']} MB")
        
        # Build mysql command
        cmd = f'mysql -h {DB_CONFIG["host"]} -u {DB_CONFIG["user"]} -p"{DB_CONFIG["password"]}" {DB_CONFIG["database"]} < {filepath}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return (True, "Database restored successfully!")
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            return (False, f"Restore failed: {error_msg}")
            
    except Exception as e:
        return (False, f"Restore error: {str(e)}")


def optimize_database_tables():
    """
    Optimize all tables in the database.
    Returns tuple: (success: bool, message: str, optimized_count: int)
    """
    import mysql.connector
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        optimized_count = 0
        errors = []
        
        for table in tables:
            try:
                cursor.execute(f"OPTIMIZE TABLE `{table}`")
                optimized_count += 1
            except Exception as e:
                errors.append(f"{table}: {str(e)}")
        
        cursor.close()
        conn.close()
        
        if errors and optimized_count == 0:
            return (False, f"Optimization failed: {'; '.join(errors[:3])}", 0)
        elif errors:
            return (True, f"Optimized {optimized_count} tables with some errors", optimized_count)
        else:
            return (True, f"Successfully optimized {optimized_count} tables!", optimized_count)
            
    except Exception as e:
        return (False, f"Optimization error: {str(e)}", 0)


def check_database_tables():
    """
    Check integrity of all tables in the database.
    Returns tuple: (success: bool, message: str, checked_count: int, errors: list)
    """
    import mysql.connector
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        checked_count = 0
        errors = []
        
        for table in tables:
            try:
                cursor.execute(f"CHECK TABLE `{table}`")
                result = cursor.fetchone()
                if result and 'OK' in str(result):
                    checked_count += 1
                else:
                    errors.append(f"{table}: {result}")
            except Exception as e:
                errors.append(f"{table}: {str(e)}")
        
        cursor.close()
        conn.close()
        
        if errors:
            error_summary = ', '.join(errors[:5])
            return (True, f"Checked {checked_count} tables. Issues found in: {error_summary}", checked_count, errors)
        else:
            return (True, f"All {checked_count} tables passed integrity check!", checked_count, [])
            
    except Exception as e:
        return (False, f"Check error: {str(e)}", 0, [])


def repair_database_tables():
    """
    Repair all tables in the database.
    Returns tuple: (success: bool, message: str, repaired_count: int)
    """
    import mysql.connector
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        repaired_count = 0
        errors = []
        
        for table in tables:
            try:
                cursor.execute(f"REPAIR TABLE `{table}`")
                repaired_count += 1
            except Exception as e:
                errors.append(f"{table}: {str(e)}")
        
        cursor.close()
        conn.close()
        
        if errors and repaired_count == 0:
            return (False, f"Repair failed: {'; '.join(errors[:3])}", 0)
        elif errors:
            return (True, f"Repaired {repaired_count} tables with some errors", repaired_count)
        else:
            return (True, f"Successfully repaired {repaired_count} tables!", repaired_count)
            
    except Exception as e:
        return (False, f"Repair error: {str(e)}", 0)


def get_backup_settings():
    """
    Get backup settings from database.
    Returns dict with settings or default values.
    """
    import mysql.connector
    
    default_settings = {
        'auto_backup_enabled': 'false',
        'auto_backup_time': '02:00',
        'backup_retention_days': '30',
        'optimize_on_backup': 'true',
        'backup_location': BACKUP_CONFIG['backup_dir']
    }
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT setting_key, setting_value FROM database_settings')
        settings_raw = cursor.fetchall()
        settings = {s['setting_key']: s['setting_value'] for s in settings_raw}
        
        cursor.close()
        conn.close()
        
        return {**default_settings, **settings}
    except Exception:
        return default_settings


def update_backup_settings(settings_dict, username='System'):
    """
    Update backup settings in database.
    Returns tuple: (success: bool, message: str)
    """
    import mysql.connector
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for key, value in settings_dict.items():
            cursor.execute(
                'UPDATE database_settings SET setting_value = %s, updated_by = %s WHERE setting_key = %s',
                (value, username, key)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return (True, "Settings updated successfully!")
    except Exception as e:
        return (False, f"Settings update error: {str(e)}")


def log_backup_operation(backup_type, filename, file_size=None, username='System', status='completed', notes=None):
    """
    Log backup operation to backup_history table.
    Returns tuple: (success: bool, message: str)
    """
    import mysql.connector
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO backup_history 
            (backup_type, filename, file_size, created_by, status, notes) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (backup_type, filename, file_size, username, status, notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return (True, "Operation logged successfully")
    except Exception as e:
        return (False, f"Logging error: {str(e)}")
