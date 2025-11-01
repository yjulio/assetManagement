
 



 

from flask import Flask, request, redirect, url_for, flash, session, render_template
from AssetManagement import InventorySystem
from config import FLASK_CONFIG, DB_CONFIG
import html
import os
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error

try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:
    pd = None
    HAVE_PANDAS = False

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Database connection function
def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        raise

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = FLASK_CONFIG.get('secret_key', 'change_this_to_a_random_secret')
system = InventorySystem()
def calculate_depreciation(purchase_price, purchase_date_str, salvage_value, useful_life_years, method='straight_line'):
    """Calculate current asset value based on depreciation"""
    if not purchase_date_str or not purchase_price:
        return purchase_price
    
    try:
        if isinstance(purchase_date_str, date):
            purchase_date = purchase_date_str
        else:
            purchase_date = datetime.strptime(str(purchase_date_str), '%Y-%m-%d').date()
        
        today = date.today()
        years_owned = (today - purchase_date).days / 365.25
        
        if years_owned >= useful_life_years:
            return salvage_value
        
        depreciable_amount = purchase_price - salvage_value
        
        if method == 'straight_line':
            annual_depreciation = depreciable_amount / useful_life_years
            accumulated_depreciation = annual_depreciation * years_owned
            current_value = purchase_price - accumulated_depreciation
        elif method == 'declining_balance':
            rate = 2.0 / useful_life_years  # Double declining balance
            current_value = purchase_price * ((1 - rate) ** years_owned)
            current_value = max(current_value, salvage_value)
        else:
            current_value = purchase_price
        
        return max(current_value, salvage_value)
    except:
        return purchase_price

def header(title="Asset Management System"):
    # Deprecated: header content moved to Jinja templates. Kept for compatibility if referenced.
    return ""


