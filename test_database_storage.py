#!/usr/bin/env python3
"""
Test script to verify database can store and retrieve all asset data including images
"""

import sys
sys.path.insert(0, '/home/assetManagement/src')

from AssetManagement import InventorySystem
import mysql.connector

def test_database_storage():
    """Test complete database storage functionality"""
    print("="*70)
    print("DATABASE STORAGE TEST")
    print("="*70)
    
    # Initialize system
    print("\n1. Initializing Inventory System...")
    try:
        system = InventorySystem()
        print("   ✅ System initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test database connection
    print("\n2. Testing database connection...")
    try:
        system.cursor.execute("SELECT VERSION()")
        version = system.cursor.fetchone()
        print(f"   ✅ Connected to MySQL/MariaDB version: {version[0]}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Check inventory table structure
    print("\n3. Verifying inventory table structure...")
    try:
        system.cursor.execute("DESCRIBE inventory")
        columns = system.cursor.fetchall()
        column_names = [col[0] for col in columns]
        print(f"   ✅ Found {len(columns)} columns in inventory table")
        
        required_columns = ['name', 'quantity', 'price', 'description', 'category', 
                          'supplier', 'department', 'location', 'model', 'brand',
                          'serial_number', 'purchase_date', 'depreciation_method',
                          'useful_life_years', 'salvage_value', 'responsible_officer',
                          'province_name', 'island', 'unit_section', 'asset_category',
                          'lpo_number', 'asset_condition', 'asset_tag',
                          'image_1', 'image_2', 'image_3', 'image_4', 'image_5']
        
        missing = [col for col in required_columns if col not in column_names]
        if missing:
            print(f"   ⚠️  Missing columns: {', '.join(missing)}")
        else:
            print("   ✅ All required columns present")
            
    except Exception as e:
        print(f"   ❌ Error checking structure: {e}")
        return False
    
    # Test data insertion with all fields
    print("\n4. Testing data insertion...")
    test_asset_name = "TEST_DATABASE_ASSET_001"
    
    # Clean up any existing test data
    try:
        system.cursor.execute("DELETE FROM inventory WHERE name = %s", (test_asset_name,))
        system.conn.commit()
    except:
        pass
    
    try:
        system.add_item(
            name=test_asset_name,
            quantity=10,
            price=1500.50,
            description="Test asset for database verification",
            low_stock_threshold=5,
            category="Electronics",
            supplier="Unknown",
            department="IT Department",
            funding_source="Budget 2026",
            location="Building A",
            model="Model X-2000",
            brand="TestBrand",
            serial_number="SN-TEST-123456",
            purchase_date="2026-02-11",
            depreciation_method="straight_line",
            useful_life_years=5,
            salvage_value=150.00,
            responsible_officer="John Doe",
            province_name="Shefa",
            island="Efate",
            unit_section="IT Section",
            asset_category="Computer & IT",
            lpo_number="LPO-2026-001",
            asset_condition="Excellent",
            asset_tag="ASSET-TEST-001",
            image_1="/uploads/assets/test_image_1.jpg",
            image_2="/uploads/assets/test_image_2.jpg",
            image_3=None,
            image_4=None,
            image_5=None
        )
        print(f"   ✅ Successfully inserted test asset: {test_asset_name}")
    except Exception as e:
        print(f"   ❌ Insertion failed: {e}")
        return False
    
    # Verify data retrieval
    print("\n5. Verifying data retrieval...")
    try:
        system.cursor.execute("""
            SELECT name, quantity, price, department, location, model, brand, 
                   serial_number, responsible_officer, province_name, island,
                   asset_category, lpo_number, asset_condition, asset_tag,
                   image_1, image_2
            FROM inventory WHERE name = %s
        """, (test_asset_name,))
        
        result = system.cursor.fetchone()
        if result:
            print(f"   ✅ Successfully retrieved data:")
            print(f"      - Name: {result[0]}")
            print(f"      - Quantity: {result[1]}")
            print(f"      - Price: {result[2]}")
            print(f"      - Department: {result[3]}")
            print(f"      - Location: {result[4]}")
            print(f"      - Model: {result[5]}")
            print(f"      - Brand: {result[6]}")
            print(f"      - Serial Number: {result[7]}")
            print(f"      - Responsible Officer: {result[8]}")
            print(f"      - Province: {result[9]}")
            print(f"      - Island: {result[10]}")
            print(f"      - Asset Category: {result[11]}")
            print(f"      - LPO Number: {result[12]}")
            print(f"      - Condition: {result[13]}")
            print(f"      - Asset Tag: {result[14]}")
            print(f"      - Image 1: {result[15]}")
            print(f"      - Image 2: {result[16]}")
        else:
            print(f"   ❌ Data not found after insertion")
            return False
    except Exception as e:
        print(f"   ❌ Retrieval failed: {e}")
        return False
    
    # Check total asset count
    print("\n6. Checking total assets in database...")
    try:
        system.cursor.execute("SELECT COUNT(*) FROM inventory")
        count = system.cursor.fetchone()[0]
        print(f"   ✅ Total assets in database: {count}")
    except Exception as e:
        print(f"   ❌ Count query failed: {e}")
    
    # Clean up test data
    print("\n7. Cleaning up test data...")
    try:
        system.cursor.execute("DELETE FROM inventory WHERE name = %s", (test_asset_name,))
        system.conn.commit()
        print(f"   ✅ Test data removed successfully")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")
    
    print("\n" + "="*70)
    print("✅ DATABASE TEST PASSED - All systems operational!")
    print("="*70)
    return True

if __name__ == "__main__":
    success = test_database_storage()
    sys.exit(0 if success else 1)
