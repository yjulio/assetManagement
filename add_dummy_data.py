#!/usr/bin/env python3
import mysql.connector
from datetime import datetime, timedelta
import random

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'user_asset',
    'password': '8.RvT2qhPC#VQkrd',
    'database': 'db_asset'
}

def add_dummy_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    print("Adding dummy data to database...")
    
    # 1. Add dummy users
    print("\n1. Adding users...")
    users = [
        ('john.doe', 'John Doe', 'john.doe@vbos.com', 'password123'),
        ('jane.smith', 'Jane Smith', 'jane.smith@vbos.com', 'password123'),
        ('bob.wilson', 'Bob Wilson', 'bob.wilson@vbos.com', 'password123'),
        ('alice.brown', 'Alice Brown', 'alice.brown@vbos.com', 'password123'),
        ('mike.johnson', 'Mike Johnson', 'mike.johnson@vbos.com', 'password123'),
    ]
    
    for username, name, email, password_hash in users:
        try:
            cursor.execute("""
                INSERT INTO users (username, name, email, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (username, name, email, password_hash))
            print(f"  ✓ Added user: {username}")
        except mysql.connector.IntegrityError:
            print(f"  - User {username} already exists")
    
    # 2. Add dummy suppliers
    print("\n2. Adding suppliers...")
    suppliers = [
        ('Tech Solutions Ltd', '555-0101', 'tech@solutions.com'),
        ('Office Pro Supplies', '555-0102', 'info@officepro.com'),
        ('Global IT Systems', '555-0103', 'sales@globalit.com'),
        ('Furniture World', '555-0104', 'contact@furnitureworld.com'),
        ('Toyota Vanuatu', '555-0105', 'sales@toyota.vu'),
    ]
    
    for name, contact, email in suppliers:
        try:
            cursor.execute("""
                INSERT INTO suppliers (name, contact, email)
                VALUES (%s, %s, %s)
            """, (name, contact, email))
            print(f"  ✓ Added supplier: {name}")
        except mysql.connector.IntegrityError:
            print(f"  - Supplier {name} already exists")
    
    # 3. Add dummy inventory/assets
    print("\n3. Adding inventory items...")
    assets = [
        ('Dell Latitude 5520', 10, 1200.00, 'High-performance laptop', 5, 'Computer Equipment', 'Tech Solutions Ltd', 'IT', 'Head Office', 'Latitude 5520', 'Dell', 'DL2024001', datetime.now() - timedelta(days=90)),
        ('HP EliteBook 840', 8, 1100.00, 'Business laptop', 3, 'Computer Equipment', 'Tech Solutions Ltd', 'IT', 'Head Office', 'EliteBook 840', 'HP', 'HP2024001', datetime.now() - timedelta(days=60)),
        ('Office Desk', 20, 350.00, 'Adjustable office desk', 5, 'Furniture', 'Furniture World', 'Administration', 'Head Office', 'Bekant', 'IKEA', 'BK2024001', datetime.now() - timedelta(days=180)),
        ('Office Chair', 25, 800.00, 'Ergonomic chair', 5, 'Furniture', 'Furniture World', 'Administration', 'Head Office', 'Aeron', 'Herman Miller', 'HM2024001', datetime.now() - timedelta(days=180)),
        ('Cisco Router', 5, 450.00, 'Business router', 2, 'Network Equipment', 'Global IT Systems', 'IT', 'Head Office', 'RV340', 'Cisco', 'CS2024001', datetime.now() - timedelta(days=120)),
        ('iPhone 14 Pro', 15, 1200.00, 'Company phone', 5, 'Mobile Devices', 'Tech Solutions Ltd', 'IT', 'Head Office', 'iPhone 14 Pro', 'Apple', 'AP2024001', datetime.now() - timedelta(days=45)),
        ('Samsung Monitor 27"', 30, 400.00, '4K monitor', 10, 'Computer Equipment', 'Tech Solutions Ltd', 'IT', 'Head Office', '27" UHD', 'Samsung', 'SM2024001', datetime.now() - timedelta(days=75)),
        ('Toyota Hilux', 2, 35000.00, 'Company vehicle', 1, 'Vehicles', 'Toyota Vanuatu', 'Operations', 'Head Office', 'Hilux 2023', 'Toyota', 'TY2024001', datetime.now() - timedelta(days=365)),
        ('HP LaserJet Printer', 5, 650.00, 'Office printer', 2, 'Office Supplies', 'Office Pro Supplies', 'Administration', 'Port Vila Branch', 'LaserJet Pro', 'HP', 'HP2024002', datetime.now() - timedelta(days=150)),
        ('Microsoft Surface Pro', 6, 1400.00, 'Tablet laptop', 3, 'Computer Equipment', 'Tech Solutions Ltd', 'Finance', 'Head Office', 'Surface Pro 9', 'Microsoft', 'MS2024001', datetime.now() - timedelta(days=30)),
        ('Dell UltraSharp Monitor', 12, 550.00, '27" QHD monitor with USB-C', 5, 'Computer Equipment', 'Tech Solutions Ltd', 'IT', 'Head Office', 'U2723DE', 'Dell', 'DU2024001', datetime.now() - timedelta(days=20)),
        ('Logitech MX Master 3', 50, 99.00, 'Wireless mouse', 10, 'Computer Equipment', 'Office Pro Supplies', 'IT', 'Head Office', 'MX Master 3', 'Logitech', 'LG2024001', datetime.now() - timedelta(days=50)),
        ('Standing Desk Converter', 8, 280.00, 'Adjustable height desk converter', 3, 'Furniture', 'Furniture World', 'Administration', 'Head Office', 'VariDesk Pro', 'VariDesk', 'VD2024001', datetime.now() - timedelta(days=100)),
        ('Canon ImageRunner', 2, 2800.00, 'Multifunction copier/printer', 1, 'Office Supplies', 'Office Pro Supplies', 'Administration', 'Head Office', 'imageRUNNER ADVANCE', 'Canon', 'CN2024001', datetime.now() - timedelta(days=200)),
        ('Netgear ProSAFE Switch', 4, 320.00, '24-port Gigabit switch', 2, 'Network Equipment', 'Global IT Systems', 'IT', 'Port Vila Branch', 'GS724T', 'Netgear', 'NG2024001', datetime.now() - timedelta(days=110)),
    ]
    
    for name, qty, price, desc, threshold, category, supplier, dept, location, model, brand, serial, purchase_date in assets:
        try:
            cursor.execute("""
                INSERT INTO inventory (name, quantity, price, description, low_stock_threshold,
                                     category, supplier, department, location, model, brand,
                                     serial_number, purchase_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, qty, price, desc, threshold, category, supplier, dept, location, model, brand, serial, purchase_date))
            print(f"  ✓ Added item: {name}")
        except mysql.connector.IntegrityError:
            print(f"  - Item {name} already exists")
    
    # 4. Add some checkout records
    print("\n4. Adding checkout records...")
    checkouts = [
        ('Dell Latitude 5520', 'John Doe', 2, 'IT', 'Head Office', datetime.now() - timedelta(days=10)),
        ('HP EliteBook 840', 'Jane Smith', 1, 'Finance', 'Head Office', datetime.now() - timedelta(days=5)),
        ('iPhone 14 Pro', 'Bob Wilson', 1, 'Operations', 'Head Office', datetime.now() - timedelta(days=2)),
    ]
    
    for asset, person, qty, dept, loc, date in checkouts:
        try:
            cursor.execute("""
                INSERT INTO asset_transactions (asset_name, transaction_type, person, quantity, 
                                              department, location, transaction_date, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (asset, 'checkout', person, qty, dept, loc, date, 'Dummy checkout record'))
            print(f"  ✓ Added checkout: {asset} to {person}")
        except Exception as e:
            print(f"  - Checkout error: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Dummy data added successfully!")
    print("\nSummary:")
    print(f"  - {len(users)} users")
    print(f"  - {len(suppliers)} suppliers")
    print(f"  - {len(assets)} inventory items")
    print(f"  - {len(checkouts)} checkout records")

if __name__ == '__main__':
    try:
        add_dummy_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