def require_group(group_name):
    """Decorator to require that the logged-in user belongs to group_name."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            username = session.get('username')
            if not username:
                flash('Please log in to continue', 'warning')
                return redirect(url_for('login'))
            user = system.users.get(username)
            if not user:
                flash('Unknown user', 'error')
                return redirect(url_for('login'))
            if group_name not in user.get('groups', set()):
                flash('You do not have permission to perform this action', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Simple login-required decorator for routes that need authentication
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('username'):
            flash('Please log in to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    # Get search query
    search_query = request.args.get('q', '').lower()
    # Calculate dashboard metrics
    items = system.inventory
    if search_query:
        items = {k: v for k, v in items.items() if search_query in k.lower() or search_query in (v.get('category','').lower()) or search_query in (v.get('supplier','').lower())}
    
    # Get dashboard configuration from database or session
    user_id = session.get('username', 'default')
    dashboard_widgets = session.get('dashboard_widgets', ['total_assets', 'total_value', 'low_stock', 'categories'])
    dashboard_charts = session.get('dashboard_charts', [])
    
    # Try to load from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT widget_name FROM dashboard_config WHERE user_id = %s AND is_enabled = TRUE ORDER BY display_order",
            (user_id,)
        )
        db_widgets = [row[0] for row in cursor.fetchall()]
        if db_widgets:
            dashboard_widgets = db_widgets
            session['dashboard_widgets'] = dashboard_widgets
        
        cursor.execute(
            "SELECT chart_name FROM dashboard_charts WHERE user_id = %s AND is_enabled = TRUE ORDER BY display_order",
            (user_id,)
        )
        db_charts = [row[0] for row in cursor.fetchall()]
        if db_charts:
            dashboard_charts = db_charts
            session['dashboard_charts'] = dashboard_charts
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Dashboard config load error: {e}")
        # Use session defaults
    
    # Calculate all metrics
    total_items = len(items)
    total_value = sum(item['quantity'] * item['price'] for item in items.values())
    low_stock_items = sum(1 for item in items.values() if item['quantity'] <= 5)
    unique_categories = len(set(item['category'] for item in items.values()))
    total_suppliers = len(system.suppliers)
    checked_out = sum(1 for item in items.values() if item.get('checked_out', False))
    pending_maintenance = sum(1 for item in items.values() if item.get('maintenance_status') == 'pending')
    
    # Get recent activity (last 10 items)
    inventory_items = sorted([(name, type('Obj', (), d)) for name, d in items.items()], key=lambda x: x[0])
    recent_activity = inventory_items[:10] if 'recent_activity' in dashboard_widgets else []
    
    return render_template('index.html', 
                         title='Dashboard', 
                         total_items=total_items, 
                         total_value=total_value, 
                         low_stock_items=low_stock_items, 
                         unique_categories=unique_categories,
                         total_suppliers=total_suppliers,
                         checked_out=checked_out,
                         pending_maintenance=pending_maintenance,
                         inventory_items=inventory_items,
                         recent_activity=recent_activity,
                         dashboard_widgets=dashboard_widgets,
                         dashboard_charts=dashboard_charts)

@app.route("/add", methods=["GET", "POST"])
@require_group('Admin')
def add():
    if request.method == "POST":
        name = (request.form.get("name", "") or "").strip()
        quantity = int(request.form.get("quantity") or 0)
        price = float(request.form.get("price") or 0.0)
        description = request.form.get("description", "") or ""
        low_stock_threshold = int(request.form.get("low_stock_threshold") or 5)
        category = request.form.get("category", "Uncategorized") or "Uncategorized"
        supplier = request.form.get("supplier", "Unknown") or "Unknown"
        department = (request.form.get('department') or '').strip() or None
        location = (request.form.get('location') or '').strip() or None
        model = (request.form.get('model') or '').strip() or None
        brand = (request.form.get('brand') or '').strip() or None
        serial_number = (request.form.get('serial_number') or '').strip() or None
        purchase_date = (request.form.get('purchase_date') or '').strip() or None
        depreciation_method = request.form.get('depreciation_method', 'straight_line')
        useful_life_years = int(request.form.get('useful_life_years') or 5)
        salvage_value = float(request.form.get('salvage_value') or 0.0)
        if name:
            system.add_item(name, quantity, price, description, low_stock_threshold, category, supplier, 
                          department, location, model, brand, serial_number, purchase_date,
                          depreciation_method, useful_life_years, salvage_value)
            flash(f"Added item '{name}'.", 'success')
            return redirect(url_for('index'))
        else:
            flash('Name is required', 'error')
            return redirect(url_for('add'))
    return render_template('add.html', title='Add Asset', suppliers=sorted(system.suppliers.keys()))

@app.route("/update", methods=["GET", "POST"])
@require_group('Admin')
def update():
    if request.method == "POST":
        name = request.form.get("name","")
        change = int(request.form.get("change") or 0)
        system.update_quantity(name, change)
        return redirect(url_for("index"))
    return render_template('update.html', title='Update Quantity')

@app.route("/suppliers", methods=["GET", "POST"])
@require_group('Admin')
def suppliers():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        contact = request.form.get("contact","")
        email = request.form.get("email","")
        system.add_supplier(name, contact, email)
        return redirect(url_for("suppliers"))
    suppliers_list = sorted([(n, {'contact': s.get('contact',''), 'email': s.get('email','')}) for n, s in system.suppliers.items()], key=lambda x: x[0])
    # convert dicts into simple namespace-like for Jinja
    suppliers_ns = [(n, type('Obj', (), d)) for n, d in suppliers_list]
    return render_template('suppliers.html', title='Suppliers', suppliers=suppliers_ns)


@app.route("/groups", methods=["GET", "POST"])
def groups():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "")
        if name:
            # require admin to create groups
            username = session.get('username')
            if not username or 'Admin' not in system.users.get(username, {}).get('groups', set()):
                flash('Only Admins can create groups', 'error')
                return redirect(url_for('groups'))
            system.add_group(name, description)
        return redirect(url_for("groups"))
    groups_list = sorted([(n, {'description': g.get('description','')}) for n, g in system.groups.items()], key=lambda x: x[0])
    groups_ns = [(n, type('Obj', (), d)) for n, d in groups_list]
    return render_template('groups.html', title='Groups', groups=groups_ns)


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        if username:
            # require admin to create users
            username_session = session.get('username')
            if not username_session or 'Admin' not in system.users.get(username_session, {}).get('groups', set()):
                flash('Only Admins can create users', 'error')
                return redirect(url_for('users'))
            pw_hash = generate_password_hash(password) if password else None
            system.add_user(username, email, pw_hash)
        return redirect(url_for('users'))
    users_list = sorted([(uname, {'email': u.get('email',''), 'groups': u.get('groups', set())}) for uname, u in system.users.items()], key=lambda x: x[0])
    # For Jinja, groups can be set; Jinja can iterate sets but order may vary; acceptable for now
    users_ns = [(uname, type('Obj', (), d)) for uname, d in users_list]
    return render_template('users.html', title='Users', users=users_ns)


@app.route('/assign-group', methods=['GET', 'POST'])
@require_group('Admin')
def assign_group():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        group_name = request.form.get('group','').strip()
        if username and group_name:
            system.assign_user_to_group(username, group_name)
        return redirect(url_for('assign_group'))
    return render_template('assign_group.html', title='Assign Group', users=sorted(system.users.keys()), groups=sorted(system.groups.keys()))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = system.users.get(username)
        if not user:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        pw_hash = user.get('password_hash')
        if pw_hash and check_password_hash(pw_hash, password):
            session['username'] = username
            flash('Logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    # GET
    return render_template('login.html', title='Login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out', 'info')
    return redirect(url_for('index'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Profile routes ---
def get_current_user():
    username = session.get('username')
    if not username:
        return None
    user = system.users.get(username)
    if not user:
        return None
    # Add username, name, profile_picture, and groups for template
    return {
        'username': username,
        'name': user.get('name', ''),
        'email': user.get('email',''),
        'profile_picture': user.get('profile_picture', None),
        'groups': list(user.get('groups', set())),
        'created_at': user.get('created_at', None)
    }

@app.route('/profile')
def profile():
    user = get_current_user()
    if not user:
        flash('Please log in to view your profile', 'warning')
        return redirect(url_for('login'))
    return render_template('profile.html', title='My Profile', user=user)

@app.route('/change-profile', methods=['GET', 'POST'])
def change_profile():
    user = get_current_user()
    if not user:
        flash('Please log in to change your profile', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        # Update name in DB and cache
        system.users[user['username']]['name'] = name
        system.cursor.execute("UPDATE users SET name=%s WHERE username=%s", (name, user['username']))
        # Update email in DB and cache
        system.users[user['username']]['email'] = email
        system.cursor.execute("UPDATE users SET email=%s WHERE username=%s", (email, user['username']))
        # Update password if provided
        if password:
            from werkzeug.security import generate_password_hash
            pw_hash = generate_password_hash(password)
            system.users[user['username']]['password_hash'] = pw_hash
            system.cursor.execute("UPDATE users SET password_hash=%s WHERE username=%s", (pw_hash, user['username']))
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            pic = request.files['profile_picture']
            if pic and pic.filename:
                import os
                ext = os.path.splitext(pic.filename)[1].lower()
                if ext in ['.jpg','.jpeg','.png','.gif','.bmp']:
                    filename = f"profile_{user['username']}{ext}"
                    save_path = os.path.join(app.static_folder, filename)
                    pic.save(save_path)
                    url_path = f"/static/{filename}"
                    system.users[user['username']]['profile_picture'] = url_path
                    system.cursor.execute("UPDATE users SET profile_picture=%s WHERE username=%s", (url_path, user['username']))
        system.conn.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('profile'))
    return render_template('change_profile.html', title='Change Profile', user=user)

@app.route('/account-details')
def account_details():
    user = get_current_user()
    if not user:
        flash('Please log in to view account details', 'warning')
        return redirect(url_for('login'))
    return render_template('account_details.html', title='Account Details', user=user)


# ---- Assets submenu routes (placeholders) ----
@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        try:
            quantity = int(request.form.get('quantity') or 0)
        except Exception:
            quantity = 0
        person = (request.form.get('person') or '').strip() or None
        department = (request.form.get('department') or '').strip() or None
        location = (request.form.get('location') or '').strip() or None
        notes = (request.form.get('notes') or '').strip() or None
        if not name:
            flash('Item name is required', 'error')
            return redirect(url_for('checkout'))
        try:
            system.checkout_item(name, quantity, username=session.get('username'), person=person, department=department, location=location, notes=notes)
            flash(f"Checked out {quantity} of '{name}'", 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('checkout'))
    # GET
    return render_template('checkout.html', title='Check Out', items=sorted(system.inventory.keys()))

@app.route('/checkin', methods=['GET','POST'])
@login_required
def checkin():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        try:
            quantity = int(request.form.get('quantity') or 0)
        except Exception:
            quantity = 0
        person = (request.form.get('person') or '').strip() or None
        notes = (request.form.get('notes') or '').strip() or None
        if not name:
            flash('Item name is required', 'error')
            return redirect(url_for('checkin'))
        try:
            system.checkin_item(name, quantity, username=session.get('username'), person=person, notes=notes)
            flash(f"Checked in {quantity} of '{name}'", 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('checkin'))
    return render_template('checkin.html', title='Check In', items=sorted(system.inventory.keys()))

@app.route('/lease')
@login_required
def lease():
    return render_template('page.html', title='Lease', heading='Lease Asset', description='Create and manage asset leases.')

@app.route('/lease-return')
@login_required
def lease_return():
    return render_template('page.html', title='Lease Return', heading='Lease Return', description='Process the return of leased assets.')

@app.route('/dispose', methods=['GET', 'POST'])
@login_required
def dispose():
    if request.method == 'POST':
        asset_name = request.form.get('asset_name')
        quantity = int(request.form.get('quantity', 1))
        reason = request.form.get('reason', '')
        disposal_method = request.form.get('disposal_method', '')
        notes = request.form.get('notes', '')
        
        if asset_name and asset_name in system.inventory:
            asset = system.inventory[asset_name]
            
            if asset['quantity'] >= quantity:
                # Update quantity
                new_quantity = asset['quantity'] - quantity
                system.update_quantity(asset_name, new_quantity)
                
                # Record transaction
                cursor = system.conn.cursor()
                cursor.execute('''
                    INSERT INTO asset_transactions 
                    (asset_name, action, quantity, notes, user_id, person, department)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (asset_name, 'dispose', quantity, 
                      f"Reason: {reason} | Method: {disposal_method} | {notes}",
                      session.get('username'), 
                      f"Disposal - {disposal_method}",
                      reason))
                system.conn.commit()
                cursor.close()
                
                flash(f'Successfully disposed {quantity} unit(s) of {asset_name}', 'success')
                return redirect(url_for('dispose'))
            else:
                flash(f'Insufficient quantity. Only {asset["quantity"]} available.', 'error')
        else:
            flash('Asset not found', 'error')
    
    assets = [(name, data) for name, data in system.inventory.items()]
    assets.sort(key=lambda x: x[0])
    return render_template('dispose.html', assets=assets)

@app.route('/maintenance', methods=['GET', 'POST'])
@login_required
def maintenance():
    if request.method == 'POST':
        asset_name = request.form.get('asset_name')
        maintenance_type = request.form.get('maintenance_type')
        scheduled_date = request.form.get('scheduled_date')
        description = request.form.get('description', '')
        cost = float(request.form.get('cost', 0))
        notes = request.form.get('notes', '')
        
        if asset_name and asset_name in system.inventory:
            cursor = system.conn.cursor()
            cursor.execute('''
                INSERT INTO asset_transactions 
                (asset_name, action, quantity, notes, user_id, person, department)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (asset_name, 'maintenance', 1, 
                  f"Type: {maintenance_type} | Date: {scheduled_date} | Cost: VT{cost} | {description} | {notes}",
                  session.get('username'), 
                  maintenance_type,
                  f"Cost: VT{cost}"))
            system.conn.commit()
            cursor.close()
            
            flash(f'Maintenance scheduled for {asset_name}', 'success')
            return redirect(url_for('maintenance'))
        else:
            flash('Asset not found', 'error')
    
    assets = [(name, data) for name, data in system.inventory.items()]
    assets.sort(key=lambda x: x[0])
    return render_template('maintenance.html', assets=assets)

@app.route('/move', methods=['GET', 'POST'])
@login_required
def move():
    if request.method == 'POST':
        asset_name = request.form.get('asset_name')
        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')
        from_department = request.form.get('from_department')
        to_department = request.form.get('to_department')
        quantity = int(request.form.get('quantity', 1))
        notes = request.form.get('notes', '')
        
        if asset_name and asset_name in system.inventory:
            # Update asset location
            cursor = system.conn.cursor()
            cursor.execute('''
                UPDATE inventory 
                SET location = %s, department = %s
                WHERE name = %s
            ''', (to_location, to_department, asset_name))
            
            # Record transaction
            cursor.execute('''
                INSERT INTO asset_transactions 
                (asset_name, action, quantity, notes, user_id, person, location, department)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (asset_name, 'move', quantity, 
                  f"From: {from_location}/{from_department} → To: {to_location}/{to_department} | {notes}",
                  session.get('username'), 
                  f"Moved to {to_location}",
                  to_location,
                  to_department))
            system.conn.commit()
            cursor.close()
            
            # Update in-memory
            system.inventory[asset_name]['location'] = to_location
            system.inventory[asset_name]['department'] = to_department
            
            flash(f'Successfully moved {asset_name} to {to_location}', 'success')
            return redirect(url_for('move'))
        else:
            flash('Asset not found', 'error')
    
    assets = [(name, data) for name, data in system.inventory.items()]
    assets.sort(key=lambda x: x[0])
    return render_template('move.html', assets=assets)

@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    if request.method == 'POST':
        asset_name = request.form.get('asset_name')
        quantity = int(request.form.get('quantity', 1))
        reserved_by = request.form.get('reserved_by')
        reserved_for = request.form.get('reserved_for')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        notes = request.form.get('notes', '')
        
        if asset_name and asset_name in system.inventory:
            asset = system.inventory[asset_name]
            
            if asset['quantity'] >= quantity:
                cursor = system.conn.cursor()
                cursor.execute('''
                    INSERT INTO asset_transactions 
                    (asset_name, action, quantity, notes, user_id, person, department)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (asset_name, 'reserve', quantity, 
                      f"Reserved by: {reserved_by} | For: {reserved_for} | Period: {start_date} to {end_date} | {notes}",
                      session.get('username'), 
                      reserved_by,
                      reserved_for))
                system.conn.commit()
                cursor.close()
                
                flash(f'Successfully reserved {quantity} unit(s) of {asset_name}', 'success')
                return redirect(url_for('reserve'))
            else:
                flash(f'Insufficient quantity. Only {asset["quantity"]} available.', 'error')
        else:
            flash('Asset not found', 'error')
    
    assets = [(name, data) for name, data in system.inventory.items()]
    assets.sort(key=lambda x: x[0])
    return render_template('reserve.html', assets=assets)


# ---- Setup submenu routes ----
@app.route('/company-info')
@login_required
def company_info():
    return render_template('page.html', title='Company Info', heading='Company Information', description='Manage organization details and branding.')

@app.route('/locations')
@login_required
def locations():
    return render_template('page.html', title='Locations', heading='Locations', description='Manage locations where assets are stored or used.')

@app.route('/departments')
@login_required
def departments():
    return render_template('page.html', title='Departments', heading='Departments', description='Manage departments and organizational units.')

@app.route('/categories')
@login_required
def categories():
    return render_template('page.html', title='Categories', heading='Categories', description='Define asset categories to organize inventory.')

@app.route('/subcategories')
@login_required
def subcategories():
    return render_template('page.html', title='Subcategories', heading='Subcategories', description='Define asset subcategories for finer grouping.')

@app.route('/database')
@require_group('Admin')
def database():
    return render_template('page.html', title='Database', heading='Database', description='Backup, restore, and manage database settings.')

@app.route('/manage-dashboard', methods=['GET', 'POST'])
@login_required
def manage_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get selected widgets and charts from form
        selected_widgets = request.form.getlist('widget')
        selected_charts = request.form.getlist('chart')
        
        # Store in session for immediate use
        session['dashboard_widgets'] = selected_widgets
        session['dashboard_charts'] = selected_charts
        
        # Store in database for persistence
        user_id = session.get('username', 'default')
        
        try:
            # Delete existing configuration
            cursor.execute("DELETE FROM dashboard_config WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM dashboard_charts WHERE user_id = %s", (user_id,))
            
            # Insert new widget configuration
            for idx, widget in enumerate(selected_widgets):
                cursor.execute(
                    "INSERT INTO dashboard_config (user_id, widget_name, is_enabled, display_order) VALUES (%s, %s, %s, %s)",
                    (user_id, widget, True, idx)
                )
            
            # Insert new chart configuration
            for idx, chart in enumerate(selected_charts):
                cursor.execute(
                    "INSERT INTO dashboard_charts (user_id, chart_name, is_enabled, display_order) VALUES (%s, %s, %s, %s)",
                    (user_id, chart, True, idx)
                )
            
            conn.commit()
            flash(f'Dashboard configuration saved: {len(selected_widgets)} widgets, {len(selected_charts)} charts', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error saving dashboard configuration: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('manage_dashboard'))
    
    # Get current configuration from database
    user_id = session.get('username', 'default')
    current_widgets = []
    current_charts = []
    
    try:
        # Get widgets from database
        cursor.execute(
            "SELECT widget_name FROM dashboard_config WHERE user_id = %s AND is_enabled = TRUE ORDER BY display_order",
            (user_id,)
        )
        current_widgets = [row[0] for row in cursor.fetchall()]
        
        # Get charts from database
        cursor.execute(
            "SELECT chart_name FROM dashboard_charts WHERE user_id = %s AND is_enabled = TRUE ORDER BY display_order",
            (user_id,)
        )
        current_charts = [row[0] for row in cursor.fetchall()]
        
        # If no config in database, use defaults
        if not current_widgets:
            current_widgets = ['total_assets', 'total_value', 'low_stock', 'categories']
        if not current_charts:
            current_charts = []
            
        # Update session with database values
        session['dashboard_widgets'] = current_widgets
        session['dashboard_charts'] = current_charts
        
    except Exception as e:
        # Fallback to session or defaults
        current_widgets = session.get('dashboard_widgets', ['total_assets', 'total_value', 'low_stock', 'categories'])
        current_charts = session.get('dashboard_charts', [])
        flash(f'Using session configuration: {str(e)}', 'warning')
    finally:
        cursor.close()
        conn.close()
    
    return render_template('manage_dashboard.html', 
                         title='Manage Dashboard',
                         current_widgets=current_widgets,
                         current_charts=current_charts)


# ---- Advances submenu routes ----
@app.route('/contracts')
@login_required
def contracts():
    return render_template('page.html', title='Contracts/Licenses', heading='Contracts and Licenses', description='Track contracts, licenses, and renewal dates.')

@app.route('/employees')
@login_required
def employees():
    return render_template('page.html', title='Person/Employees', heading='People and Employees', description='Manage people and employee records associated with assets.')

@app.route('/customers')
@login_required
def customers():
    return render_template('page.html', title='Customers', heading='Customers', description='Manage customer records and assignments.')

@app.route('/funding')
@login_required
def funding():
    return render_template('page.html', title='Funding', heading='Funding', description='Track funding sources and budgets for assets.')


# ---- Customize forms ----
@app.route('/customize-assets-form')
@require_group('Admin')
def customize_assets_form():
    return render_template('page.html', title='Customize Assets Form', heading='Customize Assets Form', description='Configure fields and layout for the assets form.')

@app.route('/customize-customers-form')
@require_group('Admin')
def customize_customers_form():
    return render_template('page.html', title='Customize Customers Form', heading='Customize Customers Form', description='Configure fields and layout for the customers form.')

@app.route('/customize-maintenance-form')
@require_group('Admin')
def customize_maintenance_form():
    return render_template('page.html', title='Customize Maintenance Form', heading='Customize Maintenance Form', description='Configure fields and layout for the maintenance form.')

@app.route('/customize-contracts-form')
@require_group('Admin')
def customize_contracts_form():
    return render_template('page.html', title='Customize Contracts Form', heading='Customize Contracts Form', description='Configure fields and layout for the contracts form.')


@app.route('/import', methods=['GET', 'POST'])
@require_group('Admin')
def import_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            try:
                # Read CSV or Excel with fallback when pandas is not available
                if filename.lower().endswith('.csv'):
                    if HAVE_PANDAS:
                        df = pd.read_csv(filepath)
                        iterator = df.iterrows()
                    else:
                        import csv
                        with open(filepath, newline='', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                        iterator = enumerate(rows)
                else:
                    if not HAVE_PANDAS:
                        os.remove(filepath)
                        flash('Excel import requires pandas. Install pandas to import .xlsx files.', 'error')
                        return redirect(request.url)
                    df = pd.read_excel(filepath)
                    iterator = df.iterrows()

                for _, row in iterator:
                    # row can be a pandas Series or a dict
                    name = str(row.get('name', '')).strip()
                    if not name:
                        continue
                    qty = int(row.get('quantity', 0) or 0)
                    price = float(row.get('price', 0.0) or 0.0)
                    desc = str(row.get('description', '') or '')
                    thresh = int(row.get('low_stock_threshold', 5) or 5)
                    cat = str(row.get('category', 'Uncategorized') or 'Uncategorized')
                    sup = str(row.get('supplier', 'Unknown') or 'Unknown')
                    system.add_item(name, qty, price, desc, thresh, cat, sup)
                os.remove(filepath)
                flash('Import successful', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
                flash('Error processing file: ' + str(e), 'error')
                return redirect(request.url)
    return render_template('import.html', title='Import Data')



# --- Asset listing route ---
@app.route('/assets')
def assets():
    # Only allow logged-in users to view asset list
    if not session.get('username'):
        flash('Please log in to view assets', 'warning')
        return redirect(url_for('login'))
    
    # Add depreciation calculation to each asset
    assets_with_depreciation = []
    for name, d in system.inventory.items():
        asset_copy = dict(d)
        current_value = calculate_depreciation(
            d.get('price', 0),
            d.get('purchase_date'),
            d.get('salvage_value', 0),
            d.get('useful_life_years', 5),
            d.get('depreciation_method', 'straight_line')
        )
        asset_copy['current_value'] = current_value
        assets_with_depreciation.append((name, type('Obj', (), asset_copy)))
    
    assets_with_depreciation.sort(key=lambda x: x[0])
    return render_template('assets.html', title='Asset List', assets=assets_with_depreciation, calculate_depreciation=calculate_depreciation)


@app.route('/view-asset/<asset_name>')
@login_required
def view_asset(asset_name):
    if asset_name not in system.inventory:
        flash(f'Asset "{asset_name}" not found', 'error')
        return redirect(url_for('assets'))
    
    asset = system.inventory[asset_name]
    
    # Calculate current value if depreciation is enabled
    current_value = asset['price']
    depreciation_info = None
    
    if asset.get('depreciation_method') and asset['depreciation_method'] != 'none':
        current_value = calculate_depreciation(
            asset['price'],
            asset.get('purchase_date'),
            asset.get('salvage_value', 0),
            asset.get('useful_life_years', 5),
            asset['depreciation_method']
        )
        depreciation_amount = asset['price'] - current_value
        depreciation_percentage = (depreciation_amount / asset['price'] * 100) if asset['price'] > 0 else 0
        depreciation_info = {
            'amount': depreciation_amount,
            'percentage': depreciation_percentage,
            'current_value': current_value
        }
    
    return render_template('view_asset.html', 
                         asset_name=asset_name, 
                         asset=asset,
                         current_value=current_value,
                         depreciation_info=depreciation_info)


@app.route('/assign-asset/<asset_name>', methods=['GET', 'POST'])
@login_required
def assign_asset(asset_name):
    if asset_name not in system.inventory:
        flash(f'Asset "{asset_name}" not found', 'error')
        return redirect(url_for('assets'))
    
    asset = system.inventory[asset_name]
    
    if request.method == 'POST':
        person = request.form.get('person')
        department = request.form.get('department')
        location = request.form.get('location')
        notes = request.form.get('notes')
        
        # Update asset assignment
        cursor = system.conn.cursor()
        cursor.execute('''
            UPDATE inventory 
            SET department = %s, location = %s
            WHERE name = %s
        ''', (department, location, asset_name))
        
        # Record transaction
        cursor.execute('''
            INSERT INTO asset_transactions 
            (asset_name, action, quantity, person, department, location, notes, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (asset_name, 'assign', 1, person, department, location, notes, session.get('username')))
        
        system.conn.commit()
        cursor.close()
        
        # Update in-memory inventory
        system.inventory[asset_name]['department'] = department
        system.inventory[asset_name]['location'] = location
        
        flash(f'Asset "{asset_name}" successfully assigned to {person}', 'success')
        return redirect(url_for('assets'))
    
    return render_template('assign_asset.html', asset_name=asset_name, asset=asset)


@app.route('/edit-asset/<asset_name>', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_name):
    if asset_name not in system.inventory:
        flash(f'Asset "{asset_name}" not found', 'error')
        return redirect(url_for('assets'))
    
    if request.method == 'POST':
        try:
            # Get form data
            quantity = int(request.form.get('quantity', 0))
            price = float(request.form.get('price', 0.0))
            description = request.form.get('description', '')
            low_stock_threshold = int(request.form.get('low_stock_threshold', 5))
            category = request.form.get('category', 'Uncategorized')
            supplier = request.form.get('supplier', 'Unknown')
            department = request.form.get('department', '')
            location = request.form.get('location', '')
            model = request.form.get('model', '')
            brand = request.form.get('brand', '')
            serial_number = request.form.get('serial_number', '')
            purchase_date = request.form.get('purchase_date', '')
            depreciation_method = request.form.get('depreciation_method', 'straight_line')
            useful_life_years = int(request.form.get('useful_life_years') or 5)
            salvage_value = float(request.form.get('salvage_value') or 0.0)
            
            # Update in memory
            system.inventory[asset_name].update({
                'quantity': quantity,
                'price': price,
                'description': description,
                'low_stock_threshold': low_stock_threshold,
                'category': category,
                'supplier': supplier,
                'department': department if department else None,
                'location': location if location else None,
                'model': model if model else None,
                'brand': brand if brand else None,
                'serial_number': serial_number if serial_number else None,
                'purchase_date': purchase_date if purchase_date else None,
                'depreciation_method': depreciation_method,
                'useful_life_years': useful_life_years,
                'salvage_value': salvage_value
            })
            
            # Update in database
            system.cursor.execute("""
                UPDATE inventory 
                SET quantity=%s, price=%s, description=%s, low_stock_threshold=%s, 
                    category=%s, supplier=%s, department=%s, location=%s,
                    model=%s, brand=%s, serial_number=%s, purchase_date=%s,
                    depreciation_method=%s, useful_life_years=%s, salvage_value=%s
                WHERE name=%s
            """, (quantity, price, description, low_stock_threshold, category, supplier, 
                  department if department else None, location if location else None,
                  model if model else None, brand if brand else None, 
                  serial_number if serial_number else None, purchase_date if purchase_date else None,
                  depreciation_method, useful_life_years, salvage_value,
                  asset_name))
            system.conn.commit()
            
            flash(f'Asset "{asset_name}" updated successfully', 'success')
            return redirect(url_for('assets'))
        except Exception as e:
            flash(f'Error updating asset: {str(e)}', 'error')
    
    # GET request - show edit form
    asset_data = system.inventory[asset_name]
    suppliers = sorted(system.suppliers.keys())
    return render_template('edit_asset.html', title='Edit Asset', asset_name=asset_name, 
                         asset=asset_data, suppliers=suppliers)


@app.route('/delete-asset/<asset_name>', methods=['POST'])
@login_required
def delete_asset(asset_name):
    try:
        system.remove_item(asset_name)
        flash(f'Asset "{asset_name}" has been deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting asset: {str(e)}', 'error')
    return redirect(url_for('assets'))


@app.route('/delete-selected-assets', methods=['POST'])
@login_required
def delete_selected_assets():
    selected_assets = request.form.getlist('selected_assets')
    if not selected_assets:
        flash('No assets selected', 'warning')
        return redirect(url_for('assets'))
    
    deleted_count = 0
    errors = []
    
    for asset_name in selected_assets:
        try:
            system.remove_item(asset_name)
            deleted_count += 1
        except Exception as e:
            errors.append(f'{asset_name}: {str(e)}')
    
    if deleted_count > 0:
        flash(f'Successfully deleted {deleted_count} asset(s)', 'success')
    
    if errors:
        flash(f'Errors: {"; ".join(errors)}', 'error')
    
    return redirect(url_for('assets'))


# --- Document Gallery ---
@app.route('/document-gallery')
@login_required
def document_gallery():
    return render_template('document_gallery.html', title='Document Gallery')


# --- Image Gallery ---
@app.route('/image-gallery')
@login_required
def image_gallery():
    return render_template('image_gallery.html', title='Image Gallery')


# --- Lists Routes ---
@app.route('/lists/assets')
@login_required
def lists_assets():
    assets = sorted([(name, type('Obj', (), d)) for name, d in system.inventory.items()], key=lambda x: x[0])
    return render_template('lists_assets.html', title='Lists of Assets', assets=assets)


@app.route('/lists/maintenances')
@login_required
def lists_maintenances():
    # Get all maintenance records from the system
    maintenances = []
    return render_template('lists_maintenances.html', title='Lists of Maintenances', maintenances=maintenances)


@app.route('/lists/contracts')
@login_required
def lists_contracts():
    # Get all contract records from the system
    contracts = []
    return render_template('lists_contracts.html', title='Lists of Contracts', contracts=contracts)


# --- Reports Routes ---
@app.route('/reports/automated')
@login_required
def report_automated():
    # Generate automated report with key metrics
    metrics = {
        'total_assets': len(system.inventory),
        'total_quantity': sum(d['quantity'] for d in system.inventory.values()),
        'total_value': sum(d.get('price', 0) * d['quantity'] for d in system.inventory.values()),
        'low_stock_count': sum(1 for d in system.inventory.values() if d['quantity'] <= d.get('low_stock_threshold', 5))
    }
    
    # Get recent transactions
    try:
        system.cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM asset_transactions
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY action
        """)
        recent_activity = system.cursor.fetchall()
    except:
        recent_activity = []
    
    # Category breakdown
    category_stats = {}
    for name, d in system.inventory.items():
        cat = d.get('category', 'Uncategorized')
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'quantity': 0, 'value': 0}
        category_stats[cat]['count'] += 1
        category_stats[cat]['quantity'] += d['quantity']
        category_stats[cat]['value'] += d.get('price', 0) * d['quantity']
    
    # Top assets by value
    top_assets = []
    for name, d in system.inventory.items():
        value = d.get('price', 0) * d['quantity']
        top_assets.append({'name': name, 'value': value, 'quantity': d['quantity']})
    top_assets.sort(key=lambda x: x['value'], reverse=True)
    top_assets = top_assets[:10]
    
    return render_template('report_automated.html', 
                         title='Automated Report',
                         metrics=metrics,
                         recent_activity=recent_activity,
                         category_stats=category_stats,
                         top_assets=top_assets)


