import mysql.connector
import sys
sys.path.insert(0, 'src')
from config import DB_CONFIG

print("Testing MySQL connection...")
print(f"Host: {DB_CONFIG['host']}")
print(f"User: {DB_CONFIG['user']}")
print(f"Database: {DB_CONFIG['database']}")

try:
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        connection_timeout=5
    )
    print("✓ Connected successfully!")
    conn.close()
except mysql.connector.Error as err:
    print(f"✗ Connection failed: {err}")
    sys.exit(1)
