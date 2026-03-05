#!/usr/bin/env python3
"""Quick script to add asset fields"""
import mysql.connector
import os

# Get password
with open('/home/assetManagement/.env') as f:
    for line in f:
        if line.startswith('DB_PASSWORD='):
            password = line.split('=', 1)[1].strip()
            break

conn = mysql.connector.connect(
    host='localhost',
    user='user_asset',
    password=password,
    database='db_asset'
)

cursor = conn.cursor()

fields = [
    "ALTER TABLE inventory ADD COLUMN responsible_officer VARCHAR(255)",
    "ALTER TABLE inventory ADD COLUMN province_name VARCHAR(100)",
    "ALTER TABLE inventory ADD COLUMN island VARCHAR(100)",
    "ALTER TABLE inventory ADD COLUMN unit_section VARCHAR(255)",
    "ALTER TABLE inventory ADD COLUMN asset_category VARCHAR(255)",
    "ALTER TABLE inventory ADD COLUMN lpo_number VARCHAR(100)",
    "ALTER TABLE inventory ADD COLUMN asset_condition ENUM('Excellent','Good','Fair','Poor','Broken') DEFAULT 'Good'",
    "ALTER TABLE inventory ADD COLUMN asset_tag VARCHAR(100)",
    "ALTER TABLE inventory ADD COLUMN image_1 VARCHAR(500)",
    "ALTER TABLE inventory ADD COLUMN image_2 VARCHAR(500)",
    "ALTER TABLE inventory ADD COLUMN image_3 VARCHAR(500)",
    "ALTER TABLE inventory ADD COLUMN image_4 VARCHAR(500)",
    "ALTER TABLE inventory ADD COLUMN image_5 VARCHAR(500)"
]

for sql in fields:
    try:
        cursor.execute(sql)
        conn.commit()
        print(f"✓ {sql[:50]}...")
    except mysql.connector.Error as e:
        if e.errno != 1060:  # Duplicate column
            print(f"✗ Error: {e}")
        else:
            print(f"ℹ Column already exists")

cursor.close()
conn.close()
print("\nDone!")