@app.route('/reports/custom', methods=['GET', 'POST'])
@login_required
def report_custom():
    categories = sorted(set(d.get('category', 'Uncategorized') for d in system.inventory.values()))
    
    if request.method == 'POST':
        # Handle custom report generation
        report_name = request.form.get('report_name')
        flash(f'Custom report "{report_name}" generated successfully', 'success')
    
    return render_template('report_custom.html', title='Custom Report', categories=categories)


@app.route('/reports/inventory')
@login_required
def report_inventory():
    assets_with_values = []
    for name, d in system.inventory.items():
        asset_copy = dict(d)
        current_value = calculate_depreciation(
            d.get('price', 0),
            d.get('purchase_date'),
            d.get('salvage_value', 0),
            d.get('useful_life_years', 5),
            d.get('depreciation_method', 'straight_line')
        )
        asset_copy['current_value'] = current_value
        asset_copy['total_value'] = current_value * d.get('quantity', 0)
        assets_with_values.append((name, asset_copy))
    
    assets_with_values.sort(key=lambda x: x[0])
    total_items = len(assets_with_values)
    total_units = sum(d['quantity'] for _, d in assets_with_values)
    total_value = sum(d['total_value'] for _, d in assets_with_values)
    
    return render_template('report_inventory.html', title='Inventory Report', 
                         assets=assets_with_values, total_items=total_items,
                         total_units=total_units, total_value=total_value)


