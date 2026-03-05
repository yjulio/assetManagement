#!/usr/bin/env python3
"""
Database migration script to add new asset fields
Run from project root: python3 add_asset_fields_migration.py
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import DB_CONFIG
import mysql.connector

def add_column_if_not_exists(cursor, table, column, definition):
    """Add a column if it doesn't already exist"""
    try:
        # Check if column exists
        cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{column}'")
        result = cursor.fetchone()
        
        if not result:
            sql = f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            print(f"Adding column {column}...")
            cursor.execute(sql)
            print(f"  ✓ Column {column} added successfully")
            return True
        else:
            print(f"  ℹ Column {column} already exists, skipping...")
            return False
    except mysql.connector.Error as err:
        print(f"  ✗ Error adding column {column}: {err}")
        return False

def create_index_if_not_exists(cursor, table, index_name, column):
    """Create an index if it doesn't already exist"""
    try:
        # Check if index exists
        cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = '{index_name}'")
        result = cursor.fetchone()
        
        if not result:
            sql = f"CREATE INDEX {index_name} ON {table}({column})"
            print(f"Creating index {index_name}...")
            cursor.execute(sql)
            print(f"  ✓ Index {index_name} created successfully")
            return True
        else:
            print(f"  ℹ Index {index_name} already exists, skipping...")
            return False
    except mysql.connector.Error as err:
        print(f"  ✗ Error creating index {index_name}: {err}")
        return False

def main():
    print("=" * 60)
    print("Asset Management System - Database Migration")
    print("Adding new asset fields")
    print("=" * 60)
    
    # Connect to database
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        cursor = conn.cursor()
        print("\n✓ Connected to database successfully\n")
    except mysql.connector.Error as err:
        print(f"\n✗ Database connection failed: {err}")
        return 1
    
    # Define new columns to add
    columns_to_add = [
        ('responsible_officer', 'VARCHAR(255) DEFAULT NULL'),
        ('province_name', 'VARCHAR(100) DEFAULT NULL'),
        ('island', 'VARCHAR(100) DEFAULT NULL'),
        ('unit_section', 'VARCHAR(255) DEFAULT NULL'),
        ('asset_category', 'VARCHAR(255) DEFAULT NULL'),
        ('lpo_number', 'VARCHAR(100) DEFAULT NULL'),
        ('asset_condition', "ENUM('Excellent', 'Good', 'Fair', 'Poor', 'Broken') DEFAULT 'Good'"),
        ('asset_tag', 'VARCHAR(100) DEFAULT NULL'),
        ('image_1', 'VARCHAR(500) DEFAULT NULL'),
        ('image_2', 'VARCHAR(500) DEFAULT NULL'),
        ('image_3', 'VARCHAR(500) DEFAULT NULL'),
        ('image_4', 'VARCHAR(500) DEFAULT NULL'),
        ('image_5', 'VARCHAR(500) DEFAULT NULL'),
    ]
    
    # Add columns
    print("Adding columns to inventory table:")
    print("-" * 60)
    added_count = 0
    for column_name, definition in columns_to_add:
        if add_column_if_not_exists(cursor, 'inventory', column_name, definition):
            added_count += 1
        conn.commit()
    
    # Create indexes
    print("\n" + "=" * 60)
    print("Creating indexes:")
    print("-" * 60)
    indexes_to_create = [
        ('idx_asset_tag', 'asset_tag'),
        ('idx_lpo_number', 'lpo_number'),
        ('idx_responsible_officer', 'responsible_officer'),
        ('idx_asset_condition', 'asset_condition'),
    ]
    
    index_count = 0
    for index_name, column in indexes_to_create:
        if create_index_if_not_exists(cursor, 'inventory', index_name, column):
            index_count += 1
        conn.commit()
    
    # Show final table structure
    print("\n" + "=" * 60)
    print("Updated table structure:")
    print("-" * 60)
    cursor.execute("DESCRIBE inventory")
    for row in cursor.fetchall():
        field, type_, null, key, default, extra = row
        print(f"{field:25} {type_:30} {null:5} {key:5}")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"Migration completed successfully!")
    print(f"Columns added: {added_count}")
    print(f"Indexes created: {index_count}")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
