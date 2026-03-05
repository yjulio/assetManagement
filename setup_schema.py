"""Database schema setup and migration script
Ensures all required tables exist for the asset management system
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from config import DB_CONFIG

def create_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query):
    """Execute a query"""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return False
    finally:
        cursor.close()

def check_table_exists(conn, table_name):
    """Check if a table exists"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()

def setup_database_schema():
    """Set up all required database tables"""
    conn = create_connection()
    if not conn:
        print("Failed to connect to database!")
        return False
    
    print("Setting up database schema...")
    
    # Dashboard configuration table
    if not check_table_exists(conn, 'dashboard_config'):
        print("Creating dashboard_config table...")
        execute_query(conn, """
            CREATE TABLE dashboard_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                widget_name VARCHAR(100) NOT NULL,
                is_enabled BOOLEAN DEFAULT TRUE,
                display_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY user_widget (user_id, widget_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Dashboard charts table
    if not check_table_exists(conn, 'dashboard_charts'):
        print("Creating dashboard_charts table...")
        execute_query(conn, """
            CREATE TABLE dashboard_charts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                chart_name VARCHAR(100) NOT NULL,
                is_enabled BOOLEAN DEFAULT TRUE,
                display_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY user_chart (user_id, chart_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Email configuration table
    if not check_table_exists(conn, 'email_config'):
        print("Creating email_config table...")
        execute_query(conn, """
            CREATE TABLE email_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender VARCHAR(255),
                password VARCHAR(255),
                smtp_server VARCHAR(255) DEFAULT 'smtp.gmail.com',
                port INT DEFAULT 587,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Database settings table
    if not check_table_exists(conn, 'database_settings'):
        print("Creating database_settings table...")
        execute_query(conn, """
            CREATE TABLE database_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(100) NOT NULL UNIQUE,
                setting_value TEXT,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Insert default database settings
        execute_query(conn, """
            INSERT INTO database_settings (setting_key, setting_value, description) VALUES
            ('auto_optimize', 'false', 'Automatically optimize tables'),
            ('backup_retention_days', '30', 'Days to retain backups'),
            ('max_query_time', '30', 'Maximum query execution time in seconds')
        """)
    
    # System settings table
    if not check_table_exists(conn, 'system_settings'):
        print("Creating system_settings table...")
        execute_query(conn, """
            CREATE TABLE system_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(100) NOT NULL UNIQUE,
                setting_value TEXT,
                updated_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Insert default system settings
        execute_query(conn, """
            INSERT INTO system_settings (setting_key, setting_value, updated_by) VALUES
            ('site_title', 'Department of Local Authorities', 'system'),
            ('site_subtitle', 'Asset Management System', 'system'),
            ('logo_path', '/static/asset.png', 'system'),
            ('favicon_path', '/static/asset.png', 'system')
        """)
    
    # Alerts/notifications table
    if not check_table_exists(conn, 'alerts'):
        print("Creating alerts table...")
        execute_query(conn, """
            CREATE TABLE alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                alert_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT,
                severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
                asset_id INT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_alert_type (alert_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Custom form fields table
    if not check_table_exists(conn, 'custom_form_fields'):
        print("Creating custom_form_fields table...")
        execute_query(conn, """
            CREATE TABLE custom_form_fields (
                id INT AUTO_INCREMENT PRIMARY KEY,
                form_name VARCHAR(100) NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                field_label VARCHAR(255) NOT NULL,
                field_type VARCHAR(50) NOT NULL,
                is_required BOOLEAN DEFAULT FALSE,
                is_enabled BOOLEAN DEFAULT TRUE,
                display_order INT DEFAULT 0,
                options TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY form_field (form_name, field_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    print("Database schema setup complete!")
    conn.close()
    return True

if __name__ == "__main__":
    success = setup_database_schema()
    if success:
        print("\n✓ Database schema successfully configured!")
        print("All required tables are now in place.")
    else:
        print("\n✗ Database schema setup failed!")
        print("Please check the error messages above.")
        sys.exit(1)