@app.route('/reports/asset')
@login_required
def report_asset():
    assets_detailed = []
    for name, d in system.inventory.items():
        asset_copy = dict(d)
        current_value = calculate_depreciation(
            d.get('price', 0),
            d.get('purchase_date'),
            d.get('salvage_value', 0),
            d.get('useful_life_years', 5),
            d.get('depreciation_method', 'straight_line')
        )
        asset_copy['current_value'] = current_value
        assets_detailed.append((name, asset_copy))
    
    assets_detailed.sort(key=lambda x: x[0])
    return render_template('report_asset.html', title='Asset Report', assets=assets_detailed)


@app.route('/reports/audit')
@login_required
def report_audit():
    # Audit report: Check for data integrity issues
    audit_findings = []
    
    # Check for negative quantities
    negative_qty = [(name, data['quantity']) for name, data in system.inventory.items() if data['quantity'] < 0]
    if negative_qty:
        audit_findings.append({
            'category': 'Negative Quantities',
            'severity': 'High',
            'count': len(negative_qty),
            'details': negative_qty
        })
    
    # Check for assets with zero or negative prices
    invalid_prices = [(name, data['price']) for name, data in system.inventory.items() if data.get('price', 0) <= 0]
    if invalid_prices:
        audit_findings.append({
            'category': 'Invalid Prices',
            'severity': 'Medium',
            'count': len(invalid_prices),
            'details': invalid_prices
        })
    
    # Check for missing critical information
    missing_info = []
    for name, data in system.inventory.items():
        missing_fields = []
        if not data.get('category'): missing_fields.append('category')
        if not data.get('supplier'): missing_fields.append('supplier')
        if not data.get('description'): missing_fields.append('description')
        if missing_fields:
            missing_info.append((name, missing_fields))
    
    if missing_info:
        audit_findings.append({
            'category': 'Missing Information',
            'severity': 'Low',
            'count': len(missing_info),
            'details': missing_info
        })
    
    # Get transaction statistics
    try:
        system.cursor.execute("""
            SELECT action, COUNT(*) as count, SUM(quantity) as total_qty
            FROM asset_transactions
            GROUP BY action
        """)
        transaction_stats = system.cursor.fetchall()
    except:
        transaction_stats = []
    
    # Calculate totals
    total_assets = len(system.inventory)
    total_quantity = sum(d['quantity'] for d in system.inventory.values())
    total_value = sum(d.get('price', 0) * d['quantity'] for d in system.inventory.values())
    
    return render_template('report_audit.html', 
                         title='Audit Report',
                         audit_findings=audit_findings,
                         transaction_stats=transaction_stats,
                         total_assets=total_assets,
                         total_quantity=total_quantity,
                         total_value=total_value)


