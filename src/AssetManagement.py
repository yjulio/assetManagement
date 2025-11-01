# filepath: /inventory-management-system/inventory-management-system/src/AssetManagement.py

import mysql.connector
import csv
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
import getpass
from config import DB_CONFIG, EMAIL_CONFIG

class InventorySystem:
    def __init__(self):
        self.inventory = {}
        self.suppliers = {}
        self.groups = {}
        self.users = {}
        self.conn = self.create_connection()
        self.cursor = self.conn.cursor()
        self.email_config = EMAIL_CONFIG
        self._create_tables()
        self._load_suppliers()
        self._load_groups()
        self._load_users()
        self._load_inventory()

    def create_connection(self):
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            print("Connected to MySQL database.")
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            exit(1)

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                name VARCHAR(255) PRIMARY KEY,
                contact VARCHAR(255),
                email VARCHAR(255)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                name VARCHAR(255) PRIMARY KEY,
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) DEFAULT 0.0,
                description TEXT,
                low_stock_threshold INTEGER DEFAULT 5,
                category VARCHAR(255) DEFAULT 'Uncategorized',
                supplier VARCHAR(255),
                department VARCHAR(255) NULL,
                location VARCHAR(255) NULL,
                FOREIGN KEY (supplier) REFERENCES suppliers(name) ON DELETE SET NULL
            )
        ''')
        # Ensure department/location columns exist for older deployments
        try:
            self.cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'inventory'
            """)
            cols = {r[0] for r in self.cursor.fetchall()}
            alter_parts = []
            if 'department' not in cols:
                alter_parts.append('ADD COLUMN department VARCHAR(255) NULL')
            if 'location' not in cols:
                alter_parts.append('ADD COLUMN location VARCHAR(255) NULL')
            if 'model' not in cols:
                alter_parts.append('ADD COLUMN model VARCHAR(255) NULL')
            if 'brand' not in cols:
                alter_parts.append('ADD COLUMN brand VARCHAR(255) NULL')
            if 'serial_number' not in cols:
                alter_parts.append('ADD COLUMN serial_number VARCHAR(255) NULL')
            if 'purchase_date' not in cols:
                alter_parts.append('ADD COLUMN purchase_date DATE NULL')
            if 'depreciation_method' not in cols:
                alter_parts.append('ADD COLUMN depreciation_method VARCHAR(50) DEFAULT "straight_line"')
            if 'useful_life_years' not in cols:
                alter_parts.append('ADD COLUMN useful_life_years INT DEFAULT 5')
            if 'salvage_value' not in cols:
                alter_parts.append('ADD COLUMN salvage_value DECIMAL(10,2) DEFAULT 0.0')
            if alter_parts:
                self.cursor.execute('ALTER TABLE inventory ' + ', '.join(alter_parts))
        except Exception as _:
            pass
        # User / Group tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS `groups` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255),
                password_hash VARCHAR(255),
                name VARCHAR(255),
                profile_picture VARCHAR(255)
            )
        ''')
        # Ensure name and profile_picture columns exist for older deployments
        try:
            self.cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users'
            """)
            user_cols = {r[0] for r in self.cursor.fetchall()}
            user_alter_parts = []
            if 'name' not in user_cols:
                user_alter_parts.append('ADD COLUMN name VARCHAR(255) NULL')
            if 'profile_picture' not in user_cols:
                user_alter_parts.append('ADD COLUMN profile_picture VARCHAR(255) NULL')
            if user_alter_parts:
                self.cursor.execute('ALTER TABLE users ' + ', '.join(user_alter_parts))
        except Exception as _:
            pass
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_groups (
                user_id INT,
                group_id INT,
                PRIMARY KEY (user_id, group_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE
            )
        ''')
        # Transactions table for check-in and check-out
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(255) NOT NULL,
                action ENUM('checkout','checkin') NOT NULL,
                quantity INT NOT NULL,
                person VARCHAR(255),
                department VARCHAR(255),
                location VARCHAR(255),
                notes TEXT,
                username VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_name) REFERENCES inventory(name) ON DELETE CASCADE
            )
        ''')
        # Dashboard configuration tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                widget_name VARCHAR(100) NOT NULL,
                is_enabled BOOLEAN DEFAULT TRUE,
                display_order INT DEFAULT 0,
                UNIQUE KEY unique_user_widget (user_id, widget_name)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_charts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                chart_name VARCHAR(100) NOT NULL,
                is_enabled BOOLEAN DEFAULT TRUE,
                display_order INT DEFAULT 0,
                UNIQUE KEY unique_user_chart (user_id, chart_name)
            )
        ''')
        self.conn.commit()

    def _load_suppliers(self):
        self.cursor.execute("SELECT name, contact, email FROM suppliers")
        for row in self.cursor.fetchall():
            name, contact, email = row
            self.suppliers[name] = {'contact': contact or "", 'email': email or ""}

    def _load_groups(self):
        """Load groups from DB into self.groups (name -> {id, description})."""
        try:
            self.cursor.execute("SELECT id, name, description FROM `groups`")
            for row in self.cursor.fetchall():
                gid, name, desc = row
                self.groups[name] = {'id': gid, 'description': desc or ''}
        except Exception as e:
            # If the table doesn't exist or other DB error, keep groups empty
            print(f"Warning loading groups: {e}")

    def _load_users(self):
        """Load users and their group assignments into self.users."""
        try:
            self.cursor.execute("SELECT id, username, email, password_hash, name, profile_picture FROM users")
            for row in self.cursor.fetchall():
                uid, username, email, password_hash, name, profile_picture = row
                self.users[username] = {
                    'id': uid, 
                    'email': email or '', 
                    'password_hash': password_hash, 
                    'name': name or '',
                    'profile_picture': profile_picture or None,
                    'groups': set()
                }

            # load user_groups mappings
            self.cursor.execute("SELECT user_id, group_id FROM user_groups")
            for row in self.cursor.fetchall():
                user_id, group_id = row
                # find username and group name
                self.cursor.execute("SELECT username FROM users WHERE id=%s", (user_id,))
                urow = self.cursor.fetchone()
                if not urow:
                    continue
                uname = urow[0]
                self.cursor.execute("SELECT name FROM `groups` WHERE id=%s", (group_id,))
                grow = self.cursor.fetchone()
                if not grow:
                    continue
                gname = grow[0]
                if uname in self.users:
                    self.users[uname]['groups'].add(gname)
        except Exception as e:
            print(f"Warning loading users: {e}")

    def _load_inventory(self):
        self.cursor.execute("""
            SELECT name, quantity, price, description, low_stock_threshold, category, supplier, department, location,
                   model, brand, serial_number, purchase_date, depreciation_method, useful_life_years, salvage_value
            FROM inventory
        """)
        for row in self.cursor.fetchall():
            name, qty, price, desc, threshold, cat, sup, dept, loc, model, brand, serial_num, purchase_dt, dep_method, useful_life, salvage = row
            self.inventory[name] = {
                'quantity': qty,
                'price': float(price) if price is not None else 0.0,
                'description': desc or "",
                'low_stock_threshold': threshold or 5,
                'category': cat or "Uncategorized",
                'supplier': sup or "Unknown",
                'department': dept or None,
                'location': loc or None,
                'model': model or None,
                'brand': brand or None,
                'serial_number': serial_num or None,
                'purchase_date': purchase_dt or None,
                'depreciation_method': dep_method or 'straight_line',
                'useful_life_years': useful_life or 5,
                'salvage_value': float(salvage) if salvage is not None else 0.0
            }

    def add_supplier(self, name, contact="", email=""):
        if name in self.suppliers:
            print(f"Supplier '{name}' already exists.")
            return
        try:
            self.cursor.execute(
                "INSERT INTO suppliers (name, contact, email) VALUES (%s, %s, %s)",
                (name, contact, email)
            )
            self.conn.commit()
            self.suppliers[name] = {'contact': contact, 'email': email}
            print(f"Added supplier '{name}'.")
        except mysql.connector.Error as err:
            print(f"Error adding supplier: {err}")

    def add_group(self, name, description=""):
        """Add a user group (id, name, description). No-op if exists."""
        name = (name or '').strip()
        if not name:
            print("Group name required.")
            return
        if name in self.groups:
            print(f"Group '{name}' already exists.")
            return
        try:
            self.cursor.execute(
                "INSERT INTO `groups` (name, description) VALUES (%s, %s)",
                (name, description)
            )
            self.conn.commit()
            gid = self.cursor.lastrowid
            self.groups[name] = {'id': gid, 'description': description}
            print(f"Added group '{name}'.")
        except mysql.connector.Error as err:
            print(f"Error adding group: {err}")

    def view_groups(self):
        if not self.groups:
            print("No groups defined.")
            return
        print("Groups:")
        for name in sorted(self.groups.keys()):
            g = self.groups[name]
            print(f"- {name}: {g.get('description','')}")

    def add_user(self, username, email="", password_hash=None):
        """Create a user. Expects password_hash to be a hashed password string (or None)."""
        username = (username or '').strip()
        if not username:
            print("Username required.")
            return
        if username in self.users:
            print(f"User '{username}' already exists.")
            return
        try:
            self.cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            self.conn.commit()
            uid = self.cursor.lastrowid
            self.users[username] = {'id': uid, 'email': email, 'password_hash': password_hash, 'groups': set()}
            print(f"Added user '{username}'.")
        except mysql.connector.Error as err:
            print(f"Error adding user: {err}")

    def assign_user_to_group(self, username, group_name):
        """Assign an existing user to an existing group."""
        if username not in self.users:
            print(f"User '{username}' not found.")
            return
        if group_name not in self.groups:
            print(f"Group '{group_name}' not found.")
            return
        uid = self.users[username]['id']
        gid = self.groups[group_name]['id']
        try:
            self.cursor.execute("INSERT IGNORE INTO user_groups (user_id, group_id) VALUES (%s, %s)", (uid, gid))
            self.conn.commit()
            self.users[username]['groups'].add(group_name)
            print(f"Assigned user '{username}' to group '{group_name}'.")
        except mysql.connector.Error as err:
            print(f"Error assigning user to group: {err}")

    def view_users(self):
        if not self.users:
            print("No users created.")
            return
        print("Users:")
        for uname in sorted(self.users.keys()):
            u = self.users[uname]
            groups = ", ".join(sorted(u.get('groups', []))) or '-'
            print(f"- {uname}: {u.get('email','')} | Groups: {groups}")

    def view_suppliers(self):
        if not self.suppliers:
            print("No suppliers added.")
            return
        print("Suppliers:")
        for name in sorted(self.suppliers.keys()):
            s = self.suppliers[name]
            print(f"- {name}: Contact={s['contact']}, Email={s['email']}")

    def add_item(self, name, quantity, price=0.0, description="", low_stock_threshold=5, category="Uncategorized", supplier="Unknown", department=None, location=None, model=None, brand=None, serial_number=None, purchase_date=None, depreciation_method='straight_line', useful_life_years=5, salvage_value=0.0):
        if name in self.inventory:
            print(f"Item '{name}' already exists. Use update_quantity to adjust stock.")
            return

        if supplier != "Unknown" and supplier not in self.suppliers:
            print(f"Warning: Supplier '{supplier}' not in database. Adding as 'Unknown'.")
            supplier = "Unknown"

        try:
            self.cursor.execute("""
                INSERT INTO inventory 
                (name, quantity, price, description, low_stock_threshold, category, supplier, department, location,
                 model, brand, serial_number, purchase_date, depreciation_method, useful_life_years, salvage_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, quantity, price, description, low_stock_threshold, category, supplier, department, location,
                  model, brand, serial_number, purchase_date, depreciation_method, useful_life_years, salvage_value))
            self.conn.commit()

            self.inventory[name] = {
                'quantity': quantity,
                'price': price,
                'description': description,
                'low_stock_threshold': low_stock_threshold,
                'category': category,
                'supplier': supplier,
                'department': department,
                'location': location,
                'model': model,
                'brand': brand,
                'serial_number': serial_number,
                'purchase_date': purchase_date,
                'depreciation_method': depreciation_method,
                'useful_life_years': useful_life_years,
                'salvage_value': salvage_value
            }
            print(f"Added '{name}' (Category: {category}, Supplier: {supplier}).")
        except mysql.connector.Error as err:
            print(f"Error adding item: {err}")

    def remove_item(self, name):
        if name not in self.inventory:
            print(f"Item '{name}' not found.")
            return
        try:
            self.cursor.execute("DELETE FROM inventory WHERE name = %s", (name,))
            self.conn.commit()
            del self.inventory[name]
            print(f"Removed '{name}' from inventory.")
        except mysql.connector.Error as err:
            print(f"Error removing item: {err}")

    def update_quantity(self, name, quantity_change):
        if name not in self.inventory:
            print(f"Item '{name}' not found.")
            return
        new_quantity = self.inventory[name]['quantity'] + quantity_change
        if new_quantity < 0:
            new_quantity = 0
            print(f"Warning: Cannot go below 0. Set to 0.")

        self.inventory[name]['quantity'] = new_quantity
        try:
            self.cursor.execute("UPDATE inventory SET quantity = %s WHERE name = %s", (new_quantity, name))
            self.conn.commit()
            print(f"Updated '{name}' → {new_quantity} units.")
        except mysql.connector.Error as err:
            print(f"Error updating quantity: {err}")
            return

        if new_quantity < self.inventory[name]['low_stock_threshold']:
            msg = f"LOW STOCK: '{name}' has {new_quantity} left (threshold: {self.inventory[name]['low_stock_threshold']})."
            print(msg)
            if self.email_config.get('sender') and self.email_config.get('recipient'):
                self.send_email("Low Stock Alert", msg)

    # --- Check-out and Check-in helpers ---
    def checkout_item(self, name, quantity, username=None, person=None, department=None, location=None, notes=None):
        if name not in self.inventory:
            raise ValueError("Item not found")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        available = self.inventory[name]['quantity']
        if quantity > available:
            raise ValueError(f"Only {available} available to checkout")
        # Update quantity
        self.inventory[name]['quantity'] = available - quantity
        try:
            self.cursor.execute("UPDATE inventory SET quantity=%s WHERE name=%s", (available - quantity, name))
            # Log transaction
            self.cursor.execute(
                """
                INSERT INTO asset_transactions (item_name, action, quantity, person, department, location, notes, username)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (name, 'checkout', quantity, person, department, location, notes, username)
            )
            self.conn.commit()
        except mysql.connector.Error as err:
            # rollback memory cache
            self.inventory[name]['quantity'] = available
            raise err

    def checkin_item(self, name, quantity, username=None, person=None, notes=None):
        if name not in self.inventory:
            raise ValueError("Item not found")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        new_q = self.inventory[name]['quantity'] + quantity
        self.inventory[name]['quantity'] = new_q
        try:
            self.cursor.execute("UPDATE inventory SET quantity=%s WHERE name=%s", (new_q, name))
            self.cursor.execute(
                """
                INSERT INTO asset_transactions (item_name, action, quantity, person, notes, username)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (name, 'checkin', quantity, person, notes, username)
            )
            self.conn.commit()
        except mysql.connector.Error as err:
            # rollback memory cache
            self.inventory[name]['quantity'] = new_q - quantity
            raise err

    def search_item(self, name):
        item = self.inventory.get(name)
        if not item:
            print(f"Item '{name}' not found.")
            return None
        return item

    def view_inventory(self):
        if not self.inventory:
            print("Inventory is empty.")
            return

        grouped = defaultdict(list)
        for name, details in self.inventory.items():
            grouped[details['category']].append((name, details))

        print("\nCurrent Inventory (by Category):")
        for category in sorted(grouped.keys()):
            print(f"\n[{category}]")
            for name, d in sorted(grouped[category]):
                status = " [LOW]" if d['quantity'] < d['low_stock_threshold'] else ""
                print(f"  • {name}{status}: {d['quantity']} @ ${d['price']:.2f} | {d['description'] or '-'} | Supp: {d['supplier']}")

    def generate_report(self):
        total_items = len(self.inventory)
        total_stock = sum(d['quantity'] for d in self.inventory.values())
        total_value = sum(d['quantity'] * d['price'] for d in self.inventory.values())

        print(f"\n=== INVENTORY REPORT ===")
        print(f"Total Unique Items: {total_items}")
        print(f"Total Units in Stock: {total_stock}")
        print(f"Total Value: ${total_value:.2f}")

        cat_stats = defaultdict(lambda: {'items': 0, 'stock': 0, 'value': 0.0})
        for d in self.inventory.values():
            c = d['category']
            cat_stats[c]['items'] += 1
            cat_stats[c]['stock'] += d['quantity']
            cat_stats[c]['value'] += d['quantity'] * d['price']

        print("\nBy Category:")
        for c in sorted(cat_stats.keys()):
            s = cat_stats[c]
            print(f"  • {c}: {s['items']} items, {s['stock']} units, ${s['value']:.2f}")

        low = [n for n, d in self.inventory.items() if d['quantity'] < d['low_stock_threshold']]
        if low:
            print(f"\nLow Stock Alerts ({len(low)}):")
            for n in low:
                d = self.inventory[n]
                print(f"  • {n}: {d['quantity']} (threshold: {d['low_stock_threshold']})")

    def export_to_csv(self, filename='inventory_export.csv'):
        if not self.inventory:
            print("Nothing to export.")
            return
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'quantity', 'price', 'description', 'low_stock_threshold', 'category', 'supplier'])
                writer.writeheader()
                for name, d in sorted(self.inventory.items()):
                    row = {'name': name, **d}
                    row['price'] = f"{row['price']:.2f}"
                    writer.writerow(row)
            print(f"Exported to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

    def export_suppliers_to_csv(self, filename='suppliers_export.csv'):
        if not self.suppliers:
            print("No suppliers to export.")
            return
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'contact', 'email'])
                writer.writeheader()
                for name, d in sorted(self.suppliers.items()):
                    writer.writerow({'name': name, 'contact': d['contact'], 'email': d['email']})
            print(f"Suppliers exported to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

    def send_email(self, subject, body):
        if not all(self.email_config.get(k) for k in ['sender', 'password', 'recipient']):
            print("Email not fully configured.")
            return

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_config['sender']
        msg['To'] = self.email_config['recipient']

        try:
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['port']) as server:
                server.starttls()
                server.login(self.email_config['sender'], self.email_config['password'])
                server.send_message(msg)
            print("Email sent!")
        except Exception as e:
            print(f"Email failed: {e}")

    def run(self):
        print("Inventory Management System Started")
        while True:
            print("\n" + "="*40)
            print("1. Add Item         7. Add Supplier")
            print("2. Remove Item      8. View Suppliers")
            print("3. Update Qty       9. Export Inventory")
            print("4. Search Item     10. Export Suppliers")
            print("5. View Inventory  11. Exit")
            print("="*40)
            choice = input("Choose (1-11): ").strip()

            if choice == '1':
                name = input("Name: ")
                qty = int(input("Quantity: "))
                price = float(input("Price (0 for none): ") or 0)
                desc = input("Description: ")
                thresh = int(input("Low threshold [5]: ") or 5)
                cat = input("Category [Uncategorized]: ") or "Uncategorized"
                sup = input("Supplier [Unknown]: ") or "Unknown"
                if sup != "Unknown" and sup not in self.suppliers:
                    add = input(f"Add supplier '{sup}'? (y/n): ")
                    if add.lower() == 'y':
                        contact = input("Contact: ")
                        email = input("Email: ")
                        self.add_supplier(sup, contact, email)
                self.add_item(name, qty, price, desc, thresh, cat, sup)

            elif choice == '2':
                self.remove_item(input("Item to remove: "))
            elif choice == '3':
                name = input("Item: ")
                change = int(input("+/- quantity: "))
                self.update_quantity(name, change)
            elif choice == '4':
                item = self.search_item(input("Search item: "))
                if item:
                    print(item)
            elif choice == '5':
                self.view_inventory()
            elif choice == '6':
                self.generate_report()
            elif choice == '7':
                n = input("Supplier name: ")
                c = input("Contact: ")
                e = input("Email: ")
                self.add_supplier(n, c, e)
            elif choice == '8':
                self.view_suppliers()
            elif choice == '9':
                f = input("Filename [inventory_export.csv]: ") or "inventory_export.csv"
                self.export_to_csv(f)
            elif choice == '10':
                f = input("Filename [suppliers_export.csv]: ") or "suppliers_export.csv"
                self.export_suppliers_to_csv(f)
            elif choice == '11':
                print("Goodbye!")
                self.conn.close()
                break
            else:
                print("Invalid option.")

if __name__ == "__main__":
    system = InventorySystem()
    system.run()