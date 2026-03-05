"""Database migration for mobile features
Creates tables for asset handovers and offline sync
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

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

def setup_mobile_features():
    """Set up tables for mobile features"""
    conn = create_connection()
    if not conn:
        print("Failed to connect to database!")
        return False
    
    print("Setting up mobile features...")
    
    # Asset handovers table
    if not check_table_exists(conn, 'asset_handovers'):
        print("Creating asset_handovers table...")
        execute_query(conn, """
            CREATE TABLE asset_handovers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asset_name VARCHAR(255) NOT NULL,
                recipient_name VARCHAR(255) NOT NULL,
                recipient_email VARCHAR(255),
                notes TEXT,
                signature_path VARCHAR(500),
                handed_over_by VARCHAR(100),
                handover_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status ENUM('pending', 'completed', 'returned') DEFAULT 'completed',
                return_date DATETIME NULL,
                INDEX idx_asset_name (asset_name),
                INDEX idx_handover_date (handover_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Asset photos metadata table
    if not check_table_exists(conn, 'asset_photos'):
        print("Creating asset_photos table...")
        execute_query(conn, """
            CREATE TABLE asset_photos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asset_name VARCHAR(255) NOT NULL,
                filename VARCHAR(500) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                uploaded_by VARCHAR(100),
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                is_primary BOOLEAN DEFAULT FALSE,
                INDEX idx_asset_name (asset_name),
                INDEX idx_upload_date (upload_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Asset documents metadata table
    if not check_table_exists(conn, 'asset_documents'):
        print("Creating asset_documents table...")
        execute_query(conn, """
            CREATE TABLE asset_documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asset_name VARCHAR(255) NOT NULL,
                document_type ENUM('invoice', 'warranty', 'manual', 'certificate', 'other') DEFAULT 'other',
                filename VARCHAR(500) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                uploaded_by VARCHAR(100),
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expiry_date DATE NULL,
                notes TEXT,
                INDEX idx_asset_name (asset_name),
                INDEX idx_document_type (document_type),
                INDEX idx_upload_date (upload_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # QR code tracking table
    if not check_table_exists(conn, 'qr_code_scans'):
        print("Creating qr_code_scans table...")
        execute_query(conn, """
            CREATE TABLE qr_code_scans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asset_name VARCHAR(255) NOT NULL,
                scanned_by VARCHAR(100),
                scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                scan_location VARCHAR(255),
                device_info VARCHAR(500),
                INDEX idx_asset_name (asset_name),
                INDEX idx_scan_date (scan_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    # Offline sync queue table
    if not check_table_exists(conn, 'offline_sync_queue'):
        print("Creating offline_sync_queue table...")
        execute_query(conn, """
            CREATE TABLE offline_sync_queue (
                id INT AUTO_INCREMENT PRIMARY KEY,
                action_type VARCHAR(50) NOT NULL,
                entity_type VARCHAR(50) NOT NULL,
                entity_id VARCHAR(255),
                data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME NULL,
                status ENUM('pending', 'synced', 'failed') DEFAULT 'pending',
                error_message TEXT,
                attempts INT DEFAULT 0,
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    print("Mobile features setup complete!")
    conn.close()
    return True

if __name__ == "__main__":
    success = setup_mobile_features()
    if success:
        print("\n✓ Mobile features database tables created successfully!")
        print("Features enabled:")
        print("  - QR Code scanning and generation")
        print("  - Asset photo galleries")
        print("  - Document uploads (invoices, warranties)")
        print("  - Digital signatures for handovers")
        print("  - Offline sync support")
    else:
        print("\n✗ Mobile features setup failed!")
        sys.exit(1)