@app.route('/reports/checkout')
@login_required
def report_checkout():
    # Get all checkout transactions
    try:
        system.cursor.execute("""
            SELECT t.id, t.asset_name, t.quantity, t.person, t.department, t.location, 
                   t.notes, t.username, t.created_at
            FROM asset_transactions t
            WHERE t.action = 'checkout'
            ORDER BY t.created_at DESC
        """)
        transactions = system.cursor.fetchall()
        
        checkout_data = []
        for row in transactions:
            checkout_data.append({
                'id': row[0],
                'item_name': row[1],
                'quantity': row[2],
                'person': row[3],
                'department': row[4],
                'location': row[5],
                'notes': row[6],
                'username': row[7],
                'created_at': row[8]
            })
        
        return render_template('report_checkout.html', title='Check-out Report', transactions=checkout_data)
    except Exception as e:
        flash(f'Error loading checkout report: {str(e)}', 'error')
        return render_template('report_checkout.html', title='Check-out Report', transactions=[])


@app.route('/reports/contract')
@login_required
def report_contract():
    # Get contracts/licenses from transactions
    try:
        system.cursor.execute("""
            SELECT t.id, t.asset_name, t.notes, t.person as vendor,
                   t.department as contract_type, t.created_at as start_date
            FROM asset_transactions t
            WHERE t.action IN ('lease', 'contract')
            ORDER BY t.created_at DESC
        """)
        contracts = system.cursor.fetchall()
        
        contract_data = []
        for row in contracts:
            contract_data.append({
                'id': row[0],
                'asset_name': row[1],
                'notes': row[2],
                'vendor': row[3],
                'type': row[4],
                'start_date': row[5],
                'status': 'Active'
            })
        
        # Calculate summary
        total_contracts = len(contract_data)
        active_contracts = len([c for c in contract_data if c['status'] == 'Active'])
        
        return render_template('report_contract.html', 
                             title='Contract Report',
                             contracts=contract_data,
                             total_contracts=total_contracts,
                             active_contracts=active_contracts)
    except Exception as e:
        return render_template('report_contract.html', title='Contract Report', contracts=[], total_contracts=0, active_contracts=0)


@app.route('/reports/depreciation')
@login_required
def report_depreciation():
    depreciation_data = []
    total_purchase_value = 0
    total_current_value = 0
    total_depreciation = 0
    
    for name, d in system.inventory.items():
        if d.get('purchase_date') and d.get('depreciation_method') != 'none':
            purchase_value = d.get('price', 0) * d.get('quantity', 0)
            current_value = calculate_depreciation(
                d.get('price', 0),
                d.get('purchase_date'),
                d.get('salvage_value', 0),
                d.get('useful_life_years', 5),
                d.get('depreciation_method', 'straight_line')
            ) * d.get('quantity', 0)
            
            depreciation_amount = purchase_value - current_value
            depreciation_percent = (depreciation_amount / purchase_value * 100) if purchase_value > 0 else 0
            
            asset_info = {
                'name': name,
                'purchase_date': d.get('purchase_date'),
                'purchase_value': purchase_value,
                'current_value': current_value,
                'depreciation_amount': depreciation_amount,
                'depreciation_percent': depreciation_percent,
                'method': d.get('depreciation_method', 'straight_line'),
                'useful_life': d.get('useful_life_years', 5),
                'quantity': d.get('quantity', 0)
            }
            depreciation_data.append(asset_info)
            
            total_purchase_value += purchase_value
            total_current_value += current_value
            total_depreciation += depreciation_amount
    
    depreciation_data.sort(key=lambda x: x['depreciation_amount'], reverse=True)
    
    return render_template('report_depreciation.html', title='Depreciation Report',
                         assets=depreciation_data, total_purchase_value=total_purchase_value,
                         total_current_value=total_current_value, total_depreciation=total_depreciation)


@app.route('/reports/funding')
@login_required
def report_funding():
    # Get funding information from assets
    funding_data = []
    total_investment = 0
    total_current_value = 0
    
    for name, d in system.inventory.items():
        purchase_value = d.get('price', 0) * d.get('quantity', 0)
        current_value = purchase_value
        
        if d.get('purchase_date') and d.get('depreciation_method') != 'none':
            current_value = calculate_depreciation(
                d.get('price', 0),
                d.get('purchase_date'),
                d.get('salvage_value', 0),
                d.get('useful_life_years', 5),
                d.get('depreciation_method', 'straight_line')
            ) * d.get('quantity', 0)
        
        funding_data.append({
            'name': name,
            'category': d.get('category', 'Uncategorized'),
            'quantity': d.get('quantity', 0),
            'purchase_value': purchase_value,
            'current_value': current_value,
            'department': d.get('department', '-'),
            'purchase_date': d.get('purchase_date', '-')
        })
        
        total_investment += purchase_value
        total_current_value += current_value
    
    # Group by category
    category_summary = {}
    for item in funding_data:
        cat = item['category']
        if cat not in category_summary:
            category_summary[cat] = {'purchase_value': 0, 'current_value': 0, 'count': 0}
        category_summary[cat]['purchase_value'] += item['purchase_value']
        category_summary[cat]['current_value'] += item['current_value']
        category_summary[cat]['count'] += 1
    
    funding_data.sort(key=lambda x: x['purchase_value'], reverse=True)
    
    return render_template('report_funding.html', 
                         title='Funding Report',
                         funding_data=funding_data,
                         category_summary=category_summary,
                         total_investment=total_investment,
                         total_current_value=total_current_value)


@app.route('/reports/lease-asset')
@login_required
def report_lease_asset():
    # Get lease transactions
    try:
        system.cursor.execute("""
            SELECT t.id, t.asset_name, t.quantity, t.person as lessee,
                   t.department, t.notes, t.created_at as lease_date, t.username
            FROM asset_transactions t
            WHERE t.action = 'lease'
            ORDER BY t.created_at DESC
        """)
        leases = system.cursor.fetchall()
        
        lease_data = []
        for row in leases:
            lease_data.append({
                'id': row[0],
                'asset_name': row[1],
                'quantity': row[2],
                'lessee': row[3],
                'department': row[4],
                'notes': row[5],
                'lease_date': row[6],
                'username': row[7],
                'status': 'Active'
            })
        
        total_leases = len(lease_data)
        active_leases = len([l for l in lease_data if l['status'] == 'Active'])
        
        return render_template('report_lease_asset.html', 
                             title='Lease Asset Report',
                             leases=lease_data,
                             total_leases=total_leases,
                             active_leases=active_leases)
    except Exception as e:
        return render_template('report_lease_asset.html', title='Lease Asset Report', leases=[], total_leases=0, active_leases=0)


@app.route('/reports/maintenance')
@login_required
def report_maintenance():
    # Get maintenance transactions
    try:
        system.cursor.execute("""
            SELECT t.id, t.asset_name, t.person as maintenance_type,
                   t.department as cost, t.notes, t.created_at as scheduled_date, t.username
            FROM asset_transactions t
            WHERE t.action = 'maintenance'
            ORDER BY t.created_at DESC
        """)
        maintenance_records = system.cursor.fetchall()
        
        maintenance_data = []
        total_cost = 0
        
        for row in maintenance_records:
            # Extract cost from department field
            cost_str = row[3] if row[3] else '0'
            try:
                cost = float(cost_str.replace('Cost: VT', '').replace('VT', '').strip())
            except:
                cost = 0
            
            maintenance_data.append({
                'id': row[0],
                'asset_name': row[1],
                'type': row[2],
                'cost': cost,
                'notes': row[4],
                'scheduled_date': row[5],
                'username': row[6],
                'status': 'Completed'
            })
            total_cost += cost
        
        total_maintenance = len(maintenance_data)
        avg_cost = total_cost / total_maintenance if total_maintenance > 0 else 0
        
        return render_template('report_maintenance.html', 
                             title='Maintenance Report',
                             maintenance_data=maintenance_data,
                             total_maintenance=total_maintenance,
                             total_cost=total_cost,
                             avg_cost=avg_cost)
    except Exception as e:
        return render_template('report_maintenance.html', title='Maintenance Report', maintenance_data=[], total_maintenance=0, total_cost=0, avg_cost=0)


@app.route('/reports/reservation')
@login_required
def report_reservation():
    # Get reservation transactions
    try:
        system.cursor.execute("""
            SELECT t.id, t.asset_name, t.quantity, t.person as reserved_by,
                   t.department as reserved_for, t.notes, t.created_at as reservation_date, t.username
            FROM asset_transactions t
            WHERE t.action = 'reserve'
            ORDER BY t.created_at DESC
        """)
        reservations = system.cursor.fetchall()
        
        reservation_data = []
        for row in reservations:
            reservation_data.append({
                'id': row[0],
                'asset_name': row[1],
                'quantity': row[2],
                'reserved_by': row[3],
                'reserved_for': row[4],
                'notes': row[5],
                'reservation_date': row[6],
                'username': row[7],
                'status': 'Active'
            })
        
        total_reservations = len(reservation_data)
        active_reservations = len([r for r in reservation_data if r['status'] == 'Active'])
        
        return render_template('report_reservation.html', 
                             title='Reservation Report',
                             reservations=reservation_data,
                             total_reservations=total_reservations,
                             active_reservations=active_reservations)
    except Exception as e:
        return render_template('report_reservation.html', title='Reservation Report', reservations=[], total_reservations=0, active_reservations=0)


@app.route('/reports/status')
@login_required
def report_status():
    # System status overview
    total_assets = len(system.inventory)
    total_users = len(system.users)
    total_suppliers = len(system.suppliers)
    total_value = sum(
        calculate_depreciation(
            d.get('price', 0),
            d.get('purchase_date'),
            d.get('salvage_value', 0),
            d.get('useful_life_years', 5),
            d.get('depreciation_method', 'straight_line')
        ) * d.get('quantity', 0)
        for d in system.inventory.values()
    )
    
    # Low stock items
    low_stock = [(name, d) for name, d in system.inventory.items() 
                 if d.get('quantity', 0) < d.get('low_stock_threshold', 5)]
    
    # Recent activity
    try:
        system.cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM asset_transactions
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY action
        """)
        recent_activity = dict(system.cursor.fetchall())
    except:
        recent_activity = {}
    
    status_data = {
        'total_assets': total_assets,
        'total_users': total_users,
        'total_suppliers': total_suppliers,
        'total_value': total_value,
        'low_stock_count': len(low_stock),
        'low_stock_items': low_stock[:5],  # Top 5
        'recent_activity': recent_activity
    }
    
    return render_template('report_status.html', title='Status Report', status=status_data)


@app.route('/reports/transaction')
@login_required
def report_transaction():
    # Get all transactions (both checkin and checkout)
    try:
        system.cursor.execute("""
            SELECT t.id, t.asset_name, t.action, t.quantity, t.person, t.department, 
                   t.location, t.username, t.created_at
            FROM asset_transactions t
            ORDER BY t.created_at DESC
            LIMIT 100
        """)
        transactions = system.cursor.fetchall()
        
        transaction_data = []
        for row in transactions:
            transaction_data.append({
                'id': row[0],
                'item_name': row[1],
                'action': row[2],
                'quantity': row[3],
                'person': row[4],
                'department': row[5],
                'location': row[6],
                'username': row[7],
                'created_at': row[8]
            })
        
        return render_template('report_transaction.html', title='Transaction Report', transactions=transaction_data)
    except Exception as e:
        return render_template('report_transaction.html', title='Transaction Report', transactions=[])


@app.route('/reports/other')
@login_required
def report_other():
    # General purpose report with mixed data
    data = {
        'assets_by_supplier': {},
        'assets_by_location': {},
        'assets_by_department': {},
        'recent_transactions': []
    }
    
    # Group assets by supplier
    for name, d in system.inventory.items():
        supplier = d.get('supplier', 'Unknown')
        if supplier not in data['assets_by_supplier']:
            data['assets_by_supplier'][supplier] = []
        data['assets_by_supplier'][supplier].append({'name': name, 'quantity': d['quantity']})
    
    # Group assets by location
    for name, d in system.inventory.items():
        location = d.get('location', 'Not Set')
        if location not in data['assets_by_location']:
            data['assets_by_location'][location] = []
        data['assets_by_location'][location].append({'name': name, 'quantity': d['quantity']})
    
    # Group assets by department
    for name, d in system.inventory.items():
        department = d.get('department', 'Not Set')
        if department not in data['assets_by_department']:
            data['assets_by_department'][department] = []
        data['assets_by_department'][department].append({'name': name, 'quantity': d['quantity']})
    
    # Get recent transactions
    try:
        system.cursor.execute("""
            SELECT asset_name, action, quantity, created_at
            FROM asset_transactions
            ORDER BY created_at DESC
            LIMIT 20
        """)
        transactions = system.cursor.fetchall()
        data['recent_transactions'] = [
            {'asset': row[0], 'action': row[1], 'quantity': row[2], 'date': row[3]}
            for row in transactions
        ]
    except:
        pass
    
    return render_template('report_other.html', title='Other Report', data=data)


# ---- Help & Support route ----
@app.route('/help-support')
@login_required
def help_support():
    return render_template('page.html', title='Help & Support', heading='Help & Support', description='Get help with using the asset management system and contact support.')


if __name__ == "__main__":
    # Use configuration from config.py (supports environment variables)
    # For cloud deployment: host=0.0.0.0 allows external connections
    # Set FLASK_DEBUG=false in production environment
    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug']
    )