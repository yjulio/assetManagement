
 



 

from flask import Flask, request, redirect, url_for, flash, session, render_template, send_from_directory, jsonify
from AssetManagement import InventorySystem
from config import FLASK_CONFIG, DB_CONFIG, BACKUP_CONFIG
from utils.data_quality import DataQualityCleaner
import html
import os
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
import secrets

try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:
    pd = None
    HAVE_PANDAS = False

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# CSRF Protection Helper
def validate_csrf_token():
    """Validate CSRF token from form/JSON. Returns True if valid, False otherwise."""
    # Check form data first
    form_token = request.form.get('csrf_token')
    # For JSON requests, check JSON body
    if not form_token and request.is_json:
        form_token = request.json.get('csrf_token')
    
    session_token = session.get('csrf_token')
    
    if not form_token or not session_token or form_token != session_token:
        return False
    return True

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
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.secret_key = FLASK_CONFIG.get('secret_key', 'change_this_to_a_random_secret')
system = InventorySystem()

# Inject CSRF token into all templates (simple session-based protection)
@app.context_processor
def inject_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return dict(csrf_token=token)

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


def require_group(*allowed_groups):
    """Decorator to require that the logged-in user belongs to one of the allowed groups."""
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
            user_groups = user.get('groups', set())
            # Check if user belongs to any of the allowed groups
            if not any(group in user_groups for group in allowed_groups):
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
            flash('Please log in to access this page', 'warning')
            # Save the page they were trying to access
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return wrapped

@app.route("/landing")
def landing():
    """Public landing page"""
    groups_list = sorted(system.groups.keys()) if system.groups else []
    return render_template('landing.html', groups=groups_list)

@app.route("/")
def index():
    # If not logged in, show landing page
    if not session.get('username'):
        groups_list = sorted(system.groups.keys()) if system.groups else []
        return render_template('landing.html', groups=groups_list)
    
    # If logged in, show dashboard
    # Get search query
    search_query = request.args.get('q', '').lower()
    # Calculate dashboard metrics
    items = system.inventory
    if search_query:
        items = {k: v for k, v in items.items() if search_query in k.lower() or search_query in (v.get('category','').lower()) or search_query in (v.get('supplier','').lower())}
    
    # Get dashboard configuration from database or session
    user_id = session.get('username', 'default')
    dashboard_widgets = session.get('dashboard_widgets', ['total_assets', 'inhouse_assets', 'total_value', 'categories'])
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
    inhouse_assets = total_items - checked_out
    pending_maintenance = sum(1 for item in items.values() if item.get('maintenance_status') == 'pending')
    
    # Get recent activity (last 10 items) - only if needed
    recent_activity = []
    if 'recent_activity' in dashboard_widgets:
        inventory_items = sorted([(name, type('Obj', (), d)) for name, d in items.items()], key=lambda x: x[0])
        recent_activity = inventory_items[:10]
    
    return render_template('index.html', 
                         title='Dashboard', 
                         total_items=total_items, 
                         total_value=total_value, 
                         low_stock_items=low_stock_items, 
                         unique_categories=unique_categories,
                         total_suppliers=total_suppliers,
                         checked_out=checked_out,
                         inhouse_assets=inhouse_assets,
                         pending_maintenance=pending_maintenance,
                         recent_activity=recent_activity,
                         dashboard_widgets=dashboard_widgets,
                         dashboard_charts=dashboard_charts)

@app.route("/dashboard/export/<format_type>")
@login_required
def dashboard_export(format_type):
    """Export dashboard data in various formats"""
    # Get dashboard data
    items = system.inventory
    user_id = session.get('username', 'default')
    
    # Calculate metrics
    total_items = len(items)
    total_value = sum(item['quantity'] * item['price'] for item in items.values())
    low_stock_items = sum(1 for item in items.values() if item['quantity'] <= 5)
    unique_categories = len(set(item['category'] for item in items.values()))
    
    # Prepare data for export
    dashboard_data = {
        'Total Assets': total_items,
        'Total Value': f'VT{total_value:,.0f}',
        'Low Stock Items': low_stock_items,
        'Categories': unique_categories,
        'Suppliers': len(system.suppliers)
    }
    
    # Get asset details
    asset_details = []
    for name, item in items.items():
        asset_details.append({
            'Asset Name': name,
            'Quantity': item['quantity'],
            'Price': item['price'],
            'Total Value': item['quantity'] * item['price'],
            'Category': item.get('category', ''),
            'Supplier': item.get('supplier', ''),
            'Department': item.get('department', ''),
            'Location': item.get('location', ''),
            'Status': 'Low Stock' if item['quantity'] <= 5 else 'Normal'
        })
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'pdf':
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from io import BytesIO
            from flask import make_response
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c3e50'), spaceAfter=30)
            title = Paragraph('Asset Management Dashboard', title_style)
            elements.append(title)
            
            # Date
            date_text = Paragraph(f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', styles['Normal'])
            elements.append(date_text)
            elements.append(Spacer(1, 20))
            
            # Summary metrics table
            summary_data = [['Metric', 'Value']]
            for key, value in dashboard_data.items():
                summary_data.append([key, str(value)])
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(summary_table)
            elements.append(PageBreak())
            
            # Asset details table
            if asset_details:
                elements.append(Paragraph('Asset Details', styles['Heading2']))
                elements.append(Spacer(1, 12))
                
                asset_data = [['Asset', 'Qty', 'Price', 'Value', 'Category', 'Status']]
                for asset in asset_details[:50]:  # Limit to 50 items for PDF
                    asset_data.append([
                        asset['Asset Name'][:30],
                        str(asset['Quantity']),
                        f"VT{asset['Price']:.0f}",
                        f"VT{asset['Total Value']:.0f}",
                        asset['Category'][:20],
                        asset['Status']
                    ])
                
                asset_table = Table(asset_data, colWidths=[1.8*inch, 0.6*inch, 0.8*inch, 0.9*inch, 1.2*inch, 0.8*inch])
                asset_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(asset_table)
            
            doc.build(elements)
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=dashboard_{timestamp}.pdf'
            return response
            
        except ImportError:
            flash('PDF export requires reportlab library. Please install: pip install reportlab', 'error')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'PDF export error: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    elif format_type == 'excel':
        try:
            import pandas as pd
            from io import BytesIO
            from flask import make_response
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Dashboard summary sheet
                summary_df = pd.DataFrame(list(dashboard_data.items()), columns=['Metric', 'Value'])
                summary_df.to_excel(writer, sheet_name='Dashboard Summary', index=False)
                
                # Asset details sheet
                if asset_details:
                    assets_df = pd.DataFrame(asset_details)
                    assets_df.to_excel(writer, sheet_name='Asset Details', index=False)
            
            buffer.seek(0)
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=dashboard_{timestamp}.xlsx'
            return response
            
        except ImportError:
            flash('Excel export requires pandas and openpyxl. Please install: pip install pandas openpyxl', 'error')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Excel export error: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    elif format_type == 'csv':
        import csv
        from io import StringIO
        from flask import make_response
        
        si = StringIO()
        writer = csv.writer(si)
        
        # Write summary
        writer.writerow(['Asset Management Dashboard'])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        writer.writerow(['Dashboard Summary'])
        writer.writerow(['Metric', 'Value'])
        for key, value in dashboard_data.items():
            writer.writerow([key, value])
        
        writer.writerow([])
        writer.writerow(['Asset Details'])
        if asset_details:
            writer.writerow(list(asset_details[0].keys()))
            for asset in asset_details:
                writer.writerow(list(asset.values()))
        
        output = si.getvalue()
        response = make_response(output)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=dashboard_{timestamp}.csv'
        return response
    
    else:
        flash('Invalid export format', 'error')
        return redirect(url_for('index'))

@app.route("/add", methods=["GET", "POST"])
@require_group('Admin', 'manager')
def add():
    if request.method == "POST":
        if not validate_csrf_token():
            flash('⚠️ Invalid security token. Please refresh the page and try again.', 'error')
            return redirect(url_for('add'))
        
        try:
            name = (request.form.get("name", "") or "").strip()
            if not name:
                flash('⚠️ Asset name is required. Please enter a descriptive name for the asset.', 'warning')
                return redirect(url_for('add'))
            
            # Validate quantity
            quantity_str = request.form.get("quantity") or "0"
            try:
                quantity = int(quantity_str)
                if quantity < 0:
                    flash('⚠️ Quantity must be a positive number (e.g., 1, 5, 10).', 'warning')
                    return redirect(url_for('add'))
            except ValueError:
                flash('⚠️ Quantity must be a whole number (e.g., 1, 5, 10).', 'warning')
                return redirect(url_for('add'))
            
            # Validate price
            price_str = request.form.get("price") or "0.0"
            try:
                price = float(price_str)
                if price < 0:
                    flash('⚠️ Price must be a positive number (e.g., 100.00 or 1500.50).', 'warning')
                    return redirect(url_for('add'))
            except ValueError:
                flash('⚠️ Price must be a valid number (e.g., 100.00 or 1500.50).', 'warning')
                return redirect(url_for('add'))
            
            description = request.form.get("description", "") or ""
            
            # Validate low stock threshold
            threshold_str = request.form.get("low_stock_threshold") or "5"
            try:
                low_stock_threshold = int(threshold_str)
                if low_stock_threshold < 0:
                    low_stock_threshold = 5
            except ValueError:
                low_stock_threshold = 5
            
            category = request.form.get("category", "Uncategorized") or "Uncategorized"
            supplier = request.form.get("supplier", "Unknown") or "Unknown"
            department = (request.form.get('department') or '').strip() or None
            funding_source = (request.form.get('funding_source') or '').strip() or None
            location = (request.form.get('location') or '').strip() or None
            model = (request.form.get('model') or '').strip() or None
            brand = (request.form.get('brand') or '').strip() or None
            serial_number = (request.form.get('serial_number') or '').strip() or None
            purchase_date = (request.form.get('purchase_date') or '').strip() or None
            depreciation_method = request.form.get('depreciation_method', 'straight_line')
            
            # Validate useful life years
            useful_life_str = request.form.get('useful_life_years') or "5"
            try:
                useful_life_years = int(useful_life_str)
                if useful_life_years < 1:
                    flash('⚠️ Useful life must be at least 1 year.', 'warning')
                    return redirect(url_for('add'))
            except ValueError:
                flash('⚠️ Useful life must be a whole number (e.g., 3, 5, or 10 years).', 'warning')
                return redirect(url_for('add'))
            
            # Validate salvage value
            salvage_str = request.form.get('salvage_value') or "0.0"
            try:
                salvage_value = float(salvage_str)
                if salvage_value < 0:
                    flash('⚠️ Salvage value must be a positive number.', 'warning')
                    return redirect(url_for('add'))
            except ValueError:
                flash('⚠️ Salvage value must be a valid number (e.g., 100.00).', 'warning')
                return redirect(url_for('add'))
            
            system.add_item(name, quantity, price, description, low_stock_threshold, category, supplier, 
                          department, funding_source, location, model, brand, serial_number, purchase_date,
                          depreciation_method, useful_life_years, salvage_value)
            
            flash(f"✅ Successfully added asset '{name}'! Quantity: {quantity}, Price: ${price:.2f}", 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "unique constraint" in error_msg:
                flash(f"❌ An asset with this name or serial number already exists. Please use a different identifier.", 'error')
            elif "foreign key" in error_msg:
                flash("❌ Invalid reference. Please check your supplier or category selection.", 'error')
            else:
                flash(f"❌ Failed to add asset. Please check all fields and try again. Error: {str(e)}", 'error')
            return redirect(url_for('add'))
    
    return render_template('add.html', title='Add Asset', suppliers=sorted(system.suppliers.keys()))

@app.route("/update", methods=["GET", "POST"])
@require_group('Admin', 'manager')
def update():
    if request.method == "POST":
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('update'))
        name = request.form.get("name","")
        change = int(request.form.get("change") or 0)
        system.update_quantity(name, change)
        return redirect(url_for("index"))
    return render_template('update.html', title='Update Quantity')

@app.route("/suppliers", methods=["GET", "POST"])
@require_group('Admin', 'manager')
def suppliers():
    if request.method == "POST":
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('suppliers'))
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
        if not validate_csrf_token():
            print(f"CSRF validation failed - Form token: {request.form.get('csrf_token')[:10] if request.form.get('csrf_token') else 'None'}, Session token: {session.get('csrf_token')[:10] if session.get('csrf_token') else 'None'}")
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('groups'))
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
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('users'))
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
            flash(f'User "{username}" added successfully', 'success')
        return redirect(url_for('users'))
    users_list = sorted([(uname, {'email': u.get('email',''), 'groups': u.get('groups', set())}) for uname, u in system.users.items()], key=lambda x: x[0])
    # For Jinja, groups can be set; Jinja can iterate sets but order may vary; acceptable for now
    users_ns = [(uname, type('Obj', (), d)) for uname, d in users_list]
    return render_template('users.html', title='Users', users=users_ns)

@app.route('/users/delete/<username>', methods=['POST'])
@require_group('Admin')
def delete_user(username):
    """Delete a user"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('users'))
    
    try:
        # Prevent deleting yourself
        current_user = session.get('username')
        if username == current_user:
            flash('You cannot delete your own account', 'error')
            return redirect(url_for('users'))
        
        # Check if user exists
        if username not in system.users:
            flash('User not found', 'error')
            return redirect(url_for('users'))
        
        # Get user ID
        user_id = system.users[username]['id']
        
        # Delete from database using connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete user_groups associations first (foreign key)
        cursor.execute("DELETE FROM user_groups WHERE user_id = %s", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Remove from memory
        del system.users[username]
        
        flash(f'User "{username}" deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('users'))


@app.route('/assign-group', methods=['GET', 'POST'])
@require_group('Admin')
def assign_group():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('assign_group'))
        username = request.form.get('username','').strip()
        group_name = request.form.get('group','').strip()
        if username and group_name:
            system.assign_user_to_group(username, group_name)
        return redirect(url_for('assign_group'))
    return render_template('assign_group.html', title='Assign Group', users=sorted(system.users.keys()), groups=sorted(system.groups.keys()))



@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to dashboard
    if session.get('username'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if not validate_csrf_token():
            error = 'Invalid security token. Please try again.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        group = request.form.get('group','').strip()
        
        if not username or not password or not group:
            error = 'Please fill in all fields.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        user = system.users.get(username)
        if not user:
            error = 'Invalid username or password.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        # Check if user belongs to the selected group
        user_groups = user.get('groups', set())
        if group not in user_groups:
            error = f'This account does not have {group} privileges.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        pw_hash = user.get('password_hash')
        if pw_hash and check_password_hash(pw_hash, password):
            session['username'] = username
            session['group'] = group
            session['groups'] = list(user_groups)  # Store all user groups
            flash(f'Welcome to VBOS Asset Management System, {username}!', 'success')
            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
    
    # GET request - show landing page with login form
    groups_list = sorted(system.groups.keys())
    return render_template('landing.html', groups=groups_list)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    return send_from_directory(upload_folder, filename)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Support POST with CSRF validation (secure) and GET for backward compatibility
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid logout request. Please try again.', 'error')
            return redirect(url_for('landing'))
    
    # Clear all session data
    username = session.get('username', 'User')
    session.clear()
    
    # Don't show goodbye message on landing page to avoid confusion on next login
    return redirect(url_for('landing'))


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
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('change_profile'))
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
@require_group('Admin', 'manager')
def checkout():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('⚠️ Invalid security token. Please refresh the page and try again.', 'error')
            return redirect(url_for('checkout'))
        
        name = (request.form.get('name') or '').strip()
        if not name:
            flash('⚠️ Asset name is required. Please select an asset from the list.', 'warning')
            return redirect(url_for('checkout'))
        
        try:
            quantity = int(request.form.get('quantity') or 0)
            if quantity <= 0:
                flash('⚠️ Quantity must be at least 1. Please enter a valid quantity.', 'warning')
                return redirect(url_for('checkout'))
        except ValueError:
            flash('⚠️ Quantity must be a whole number (e.g., 1, 2, 5).', 'warning')
            return redirect(url_for('checkout'))
        
        person = (request.form.get('person') or '').strip() or None
        department = (request.form.get('department') or '').strip() or None
        location = (request.form.get('location') or '').strip() or None
        notes = (request.form.get('notes') or '').strip() or None
        
        try:
            system.checkout_item(name, quantity, username=session.get('username'), person=person, department=department, location=location, notes=notes)
            
            # Send email notification to the person checking out the asset
            try:
                from utils.email_util import send_checkout_notification_email
                from datetime import datetime
                
                if person:
                    # Get recipient email from users table
                    cursor = system.conn.cursor(dictionary=True)
                    cursor.execute('SELECT email, name FROM users WHERE username = %s OR name = %s', (person, person))
                    user_data = cursor.fetchone()
                    cursor.close()
                    
                    if user_data and user_data.get('email'):
                        checkout_details = {
                            'department': department or 'N/A',
                            'location': location or 'N/A',
                            'checkout_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'checked_out_by': session.get('username', 'System')
                        }
                        
                        send_checkout_notification_email(
                            recipient_email=user_data['email'],
                            recipient_name=user_data.get('name', person),
                            item_name=name,
                            quantity=quantity,
                            checkout_details=checkout_details,
                            notes=notes
                        )
                        flash(f"✅ Successfully checked out {quantity} unit(s) of '{name}' to {person}. Email notification sent!", 'success')
                    else:
                        flash(f"✅ Successfully checked out {quantity} unit(s) of '{name}' to {person}.", 'success')
                else:
                    flash(f"✅ Successfully checked out {quantity} unit(s) of '{name}'.", 'success')
            except Exception as e:
                print(f"Email notification error: {e}")
                flash(f"✅ Successfully checked out {quantity} unit(s) of '{name}'. (Email notification could not be sent)", 'success')
            
            return redirect(url_for('index'))
        except ValueError as e:
            error_msg = str(e).lower()
            if "insufficient" in error_msg or "not enough" in error_msg:
                flash(f"❌ Insufficient inventory. Cannot checkout {quantity} unit(s) of '{name}'. Please check available quantity.", 'error')
            else:
                flash(f"❌ Checkout failed: {str(e)}", 'error')
            return redirect(url_for('checkout'))
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg:
                flash(f"❌ Asset '{name}' not found. Please select a valid asset from the list.", 'error')
            else:
                flash(f"❌ Failed to checkout asset. Please try again. Error: {str(e)}", 'error')
            return redirect(url_for('checkout'))
    # GET
    return render_template('checkout.html', title='Check Out', items=sorted(system.inventory.keys()))

@app.route('/checkin', methods=['GET','POST'])
@require_group('Admin', 'manager')
def checkin():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('checkin'))
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
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('dispose'))
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
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('maintenance'))
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
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('move'))
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
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('reserve'))
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
@app.route('/company-info', methods=['GET', 'POST'])
@login_required
def company_info():
    """Manage company information"""
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('company_info'))
        
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            legal_name = request.form.get('legal_name', '').strip()
            abbreviation = request.form.get('abbreviation', '').strip()
            description = request.form.get('description', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            postal_code = request.form.get('postal_code', '').strip()
            country = request.form.get('country', '').strip()
            phone = request.form.get('phone', '').strip()
            fax = request.form.get('fax', '').strip()
            email = request.form.get('email', '').strip()
            website = request.form.get('website', '').strip()
            tax_id = request.form.get('tax_id', '').strip()
            registration_number = request.form.get('registration_number', '').strip()
            fiscal_year_start = request.form.get('fiscal_year_start', '').strip()
            currency = request.form.get('currency', '').strip()
            timezone = request.form.get('timezone', '').strip()
            
            if not name:
                flash('Company name is required', 'error')
                return redirect(url_for('company_info'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if company info exists
            cursor.execute("SELECT id FROM company_info LIMIT 1")
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE company_info SET
                        name = %s, legal_name = %s, abbreviation = %s, description = %s,
                        address = %s, city = %s, state = %s, postal_code = %s, country = %s,
                        phone = %s, fax = %s, email = %s, website = %s,
                        tax_id = %s, registration_number = %s, fiscal_year_start = %s,
                        currency = %s, timezone = %s, updated_by = %s
                    WHERE id = %s
                """, (name, legal_name, abbreviation, description, address, city, state, 
                      postal_code, country, phone, fax, email, website, tax_id, 
                      registration_number, fiscal_year_start or None, currency, timezone, 
                      session.get('username'), existing[0]))
                flash('Company information updated successfully', 'success')
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO company_info (
                        name, legal_name, abbreviation, description, address, city, state,
                        postal_code, country, phone, fax, email, website, tax_id,
                        registration_number, fiscal_year_start, currency, timezone, updated_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, legal_name, abbreviation, description, address, city, state,
                      postal_code, country, phone, fax, email, website, tax_id,
                      registration_number, fiscal_year_start or None, currency, timezone,
                      session.get('username')))
                flash('Company information added successfully', 'success')
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f'Error saving company information: {str(e)}', 'error')
        
        return redirect(url_for('company_info'))
    
    # GET request - display company info
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM company_info LIMIT 1")
        company = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return render_template('company_info.html', company=company)
    except Exception as e:
        flash(f'Error loading company information: {str(e)}', 'error')
        return render_template('company_info.html', company=None)

@app.route('/locations')
@login_required
def locations():
    """Display all locations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM locations 
            ORDER BY is_active DESC, name ASC
        """)
        locations_list = cursor.fetchall()
        
        # Count active locations
        active_count = sum(1 for loc in locations_list if loc.get('is_active'))
        
        # Count total assets with locations
        cursor.execute("SELECT COUNT(DISTINCT name) as count FROM inventory WHERE location IS NOT NULL AND location != ''")
        result = cursor.fetchone()
        total_assets = result['count'] if result else 0
        
        cursor.close()
        conn.close()
        
        return render_template('locations.html', 
                             title='Locations Management',
                             locations=locations_list,
                             active_count=active_count,
                             total_assets=total_assets)
    except Exception as e:
        flash(f'Error loading locations: {str(e)}', 'error')
        return render_template('locations.html', title='Locations Management', locations=[], active_count=0, total_assets=0)

@app.route('/locations/add', methods=['POST'])
@login_required
def locations_add():
    """Add a new location"""
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('locations'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip() or None
        location_type = request.form.get('type', 'Office')
        address = request.form.get('address', '').strip() or None
        city = request.form.get('city', '').strip() or None
        state = request.form.get('state', '').strip() or None
        country = request.form.get('country', '').strip() or None
        postal_code = request.form.get('postal_code', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        contact_person = request.form.get('contact_person', '').strip() or None
        capacity = int(request.form.get('capacity', 0))
        description = request.form.get('description', '').strip() or None
        is_active = 1 if request.form.get('is_active') else 0
        created_by = session.get('username', 'unknown')
        
        if not name:
            flash('Location name is required', 'error')
            return redirect(url_for('locations'))
        
        cursor.execute("""
            INSERT INTO locations (name, code, type, address, city, state, country, postal_code, 
                                 phone, contact_person, capacity, description, is_active, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, code, location_type, address, city, state, country, postal_code,
              phone, contact_person, capacity, description, is_active, created_by))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Location "{name}" added successfully', 'success')
    except Exception as e:
        flash(f'Error adding location: {str(e)}', 'error')
    
    return redirect(url_for('locations'))

@app.route('/locations/edit/<int:location_id>', methods=['GET', 'POST'])
@login_required
def locations_edit(location_id):
    """Edit a location"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('locations'))
        
        try:
            name = request.form.get('name', '').strip()
            code = request.form.get('code', '').strip() or None
            location_type = request.form.get('type', 'Office')
            address = request.form.get('address', '').strip() or None
            city = request.form.get('city', '').strip() or None
            state = request.form.get('state', '').strip() or None
            country = request.form.get('country', '').strip() or None
            postal_code = request.form.get('postal_code', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            contact_person = request.form.get('contact_person', '').strip() or None
            capacity = int(request.form.get('capacity', 0))
            description = request.form.get('description', '').strip() or None
            is_active = 1 if request.form.get('is_active') else 0
            
            if not name:
                flash('Location name is required', 'error')
                return redirect(url_for('locations_edit', location_id=location_id))
            
            cursor.execute("""
                UPDATE locations 
                SET name = %s, code = %s, type = %s, address = %s, city = %s, state = %s, 
                    country = %s, postal_code = %s, phone = %s, contact_person = %s, 
                    capacity = %s, description = %s, is_active = %s
                WHERE id = %s
            """, (name, code, location_type, address, city, state, country, postal_code,
                  phone, contact_person, capacity, description, is_active, location_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'Location "{name}" updated successfully', 'success')
            return redirect(url_for('locations'))
        except Exception as e:
            flash(f'Error updating location: {str(e)}', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('locations_edit', location_id=location_id))
    
    # GET request - show edit form
    try:
        cursor.execute("SELECT * FROM locations WHERE id = %s", (location_id,))
        location = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not location:
            flash('Location not found', 'error')
            return redirect(url_for('locations'))
        
        return render_template('locations_edit.html', title='Edit Location', location=location)
    except Exception as e:
        flash(f'Error loading location: {str(e)}', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('locations'))

@app.route('/locations/delete/<int:location_id>', methods=['POST'])
@login_required
def locations_delete(location_id):
    """Delete a location"""
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('locations'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get location name first
        cursor.execute("SELECT name FROM locations WHERE id = %s", (location_id,))
        location = cursor.fetchone()
        
        if location:
            cursor.execute("DELETE FROM locations WHERE id = %s", (location_id,))
            conn.commit()
            flash(f'Location "{location["name"]}" deleted successfully', 'success')
        else:
            flash('Location not found', 'error')
        
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error deleting location: {str(e)}', 'error')
    
    return redirect(url_for('locations'))

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
    """Database management page with backup, restore, and maintenance features"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get recent backup history
        cursor.execute("SELECT * FROM backup_history ORDER BY created_at DESC LIMIT 10")
        backup_history = cursor.fetchall()
        
        # Get database settings
        cursor.execute("SELECT setting_key, setting_value FROM database_settings")
        settings_rows = cursor.fetchall()
        settings = {row['setting_key']: row['setting_value'] for row in settings_rows}
        
        # Get database size and table count
        cursor.execute("""
            SELECT table_schema AS 'name',
                   ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'size'
            FROM information_schema.tables
            WHERE table_schema = 'db_asset'
            GROUP BY table_schema
        """)
        db_size = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_schema = 'db_asset'
        """)
        table_count = cursor.fetchone()
        
        db_info = {
            'name': db_size['name'] if db_size else 'db_asset',
            'size': db_size['size'] if db_size else 0,
            'tables': table_count['count'] if table_count else 0
        }
        
        cursor.close()
        connection.close()
        
        return render_template('backup_restore.html',
                             backup_history=backup_history,
                             settings=settings,
                             db_info=db_info)
    except Exception as e:
        return render_template('page.html',
                             title='Database Error',
                             heading='Database Error',
                             description=f'Error loading database information: {str(e)}')

@app.route('/backup-restore')
@require_group('Admin')
def backup_restore():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get backup history
    cursor.execute('SELECT * FROM backup_history ORDER BY created_at DESC LIMIT 10')
    backup_history = cursor.fetchall()
    
    # Get database settings
    cursor.execute('SELECT setting_key, setting_value FROM database_settings')
    settings_raw = cursor.fetchall()
    settings = {s['setting_key']: s['setting_value'] for s in settings_raw}
    
    # Get database info
    cursor.execute("SELECT table_schema AS 'name', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'size' FROM information_schema.tables WHERE table_schema = 'db_asset' GROUP BY table_schema")
    db_size = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'db_asset'")
    db_tables = cursor.fetchone()
    
    db_info = {
        'name': 'db_asset',
        'size': f"{db_size['size']} MB" if db_size else 'N/A',
        'tables': db_tables['count'] if db_tables else 'N/A'
    }
    
    cursor.close()
    conn.close()
    
    return render_template('backup_restore.html', 
                         title='Backup/Restore', 
                         backup_history=backup_history,
                         settings=settings,
                         db_info=db_info)

@app.route('/backup/sql', methods=['POST'])
@require_group('Admin')
def backup_sql():
    import subprocess
    import os
    from flask import make_response
    
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('backup_restore'))
    
    try:
        # Get database credentials from DB_CONFIG
        db_password = DB_CONFIG['password']
        db_name = DB_CONFIG['database']
        db_user = DB_CONFIG['user']
        db_host = DB_CONFIG['host']
        
        # Create SQL dump
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{db_name}_{timestamp}.sql'
        backup_dir = BACKUP_CONFIG['backup_dir']
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        filepath = os.path.join(backup_dir, filename)
        
        # Use mysqldump command to save to file
        cmd = f'mysqldump -h {db_host} -u {db_user} -p"{db_password}" {db_name} > {filepath}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Check if file size exceeds limit
            max_size_bytes = BACKUP_CONFIG['max_backup_size_mb'] * 1024 * 1024
            if file_size > max_size_bytes:
                flash(f'Warning: Backup file size ({file_size / 1024 / 1024:.2f} MB) exceeds recommended limit', 'warning')
            
            # Save to backup history
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO backup_history (backup_type, filename, file_size, created_by, status) VALUES (%s, %s, %s, %s, %s)',
                ('SQL', filename, file_size, session.get('username', 'Admin'), 'completed')
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            # Read file and send as download
            with open(filepath, 'r') as f:
                content = f.read()
            
            response = make_response(content)
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            response.headers["Content-type"] = "application/sql"
            flash(f'Database backup created successfully! Size: {file_size / 1024 / 1024:.2f} MB', 'success')
            return response
        else:
            flash(f'Backup failed: {result.stderr}', 'error')
            return redirect(url_for('backup_restore'))
            
    except Exception as e:
        flash(f'Backup error: {str(e)}', 'error')
        return redirect(url_for('backup_restore'))

@app.route('/restore/sql', methods=['POST'])
@require_group('Admin')
def restore_sql():
    import subprocess
    import os
    from werkzeug.utils import secure_filename
    
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('backup_restore'))
    
    if 'backup_file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('backup_restore'))
    
    file = request.files['backup_file']
    
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('backup_restore'))
    
    if not file.filename.endswith('.sql'):
        flash('Only .sql files are allowed!', 'error')
        return redirect(url_for('backup_restore'))
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join('/tmp', filename)
        file.save(temp_path)
        
        # Verify file size
        file_size = os.path.getsize(temp_path)
        max_size_bytes = BACKUP_CONFIG['max_backup_size_mb'] * 1024 * 1024
        if file_size > max_size_bytes:
            os.remove(temp_path)
            flash(f'File too large! Maximum size: {BACKUP_CONFIG["max_backup_size_mb"]} MB', 'error')
            return redirect(url_for('backup_restore'))
        
        # Get database credentials from DB_CONFIG
        db_password = DB_CONFIG['password']
        db_name = DB_CONFIG['database']
        db_user = DB_CONFIG['user']
        db_host = DB_CONFIG['host']
        
        # Restore database
        cmd = f'mysql -h {db_host} -u {db_user} -p"{db_password}" {db_name} < {temp_path}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result.returncode == 0:
            # Log the restore
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO backup_history (backup_type, filename, created_by, status, notes) VALUES (%s, %s, %s, %s, %s)',
                ('RESTORE', filename, session.get('username', 'Admin'), 'completed', 'Database restored from backup')
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Database restored successfully! Please log in again.', 'success')
            # Log out all users after restore
            session.clear()
            return redirect(url_for('login'))
        else:
            flash(f'Restore failed: {result.stderr}', 'error')
            return redirect(url_for('backup_restore'))
            
    except Exception as e:
        flash(f'Restore error: {str(e)}', 'error')
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return redirect(url_for('backup_restore'))

@app.route('/database/optimize', methods=['POST'])
@require_group('Admin')
def database_optimize():
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('backup_restore'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        optimized_count = 0
        for table in tables:
            try:
                cursor.execute(f"OPTIMIZE TABLE {table}")
                optimized_count += 1
            except Exception:
                pass
        
        cursor.close()
        conn.close()
        
        flash(f'Successfully optimized {optimized_count} tables!', 'success')
    except Exception as e:
        flash(f'Optimization error: {str(e)}', 'error')
    
    return redirect(url_for('backup_restore'))

@app.route('/database/check', methods=['POST'])
@require_group('Admin')
def database_check():
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('backup_restore'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        checked_count = 0
        errors = []
        for table in tables:
            try:
                cursor.execute(f"CHECK TABLE {table}")
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
            flash(f'Checked {checked_count} tables. Found issues in: {", ".join(errors[:5])}', 'warning')
        else:
            flash(f'All {checked_count} tables passed integrity check!', 'success')
    except Exception as e:
        flash(f'Check error: {str(e)}', 'error')
    
    return redirect(url_for('backup_restore'))

@app.route('/database/repair', methods=['POST'])
@require_group('Admin')
def database_repair():
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('backup_restore'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        repaired_count = 0
        for table in tables:
            try:
                cursor.execute(f"REPAIR TABLE {table}")
                repaired_count += 1
            except Exception:
                pass
        
        cursor.close()
        conn.close()
        
        flash(f'Successfully repaired {repaired_count} tables!', 'success')
    except Exception as e:
        flash(f'Repair error: {str(e)}', 'error')
    
    return redirect(url_for('backup_restore'))

@app.route('/database/settings', methods=['POST'])
@require_group('Admin')
def database_settings():
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('backup_restore'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get form data
        auto_backup_enabled = 'true' if request.form.get('auto_backup_enabled') else 'false'
        auto_backup_time = request.form.get('auto_backup_time', '02:00')
        backup_retention_days = request.form.get('backup_retention_days', '30')
        optimize_on_backup = 'true' if request.form.get('optimize_on_backup') else 'false'
        
        # Update settings
        settings = [
            ('auto_backup_enabled', auto_backup_enabled),
            ('auto_backup_time', auto_backup_time),
            ('backup_retention_days', backup_retention_days),
            ('optimize_on_backup', optimize_on_backup)
        ]
        
        for key, value in settings:
            cursor.execute(
                'UPDATE database_settings SET setting_value = %s, updated_by = %s WHERE setting_key = %s',
                (value, session.get('username', 'Admin'), key)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Database settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Settings update error: {str(e)}', 'error')
    
    return redirect(url_for('backup_restore'))

@app.route('/manage-dashboard', methods=['GET', 'POST'])
@login_required
def manage_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('manage_dashboard'))

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
            current_widgets = ['total_assets', 'inhouse_assets', 'total_value', 'categories']
        if not current_charts:
            current_charts = []
            
        # Update session with database values
        session['dashboard_widgets'] = current_widgets
        session['dashboard_charts'] = current_charts
        
    except Exception as e:
        # Fallback to session or defaults
        current_widgets = session.get('dashboard_widgets', ['total_assets', 'inhouse_assets', 'total_value', 'categories'])
        current_charts = session.get('dashboard_charts', [])
        flash(f'Using session configuration: {str(e)}', 'warning')
    finally:
        cursor.close()
        conn.close()
    
    return render_template('manage_dashboard.html', 
                         title='Manage Dashboard',
                         current_widgets=current_widgets,
                         current_charts=current_charts)


# ---- Data Quality Routes ----
@app.route('/data-quality')
@login_required
def data_quality_dashboard():
    """Data Quality Dashboard - Clean, standardize, and enrich asset data"""
    items = system.inventory
    
    # Convert to list of dicts for processing
    assets_list = []
    for name, data in items.items():
        asset = data.copy()
        asset['name'] = name
        assets_list.append(asset)
    
    # Generate data quality report
    quality_report = DataQualityCleaner.generate_data_quality_report(assets_list)
    
    # Get sample of assets with issues
    problematic_assets = []
    for asset in assets_list[:20]:  # Show first 20
        issues = []
        if not asset.get('category') or asset.get('category') == '':
            issues.append('Missing category')
        if not asset.get('supplier') or asset.get('supplier') == '':
            issues.append('Missing supplier')
        if not asset.get('location') or asset.get('location') == '':
            issues.append('Missing location')
        if not asset.get('purchase_date'):
            issues.append('Missing purchase date')
        if DataQualityCleaner.clean_numeric(asset.get('price', 0)) == 0:
            issues.append('Zero or invalid price')
        
        if issues:
            problematic_assets.append({
                'name': asset['name'],
                'issues': issues
            })
    
    return render_template('data_quality.html',
                         title='Data Quality Dashboard',
                         quality_report=quality_report,
                         problematic_assets=problematic_assets)


@app.route('/data-quality/clean', methods=['POST'])
@login_required
def clean_data():
    """Clean and standardize all asset data"""
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('data_quality_dashboard'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all assets
        cursor.execute("SELECT name, category, supplier, location, price, quantity FROM inventory")
        assets = cursor.fetchall()
        
        cleaned_count = 0
        for asset in assets:
            name, category, supplier, location, price, quantity = asset
            
            # Standardize
            clean_category = DataQualityCleaner.standardize_category(category)
            clean_supplier = DataQualityCleaner.standardize_supplier(supplier)
            clean_location = DataQualityCleaner.standardize_location(location)
            clean_price = DataQualityCleaner.clean_numeric(price)
            
            # Update if changed
            if (clean_category != category or clean_supplier != supplier or 
                clean_location != location or clean_price != price):
                
                cursor.execute("""
                    UPDATE inventory 
                    SET category = %s, supplier = %s, location = %s, price = %s
                    WHERE name = %s
                """, (clean_category, clean_supplier, clean_location, clean_price, name))
                
                cleaned_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reload system inventory
        system.load_inventory()
        
        flash(f'✅ Successfully cleaned and standardized {cleaned_count} assets!', 'success')
        
    except Exception as e:
        flash(f'Error cleaning data: {str(e)}', 'error')
    
    return redirect(url_for('data_quality_dashboard'))


@app.route('/data-quality/enrich', methods=['POST'])
@login_required
def enrich_data():
    """Enrich asset data with calculated fields"""
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('data_quality_dashboard'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if calculated columns exist, if not add them
        cursor.execute("SHOW COLUMNS FROM inventory LIKE 'age_years'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE inventory ADD COLUMN age_years DECIMAL(10,2) DEFAULT 0")
        
        cursor.execute("SHOW COLUMNS FROM inventory LIKE 'depreciation_value'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE inventory ADD COLUMN depreciation_value DECIMAL(15,2) DEFAULT 0")
        
        cursor.execute("SHOW COLUMNS FROM inventory LIKE 'book_value'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE inventory ADD COLUMN book_value DECIMAL(15,2) DEFAULT 0")
        
        cursor.execute("SHOW COLUMNS FROM inventory LIKE 'lifecycle_status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE inventory ADD COLUMN lifecycle_status VARCHAR(50) DEFAULT 'Unknown'")
        
        cursor.execute("SHOW COLUMNS FROM inventory LIKE 'risk_level'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE inventory ADD COLUMN risk_level VARCHAR(20) DEFAULT 'Low'")
        
        # Get all assets
        cursor.execute("SELECT name, category, supplier, location, price, quantity, purchase_date FROM inventory")
        assets = cursor.fetchall()
        
        enriched_count = 0
        for asset in assets:
            name, category, supplier, location, price, quantity, purchase_date = asset
            
            # Create asset dict
            asset_dict = {
                'name': name,
                'category': category,
                'supplier': supplier,
                'location': location,
                'price': price,
                'quantity': quantity,
                'purchase_date': purchase_date
            }
            
            # Enrich
            enriched = DataQualityCleaner.enrich_asset_data(asset_dict)
            
            # Update with calculated fields
            cursor.execute("""
                UPDATE inventory 
                SET age_years = %s, 
                    depreciation_value = %s,
                    book_value = %s,
                    lifecycle_status = %s,
                    risk_level = %s
                WHERE name = %s
            """, (
                enriched.get('age_years', 0),
                enriched.get('accumulated_depreciation', 0),
                enriched.get('book_value', price),
                enriched.get('lifecycle_status', 'Unknown'),
                enriched.get('risk_level', 'Low'),
                name
            ))
            
            enriched_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reload system inventory
        system.load_inventory()
        
        flash(f'✅ Successfully enriched {enriched_count} assets with calculated fields!', 'success')
        
    except Exception as e:
        flash(f'Error enriching data: {str(e)}', 'error')
    
    return redirect(url_for('data_quality_dashboard'))


# ---- Advances submenu routes ----
@app.route('/contracts')
@login_required
def contracts():
    return render_template('page.html', title='Contracts/Licenses', heading='Contracts and Licenses', description='Track contracts, licenses, and renewal dates.')

@app.route('/contracts/add', methods=['GET', 'POST'])
@login_required
def contracts_add():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('contracts_add'))
        # Handle contract creation
        contract_name = request.form.get('contract_name')
        contract_type = request.form.get('contract_type')
        vendor = request.form.get('vendor')
        contract_number = request.form.get('contract_number')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        cost = request.form.get('cost')
        license_count = request.form.get('license_count')
        auto_renew = request.form.get('auto_renew')
        contact_person = request.form.get('contact_person')
        description = request.form.get('description')
        
        # Handle file uploads
        uploaded_files = []
        if 'contract_files' in request.files:
            files = request.files.getlist('contract_files')
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'contracts')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in files:
                if file and file.filename:
                    # Secure the filename
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, unique_filename)
                    file.save(filepath)
                    uploaded_files.append(unique_filename)
        
        # TODO: Save contract data to database
        
        flash(f'Contract "{contract_name}" added successfully! {len(uploaded_files)} file(s) uploaded.', 'success')
        return redirect('/contracts/list')
    return render_template('contracts_add.html', title='Add Contract')

@app.route('/contracts/upload', methods=['POST'])
@login_required
def contracts_upload():
    """Handle bulk contract file uploads"""
    if not validate_csrf_token():
        return jsonify({'error': 'Invalid CSRF token'}), 403
    try:
        if 'contract_files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('contract_files')
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'contracts')
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file and file.filename:
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                uploaded_files.append({
                    'original_name': file.filename,
                    'saved_name': unique_filename,
                    'path': filepath
                })
        
        # TODO: Parse contract files and extract information
        # TODO: Save to database
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/contracts/list')
@login_required
def contracts_list():
    # TODO: Fetch contracts from database
    return render_template('contracts_list.html', title='All Contracts')

@app.route('/contracts/renewals')
@login_required
def contracts_renewals():
    # TODO: Fetch contracts expiring in 30/60/90 days
    return render_template('contracts_renewals.html', title='Upcoming Renewals')

@app.route('/contracts/expired')
@login_required
def contracts_expired():
    # TODO: Fetch expired contracts
    return render_template('contracts_expired.html', title='Expired Contracts')

@app.route('/contracts/licenses')
@login_required
def contracts_licenses():
    # TODO: Fetch software licenses
    return render_template('contracts_licenses.html', title='Software Licenses')

# =============================================
# APO (Asset Purchase Order) Routes
# =============================================

@app.route('/apo')
@login_required
def apo_index():
    """APO Dashboard - redirect to list"""
    return redirect('/apo/list')

@app.route('/apo/add', methods=['GET', 'POST'])
@login_required
def apo_add():
    """Add new Asset Purchase Order with file attachments"""
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('apo_add'))
        apo_number = request.form.get('apo_number')
        supplier = request.form.get('supplier')
        department = request.form.get('department')
        apo_date = request.form.get('apo_date')
        delivery_date = request.form.get('delivery_date')
        amount = float(request.form.get('amount', 0))
        status = request.form.get('status', 'Pending')
        description = request.form.get('description', '')
        notes = request.form.get('notes', '')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert APO record
            cursor.execute("""
                INSERT INTO apo (apo_number, supplier, department, apo_date, delivery_date, 
                                amount, status, description, notes, uploaded_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (apo_number, supplier, department, apo_date, delivery_date, 
                  amount, status, description, notes, session.get('username')))
            
            apo_id = cursor.lastrowid
            
            # Handle file uploads
            uploaded_files = []
            if 'apo_files' in request.files:
                files = request.files.getlist('apo_files')
                upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'apo')
                os.makedirs(upload_folder, exist_ok=True)
                
                for file in files:
                    if file and file.filename:
                        from werkzeug.utils import secure_filename
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(upload_folder, unique_filename)
                        file.save(filepath)
                        
                        # Save file info to database
                        cursor.execute("""
                            INSERT INTO apo_files (apo_id, original_filename, saved_filename, 
                                                  file_size, uploaded_by)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (apo_id, file.filename, unique_filename, 
                              file.content_length or 0, session.get('username')))
                        
                        uploaded_files.append(unique_filename)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'APO "{apo_number}" added successfully! {len(uploaded_files)} file(s) uploaded.', 'success')
            return redirect('/apo/list')
            
        except Exception as e:
            flash(f'Error adding APO: {str(e)}', 'error')
            return redirect('/apo/add')
    
    # GET request - show form
    suppliers = sorted(system.suppliers.keys()) if hasattr(system, 'suppliers') else []
    return render_template('apo_add.html', title='Add APO', suppliers=suppliers)

@app.route('/apo/list')
@login_required
def apo_list():
    """View all Asset Purchase Orders"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT a.*, 
                   COUNT(af.id) as file_count
            FROM apo a
            LEFT JOIN apo_files af ON a.id = af.apo_id
            GROUP BY a.id
            ORDER BY a.apo_date DESC, a.created_at DESC
        """)
        apos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('apo_list.html', title='Asset Purchase Orders', apos=apos)
    except Exception as e:
        flash(f'Error loading APOs: {str(e)}', 'error')
        return render_template('apo_list.html', title='Asset Purchase Orders', apos=[])

@app.route('/apo/upload', methods=['POST'])
@login_required
def apo_upload():
    """Ajax file upload handler for APO documents"""
    if not validate_csrf_token():
        return jsonify({'error': 'Invalid CSRF token'}), 403
    
    try:
        apo_id = request.form.get('apo_id')
        if not apo_id:
            return jsonify({'error': 'APO ID is required'}), 400
        
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'apo')
        os.makedirs(upload_folder, exist_ok=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        uploaded_files = []
        for file in files:
            if file and file.filename:
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                
                # Save to database
                cursor.execute("""
                    INSERT INTO apo_files (apo_id, filename, file_path, uploaded_by)
                    VALUES (%s, %s, %s, %s)
                """, (apo_id, filename, filepath, session.get('username')))
                
                uploaded_files.append(filename)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/customers')
@login_required
def customers():
    """Display all customers"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM customers 
            ORDER BY status ASC, company_name ASC
        """)
        customers_list = cursor.fetchall()
        
        # Count active customers
        active_count = sum(1 for c in customers_list if c.get('status') == 'Active')
        
        # Sum totals
        total_assigned_assets = sum(c.get('assigned_assets_count', 0) for c in customers_list)
        total_value = sum(c.get('total_value', 0) for c in customers_list)
        
        cursor.close()
        conn.close()
        
        return render_template('customers.html', 
                             title='Customers Management',
                             customers=customers_list,
                             active_count=active_count,
                             total_assigned_assets=total_assigned_assets,
                             total_value=total_value)
    except Exception as e:
        flash(f'Error loading customers: {str(e)}', 'error')
        return render_template('customers.html', title='Customers Management', 
                             customers=[], active_count=0, total_assigned_assets=0, total_value=0)

@app.route('/customers/add', methods=['POST'])
@login_required
def customers_add():
    """Add a new customer"""
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('customers'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        customer_code = request.form.get('customer_code', '').strip() or None
        company_name = request.form.get('company_name', '').strip()
        contact_name = request.form.get('contact_name', '').strip() or None
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        mobile = request.form.get('mobile', '').strip() or None
        address = request.form.get('address', '').strip() or None
        city = request.form.get('city', '').strip() or None
        state = request.form.get('state', '').strip() or None
        country = request.form.get('country', '').strip() or None
        postal_code = request.form.get('postal_code', '').strip() or None
        website = request.form.get('website', '').strip() or None
        tax_id = request.form.get('tax_id', '').strip() or None
        customer_type = request.form.get('customer_type', 'Corporate')
        status = request.form.get('status', 'Active')
        credit_limit = float(request.form.get('credit_limit', 0))
        payment_terms = request.form.get('payment_terms', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        created_by = session.get('username', 'unknown')
        
        if not company_name:
            flash('Company name is required', 'error')
            return redirect(url_for('customers'))
        
        cursor.execute("""
            INSERT INTO customers (customer_code, company_name, contact_name, email, phone, mobile,
                                 address, city, state, country, postal_code, website, tax_id,
                                 customer_type, status, credit_limit, payment_terms, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (customer_code, company_name, contact_name, email, phone, mobile,
              address, city, state, country, postal_code, website, tax_id,
              customer_type, status, credit_limit, payment_terms, notes, created_by))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Customer "{company_name}" added successfully', 'success')
    except Exception as e:
        flash(f'Error adding customer: {str(e)}', 'error')
    
    return redirect(url_for('customers'))

@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def customers_edit(customer_id):
    """Edit a customer"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('customers'))
        
        try:
            customer_code = request.form.get('customer_code', '').strip() or None
            company_name = request.form.get('company_name', '').strip()
            contact_name = request.form.get('contact_name', '').strip() or None
            email = request.form.get('email', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            mobile = request.form.get('mobile', '').strip() or None
            address = request.form.get('address', '').strip() or None
            city = request.form.get('city', '').strip() or None
            state = request.form.get('state', '').strip() or None
            country = request.form.get('country', '').strip() or None
            postal_code = request.form.get('postal_code', '').strip() or None
            website = request.form.get('website', '').strip() or None
            tax_id = request.form.get('tax_id', '').strip() or None
            customer_type = request.form.get('customer_type', 'Corporate')
            status = request.form.get('status', 'Active')
            credit_limit = float(request.form.get('credit_limit', 0))
            payment_terms = request.form.get('payment_terms', '').strip() or None
            notes = request.form.get('notes', '').strip() or None
            
            if not company_name:
                flash('Company name is required', 'error')
                return redirect(url_for('customers_edit', customer_id=customer_id))
            
            cursor.execute("""
                UPDATE customers 
                SET customer_code = %s, company_name = %s, contact_name = %s, email = %s, 
                    phone = %s, mobile = %s, address = %s, city = %s, state = %s, country = %s, 
                    postal_code = %s, website = %s, tax_id = %s, customer_type = %s, status = %s,
                    credit_limit = %s, payment_terms = %s, notes = %s
                WHERE id = %s
            """, (customer_code, company_name, contact_name, email, phone, mobile,
                  address, city, state, country, postal_code, website, tax_id,
                  customer_type, status, credit_limit, payment_terms, notes, customer_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'Customer "{company_name}" updated successfully', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            flash(f'Error updating customer: {str(e)}', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('customers_edit', customer_id=customer_id))
    
    # GET request - show edit form
    try:
        cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not customer:
            flash('Customer not found', 'error')
            return redirect(url_for('customers'))
        
        return render_template('customers_edit.html', title='Edit Customer', customer=customer)
    except Exception as e:
        flash(f'Error loading customer: {str(e)}', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('customers'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
def customers_delete(customer_id):
    """Delete a customer"""
    if not validate_csrf_token():
        flash('Invalid CSRF token. Please try again.', 'error')
        return redirect(url_for('customers'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get customer name first
        cursor.execute("SELECT company_name FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        
        if customer:
            cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
            conn.commit()
            flash(f'Customer "{customer["company_name"]}" deleted successfully', 'success')
        else:
            flash('Customer not found', 'error')
        
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'error')
    
    return redirect(url_for('customers'))

# ============================================================================
# DEPARTMENTS MANAGEMENT
# ============================================================================

@app.route('/departments')
@login_required
def departments():
    """Display all departments with statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        search_query = request.args.get('search', '').strip()
        
        # Build query
        query = "SELECT * FROM departments WHERE 1=1"
        params = []
        
        if status_filter == 'active':
            query += " AND is_active = TRUE"
        elif status_filter == 'inactive':
            query += " AND is_active = FALSE"
            
        if search_query:
            query += " AND (name LIKE %s OR code LIKE %s OR manager LIKE %s OR location LIKE %s)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        query += " ORDER BY name ASC"
        
        cursor.execute(query, params)
        departments_list = cursor.fetchall()
        
        # Calculate statistics
        cursor.execute("SELECT COUNT(*) as total FROM departments WHERE is_active = TRUE")
        active_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM departments")
        total_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT SUM(budget) as total FROM departments WHERE is_active = TRUE")
        result = cursor.fetchone()
        total_budget = result['total'] if result['total'] else 0
        
        cursor.execute("SELECT COUNT(DISTINCT manager) as total FROM departments WHERE is_active = TRUE AND manager IS NOT NULL")
        manager_count = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return render_template('departments.html',
                             departments=departments_list,
                             active_count=active_count,
                             total_count=total_count,
                             total_budget=total_budget,
                             manager_count=manager_count,
                             status_filter=status_filter,
                             search_query=search_query)
    except Exception as e:
        flash(f'Error loading departments: {str(e)}', 'error')
        return render_template('departments.html', departments=[], active_count=0, total_count=0, total_budget=0, manager_count=0)

@app.route('/departments/add', methods=['POST'])
@login_required
def add_department():
    """Add a new department"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('departments'))
    
    try:
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        manager = request.form.get('manager', '').strip()
        location = request.form.get('location', '').strip()
        budget = request.form.get('budget', 0)
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not code:
            flash('Department name and code are required', 'error')
            return redirect(url_for('departments'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO departments (name, code, description, manager, location, budget, phone, email, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, code, description, manager, location, budget, phone, email, session.get('username')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Department "{name}" added successfully', 'success')
    except Exception as e:
        flash(f'Error adding department: {str(e)}', 'error')
    
    return redirect(url_for('departments'))

@app.route('/departments/edit/<int:dept_id>')
@login_required
def edit_department(dept_id):
    """Display edit form for a department"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM departments WHERE id = %s", (dept_id,))
        department = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if department:
            return render_template('departments_edit.html', department=department)
        else:
            flash('Department not found', 'error')
            return redirect(url_for('departments'))
    except Exception as e:
        flash(f'Error loading department: {str(e)}', 'error')
        return redirect(url_for('departments'))

@app.route('/departments/update/<int:dept_id>', methods=['POST'])
@login_required
def update_department(dept_id):
    """Update an existing department"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('departments'))
    
    try:
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        manager = request.form.get('manager', '').strip()
        location = request.form.get('location', '').strip()
        budget = request.form.get('budget', 0)
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        is_active = request.form.get('is_active') == '1'
        
        if not name or not code:
            flash('Department name and code are required', 'error')
            return redirect(url_for('edit_department', dept_id=dept_id))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE departments 
            SET name = %s, code = %s, description = %s, manager = %s, 
                location = %s, budget = %s, phone = %s, email = %s, is_active = %s
            WHERE id = %s
        """, (name, code, description, manager, location, budget, phone, email, is_active, dept_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Department "{name}" updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating department: {str(e)}', 'error')
    
    return redirect(url_for('departments'))

@app.route('/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    """Delete a department"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('departments'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get department name before deleting
        cursor.execute("SELECT name FROM departments WHERE id = %s", (dept_id,))
        department = cursor.fetchone()
        
        if department:
            cursor.execute("DELETE FROM departments WHERE id = %s", (dept_id,))
            conn.commit()
            flash(f'Department "{department["name"]}" deleted successfully', 'success')
        else:
            flash('Department not found', 'error')
        
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error deleting department: {str(e)}', 'error')
    
    return redirect(url_for('departments'))

# ============================================================================
# EMPLOYEES MANAGEMENT
# ============================================================================

@app.route('/employees')
@login_required
def employees():
    """Display all employees with statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        department_filter = request.args.get('department', 'all')
        employment_type = request.args.get('employment_type', 'all')
        search_query = request.args.get('search', '').strip()
        
        # Build query
        query = """
            SELECT e.*, d.name as department_name 
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE 1=1
        """
        params = []
        
        if status_filter == 'active':
            query += " AND e.is_active = TRUE"
        elif status_filter == 'inactive':
            query += " AND e.is_active = FALSE"
            
        if department_filter != 'all':
            query += " AND e.department_id = %s"
            params.append(department_filter)
            
        if employment_type != 'all':
            query += " AND e.employment_type = %s"
            params.append(employment_type)
            
        if search_query:
            query += " AND (e.first_name LIKE %s OR e.last_name LIKE %s OR e.employee_id LIKE %s OR e.email LIKE %s OR e.position LIKE %s)"
            search_param = f"%{search_query}%"
            params.extend([search_param] * 5)
        
        query += " ORDER BY e.last_name ASC, e.first_name ASC"
        
        cursor.execute(query, params)
        employees_list = cursor.fetchall()
        
        # Get departments for filter dropdown
        cursor.execute("SELECT id, name FROM departments WHERE is_active = TRUE ORDER BY name")
        departments_list = cursor.fetchall()
        
        # Calculate statistics
        cursor.execute("SELECT COUNT(*) as total FROM employees WHERE is_active = TRUE")
        active_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM employees")
        total_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT department_id) as total FROM employees WHERE is_active = TRUE AND department_id IS NOT NULL")
        dept_with_employees = cursor.fetchone()['total']
        
        cursor.execute("SELECT SUM(salary) as total FROM employees WHERE is_active = TRUE")
        result = cursor.fetchone()
        total_salary = result['total'] if result['total'] else 0
        
        cursor.close()
        conn.close()
        
        return render_template('employees.html',
                             employees=employees_list,
                             departments=departments_list,
                             active_count=active_count,
                             total_count=total_count,
                             dept_with_employees=dept_with_employees,
                             total_salary=total_salary,
                             status_filter=status_filter,
                             department_filter=department_filter,
                             employment_type=employment_type,
                             search_query=search_query)
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'error')
        return render_template('employees.html', employees=[], departments=[], active_count=0, total_count=0, dept_with_employees=0, total_salary=0)

@app.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    """Add a new employee"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('employees'))
    
    try:
        # Get form data
        employee_id = request.form.get('employee_id', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        mobile = request.form.get('mobile', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        department_id = request.form.get('department_id', '').strip()
        position = request.form.get('position', '').strip()
        qualification = request.form.get('qualification', '').strip()
        employment_type = request.form.get('employment_type', '').strip()
        hire_date = request.form.get('hire_date', '').strip()
        salary = request.form.get('salary', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not employee_id or not first_name or not last_name:
            flash('Employee ID, first name, and last name are required', 'error')
            return redirect(url_for('employees'))
        
        # Handle profile photo upload
        photo_path = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                filename = file.filename.lower()
                if '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions:
                    # Create secure filename
                    import os
                    from datetime import datetime
                    ext = filename.rsplit('.', 1)[1]
                    secure_filename = f"{employee_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    
                    # Save file
                    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'employees')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, secure_filename)
                    file.save(file_path)
                    
                    # Store relative path for database
                    photo_path = f"uploads/employees/{secure_filename}"
                else:
                    flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'warning')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO employees (
                employee_id, first_name, last_name, email, phone, mobile, date_of_birth, gender,
                department_id, position, qualification, employment_type, hire_date, salary, address, city, notes, photo_path, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (employee_id, first_name, last_name, email or None, phone, mobile, date_of_birth or None, gender or None,
              department_id or None, position, qualification, employment_type, hire_date or None, salary or None, address, city, notes, photo_path, session.get('username')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Employee "{first_name} {last_name}" added successfully', 'success')
    except Exception as e:
        flash(f'Error adding employee: {str(e)}', 'error')
    
    return redirect(url_for('employees'))

@app.route('/employees/view/<int:emp_id>')
@login_required
def view_employee(emp_id):
    """Display detailed employee information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.*, d.name as department_name 
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.id = %s
        """, (emp_id,))
        employee = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if employee:
            return render_template('employees_view.html', employee=employee)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('employees'))
    except Exception as e:
        flash(f'Error loading employee: {str(e)}', 'error')
        return redirect(url_for('employees'))

@app.route('/employees/edit/<int:emp_id>')
@login_required
def edit_employee(emp_id):
    """Display edit form for an employee"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.*, d.name as department_name 
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.id = %s
        """, (emp_id,))
        employee = cursor.fetchone()
        
        # Get departments for dropdown
        cursor.execute("SELECT id, name FROM departments WHERE is_active = TRUE ORDER BY name")
        departments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if employee:
            return render_template('employees_edit.html', employee=employee, departments=departments)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('employees'))
    except Exception as e:
        flash(f'Error loading employee: {str(e)}', 'error')
        return redirect(url_for('employees'))

@app.route('/employees/update/<int:emp_id>', methods=['POST'])
@login_required
def update_employee(emp_id):
    """Update an existing employee"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('employees'))
    
    try:
        # Get form data
        employee_id = request.form.get('employee_id', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        mobile = request.form.get('mobile', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        department_id = request.form.get('department_id', '').strip()
        position = request.form.get('position', '').strip()
        qualification = request.form.get('qualification', '').strip()
        employment_type = request.form.get('employment_type', '').strip()
        hire_date = request.form.get('hire_date', '').strip()
        termination_date = request.form.get('termination_date', '').strip()
        salary = request.form.get('salary', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
        emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
        notes = request.form.get('notes', '').strip()
        is_active = request.form.get('is_active') == '1'
        
        if not employee_id or not first_name or not last_name:
            flash('Employee ID, first name, and last name are required', 'error')
            return redirect(url_for('edit_employee', emp_id=emp_id))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current photo path
        cursor.execute("SELECT photo_path FROM employees WHERE id = %s", (emp_id,))
        current_employee = cursor.fetchone()
        photo_path = current_employee['photo_path'] if current_employee else None
        
        # Handle profile photo upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                filename = file.filename.lower()
                if '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions:
                    # Delete old photo if exists
                    if photo_path:
                        import os
                        old_photo = os.path.join(os.path.dirname(os.path.dirname(__file__)), photo_path)
                        if os.path.exists(old_photo):
                            os.remove(old_photo)
                    
                    # Create secure filename
                    import os
                    from datetime import datetime
                    ext = filename.rsplit('.', 1)[1]
                    secure_filename = f"{employee_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    
                    # Save file
                    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'employees')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, secure_filename)
                    file.save(file_path)
                    
                    # Store relative path for database
                    photo_path = f"uploads/employees/{secure_filename}"
                else:
                    flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'warning')
        
        cursor.execute("""
            UPDATE employees SET
                employee_id = %s, first_name = %s, last_name = %s, email = %s, phone = %s, mobile = %s,
                date_of_birth = %s, gender = %s, department_id = %s, position = %s, qualification = %s, employment_type = %s,
                hire_date = %s, termination_date = %s, salary = %s, address = %s, city = %s,
                emergency_contact_name = %s, emergency_contact_phone = %s, notes = %s, is_active = %s, photo_path = %s
            WHERE id = %s
        """, (employee_id, first_name, last_name, email or None, phone, mobile, date_of_birth or None, 
              gender or None, department_id or None, position, qualification, employment_type, hire_date or None, 
              termination_date or None, salary or None, address, city, emergency_contact_name, 
              emergency_contact_phone, notes, is_active, photo_path, emp_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Employee "{first_name} {last_name}" updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating employee: {str(e)}', 'error')
    
    return redirect(url_for('employees'))

@app.route('/employees/delete/<int:emp_id>', methods=['POST'])
@login_required
def delete_employee(emp_id):
    """Delete an employee"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('employees'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get employee name before deleting
        cursor.execute("SELECT first_name, last_name FROM employees WHERE id = %s", (emp_id,))
        employee = cursor.fetchone()
        
        if employee:
            cursor.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
            conn.commit()
            flash(f'Employee "{employee["first_name"]} {employee["last_name"]}" deleted successfully', 'success')
        else:
            flash('Employee not found', 'error')
        
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('employees'))

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
@require_group('Admin', 'manager')
def import_data():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('import_data'))
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
@require_group('Admin', 'manager')
def assign_asset(asset_name):
    if asset_name not in system.inventory:
        flash(f'Asset "{asset_name}" not found', 'error')
        return redirect(url_for('assets'))
    
    asset = system.inventory[asset_name]
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('assign_asset', asset_name=asset_name))
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
        
        # Send email notification to the person receiving the asset
        try:
            from utils.email_util import send_asset_assignment_email
            from datetime import datetime
            
            # Get recipient email from users table
            cursor = system.conn.cursor(dictionary=True)
            cursor.execute('SELECT email, name FROM users WHERE username = %s OR name = %s', (person, person))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data and user_data.get('email'):
                asset_details = {
                    'category': asset.get('category', 'N/A'),
                    'brand': asset.get('brand', 'N/A'),
                    'model': asset.get('model', 'N/A'),
                    'serial_number': asset.get('serial_number', 'N/A'),
                    'department': department or 'N/A',
                    'location': location or 'N/A',
                    'assignment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                send_asset_assignment_email(
                    recipient_email=user_data['email'],
                    recipient_name=user_data.get('name', person),
                    asset_name=asset_name,
                    asset_details=asset_details,
                    assigned_by=session.get('username', 'System'),
                    notes=notes
                )
                flash(f'Asset "{asset_name}" successfully assigned to {person}. Email notification sent.', 'success')
            else:
                flash(f'Asset "{asset_name}" successfully assigned to {person}. (No email address found for notification)', 'success')
        except Exception as e:
            print(f"Email notification error: {e}")
            flash(f'Asset "{asset_name}" successfully assigned to {person}. (Email notification failed)', 'success')
        
        return redirect(url_for('assets'))
    
    return render_template('assign_asset.html', asset_name=asset_name, asset=asset)


@app.route('/edit-asset/<asset_name>', methods=['GET', 'POST'])
@require_group('Admin', 'manager')
def edit_asset(asset_name):
    if asset_name not in system.inventory:
        flash(f'Asset "{asset_name}" not found', 'error')
        return redirect(url_for('assets'))
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('edit_asset', asset_name=asset_name))
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
@require_group('Admin', 'manager')
def delete_asset(asset_name):
    try:
        system.remove_item(asset_name)
        flash(f'Asset "{asset_name}" has been deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting asset: {str(e)}', 'error')
    return redirect(url_for('assets'))


@app.route('/delete-selected-assets', methods=['POST'])
@require_group('Admin', 'manager')
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


# --- Alerts Routes ---
@app.route('/alerts/assets-past-due')
@login_required
def alerts_assets_past_due():
    """Display assets that are past their due date for check-in"""
    past_due_assets = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Get checked out assets past their expected return date
        cursor.execute("""
            SELECT asset_name, checkout_date, expected_return_date, 
                   checked_out_to, DATEDIFF(CURDATE(), expected_return_date) as days_overdue
            FROM asset_checkout
            WHERE status = 'checked_out' 
            AND expected_return_date < CURDATE()
            ORDER BY expected_return_date ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            past_due_assets.append({
                'asset_name': row[0],
                'checkout_date': row[1],
                'expected_return_date': row[2],
                'checked_out_to': row[3],
                'days_overdue': row[4]
            })
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error loading past due assets: {str(e)}', 'error')
    
    return render_template('alerts_assets_past_due.html', 
                         title='Assets Past Due', 
                         past_due_assets=past_due_assets)


@app.route('/alerts/contracts-expiring')
@login_required
def alerts_contracts_expiring():
    """Display contracts expiring within the next 30 days"""
    expiring_contracts = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contract_name, contract_type, start_date, end_date, 
                   vendor, DATEDIFF(end_date, CURDATE()) as days_until_expiry
            FROM contracts
            WHERE end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            AND status != 'expired'
            ORDER BY end_date ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            expiring_contracts.append({
                'contract_name': row[0],
                'contract_type': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'vendor': row[4],
                'days_until_expiry': row[5]
            })
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error loading expiring contracts: {str(e)}', 'error')
    
    return render_template('alerts_contracts_expiring.html', 
                         title='Contracts Expiring', 
                         expiring_contracts=expiring_contracts)


@app.route('/alerts/leases-expiring')
@login_required
def alerts_leases_expiring():
    """Display leases expiring within the next 30 days"""
    expiring_leases = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT asset_name, lease_start_date, lease_end_date, 
                   lessor, monthly_payment, DATEDIFF(lease_end_date, CURDATE()) as days_until_expiry
            FROM asset_leases
            WHERE lease_end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            AND status = 'active'
            ORDER BY lease_end_date ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            expiring_leases.append({
                'asset_name': row[0],
                'lease_start_date': row[1],
                'lease_end_date': row[2],
                'lessor': row[3],
                'monthly_payment': row[4],
                'days_until_expiry': row[5]
            })
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error loading expiring leases: {str(e)}', 'error')
    
    return render_template('alerts_leases_expiring.html', 
                         title='Leases Expiring', 
                         expiring_leases=expiring_leases)


@app.route('/alerts/maintenance-due')
@login_required
def alerts_maintenance_due():
    """Display maintenance that is due within the next 7 days"""
    maintenance_due = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if table exists first
        cursor.execute("SHOW TABLES LIKE 'asset_maintenance'")
        if cursor.fetchone():
            cursor.execute("""
                SELECT asset_name, maintenance_type, scheduled_date, 
                       description, DATEDIFF(scheduled_date, CURDATE()) as days_until_due
                FROM asset_maintenance
                WHERE scheduled_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                AND status = 'scheduled'
                ORDER BY scheduled_date ASC
            """)
            rows = cursor.fetchall()
            for row in rows:
                maintenance_due.append({
                    'asset_name': row[0],
                    'maintenance_type': row[1],
                    'scheduled_date': row[2],
                    'description': row[3],
                    'days_until_due': row[4]
                })
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error loading maintenance due: {str(e)}', 'error')
    
    return render_template('alerts_maintenance_due.html', 
                         title='Maintenance Due', 
                         maintenance_due=maintenance_due)


@app.route('/alerts/maintenance-overdue')
@login_required
def alerts_maintenance_overdue():
    """Display maintenance that is overdue"""
    maintenance_overdue = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if table exists first
        cursor.execute("SHOW TABLES LIKE 'asset_maintenance'")
        if cursor.fetchone():
            cursor.execute("""
                SELECT asset_name, maintenance_type, scheduled_date, 
                       description, DATEDIFF(CURDATE(), scheduled_date) as days_overdue
                FROM asset_maintenance
                WHERE scheduled_date < CURDATE()
                AND status = 'scheduled'
                ORDER BY scheduled_date ASC
            """)
            rows = cursor.fetchall()
            for row in rows:
                maintenance_overdue.append({
                    'asset_name': row[0],
                    'maintenance_type': row[1],
                    'scheduled_date': row[2],
                    'description': row[3],
                    'days_overdue': row[4]
                })
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error loading overdue maintenance: {str(e)}', 'error')
    
    return render_template('alerts_maintenance_overdue.html', 
                         title='Maintenance Overdue', 
                         maintenance_overdue=maintenance_overdue)


@app.route('/alerts/warranties-expiring')
@login_required
def alerts_warranties_expiring():
    """Display warranties expiring within the next 30 days"""
    expiring_warranties = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT asset_name, warranty_start_date, warranty_end_date, 
                   warranty_provider, coverage_details, 
                   DATEDIFF(warranty_end_date, CURDATE()) as days_until_expiry
            FROM asset_warranties
            WHERE warranty_end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            AND status = 'active'
            ORDER BY warranty_end_date ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            expiring_warranties.append({
                'asset_name': row[0],
                'warranty_start_date': row[1],
                'warranty_end_date': row[2],
                'warranty_provider': row[3],
                'coverage_details': row[4],
                'days_until_expiry': row[5]
            })
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error loading expiring warranties: {str(e)}', 'error')
    
    return render_template('alerts_warranties_expiring.html', 
                         title='Warranties Expiring', 
                         expiring_warranties=expiring_warranties)


# --- Reports Routes ---
@app.route('/reports/automated')
@login_required
def report_automated():
    # Generate automated report with key metrics
    total_assets = len(system.inventory)
    total_quantity = sum(d['quantity'] for d in system.inventory.values())
    total_value = sum(d.get('price', 0) * d['quantity'] for d in system.inventory.values())
    low_stock_count = sum(1 for d in system.inventory.values() if d['quantity'] <= d.get('low_stock_threshold', 5))
    
    # Get recent transactions with full details
    recent_activity = []
    try:
        system.cursor.execute("""
            SELECT transaction_date, asset_name, action, quantity, notes
            FROM asset_transactions
            WHERE transaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY transaction_date DESC
            LIMIT 20
        """)
        rows = system.cursor.fetchall()
        for row in rows:
            recent_activity.append({
                'transaction_date': row[0],
                'asset_name': row[1],
                'action': row[2],
                'quantity': row[3],
                'notes': row[4]
            })
    except Exception as e:
        print(f"Error fetching recent activity: {e}")
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
    
    # Top assets by value with all required fields
    top_assets = []
    for name, d in system.inventory.items():
        total_val = d.get('price', 0) * d['quantity']
        top_assets.append({
            'name': name,
            'category': d.get('category', 'Uncategorized'),
            'quantity': d['quantity'],
            'total_value': total_val
        })
    top_assets.sort(key=lambda x: x['total_value'], reverse=True)
    top_assets = top_assets[:10]
    
    return render_template('report_automated.html', 
                         title='Automated Report',
                         total_assets=total_assets,
                         total_quantity=total_quantity,
                         total_value=total_value,
                         low_stock_count=low_stock_count,
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
    return render_template('help_support.html', title='Help & Support')

@app.route('/help/user-guide')
@login_required
def help_user_guide():
    return render_template('help_user_guide.html', title='User Guide')

@app.route('/help/documentation')
@login_required
def help_documentation():
    return render_template('help_documentation.html', title='Documentation')

@app.route('/help/faq')
@login_required
def help_faq():
    return render_template('help_faq.html', title='FAQ')

@app.route('/help/video-tutorials')
@login_required
def help_video_tutorials():
    return render_template('help_video_tutorials.html', title='Video Tutorials')

@app.route('/help/contact-support')
@login_required
def help_contact_support():
    return render_template('help_contact_support.html', title='Contact Support')

@app.route('/help/system-info')
@login_required
def help_system_info():
    return render_template('help_system_info.html', title='System Information')

@app.route('/help/release-notes')
@login_required
def help_release_notes():
    return render_template('help_release_notes.html', title='Release Notes')

# Export Routes
@app.route('/export/assets', methods=['GET', 'POST'])
@login_required
def export_assets():
    if request.method == 'POST':
        format_type = request.form.get('format')
        filter_type = request.form.get('filter', 'all')
        fields = request.form.getlist('fields')
        
        if not fields:
            fields = ['id', 'name', 'category', 'serial_number', 'status', 'location', 'cost', 'purchase_date']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Build query based on filter
            query = "SELECT * FROM assets"
            if filter_type != 'all':
                query += f" WHERE status = %s"
                cursor.execute(query, (filter_type,))
            else:
                cursor.execute(query)
            
            assets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Filter fields
            filtered_assets = []
            for asset in assets:
                filtered_asset = {field: asset.get(field) for field in fields if field in asset}
                filtered_assets.append(filtered_asset)
            
            # Generate export file
            if format_type == 'csv':
                import csv
                from io import StringIO
                from flask import make_response
                
                si = StringIO()
                if filtered_assets:
                    writer = csv.DictWriter(si, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(filtered_assets)
                
                output = make_response(si.getvalue())
                output.headers["Content-Disposition"] = f"attachment; filename=assets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output.headers["Content-type"] = "text/csv"
                return output
            
            elif format_type == 'excel' and HAVE_PANDAS:
                from flask import make_response
                from io import BytesIO
                
                df = pd.DataFrame(filtered_assets)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Assets')
                output.seek(0)
                
                response = make_response(output.read())
                response.headers["Content-Disposition"] = f"attachment; filename=assets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                return response
            else:
                flash('Export format not supported or pandas not installed', 'error')
                
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'error')
    
    return render_template('export_assets.html', title='Export Assets')

@app.route('/export/users', methods=['GET', 'POST'])
@login_required
@require_group('Admin')
def export_users():
    if request.method == 'POST':
        format_type = request.form.get('format')
        filter_type = request.form.get('filter', 'all')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Build query based on filter (exclude password field)
            query = "SELECT id, username, email, group_id, created_at FROM users"
            if filter_type != 'all':
                # Add filter logic here based on requirements
                pass
            
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Generate export file
            if format_type == 'csv':
                import csv
                from io import StringIO
                from flask import make_response
                
                si = StringIO()
                if users:
                    fieldnames = ['id', 'username', 'email', 'group_id', 'created_at']
                    writer = csv.DictWriter(si, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(users)
                
                output = make_response(si.getvalue())
                output.headers["Content-Disposition"] = f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output.headers["Content-type"] = "text/csv"
                return output
            
            elif format_type == 'excel' and HAVE_PANDAS:
                from flask import make_response
                from io import BytesIO
                
                df = pd.DataFrame(users)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Users')
                output.seek(0)
                
                response = make_response(output.read())
                response.headers["Content-Disposition"] = f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                return response
                
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'error')
    
    return render_template('export_users.html', title='Export Users')

@app.route('/export/maintenance', methods=['GET', 'POST'])
@login_required
def export_maintenance():
    if request.method == 'POST':
        format_type = request.form.get('format')
        filter_type = request.form.get('filter', 'all')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM maintenance WHERE 1=1"
            params = []
            
            if date_from:
                query += " AND date >= %s"
                params.append(date_from)
            if date_to:
                query += " AND date <= %s"
                params.append(date_to)
            
            cursor.execute(query, params) if params else cursor.execute(query)
            maintenance = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Generate export file
            if format_type == 'csv':
                import csv
                from io import StringIO
                from flask import make_response
                
                si = StringIO()
                if maintenance:
                    fieldnames = maintenance[0].keys()
                    writer = csv.DictWriter(si, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(maintenance)
                
                output = make_response(si.getvalue())
                output.headers["Content-Disposition"] = f"attachment; filename=maintenance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output.headers["Content-type"] = "text/csv"
                return output
            
            elif format_type == 'excel' and HAVE_PANDAS:
                from flask import make_response
                from io import BytesIO
                
                df = pd.DataFrame(maintenance)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Maintenance')
                output.seek(0)
                
                response = make_response(output.read())
                response.headers["Content-Disposition"] = f"attachment; filename=maintenance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                return response
                
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'error')
    
    return render_template('export_maintenance.html', title='Export Maintenance')

@app.route('/export/transactions', methods=['GET', 'POST'])
@login_required
def export_transactions():
    if request.method == 'POST':
        format_type = request.form.get('format')
        transaction_type = request.form.get('transaction_type', 'all')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM asset_transactions WHERE 1=1"
            params = []
            
            if transaction_type != 'all':
                query += " AND action = %s"
                params.append(transaction_type)
            if date_from:
                query += " AND timestamp >= %s"
                params.append(date_from)
            if date_to:
                query += " AND timestamp <= %s"
                params.append(date_to)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params) if params else cursor.execute(query)
            transactions = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Generate export file
            if format_type == 'csv':
                import csv
                from io import StringIO
                from flask import make_response
                
                si = StringIO()
                if transactions:
                    fieldnames = transactions[0].keys()
                    writer = csv.DictWriter(si, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(transactions)
                
                output = make_response(si.getvalue())
                output.headers["Content-Disposition"] = f"attachment; filename=transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output.headers["Content-type"] = "text/csv"
                return output
            
            elif format_type == 'excel' and HAVE_PANDAS:
                from flask import make_response
                from io import BytesIO
                
                df = pd.DataFrame(transactions)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Transactions')
                output.seek(0)
                
                response = make_response(output.read())
                response.headers["Content-Disposition"] = f"attachment; filename=transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                return response
                
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'error')
    
    return render_template('export_transactions.html', title='Export Transactions')

@app.route('/export/all', methods=['GET', 'POST'])
@login_required
@require_group('Admin')
def export_all():
    if request.method == 'POST':
        format_type = request.form.get('format')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            tables = ['assets', 'users', 'asset_transactions', 'maintenance', 'categories', 
                     'locations', 'suppliers', 'employees', 'customers', 'groups']
            
            all_data = {}
            for table in tables:
                try:
                    if table == 'users':
                        # Exclude passwords
                        cursor.execute(f"SELECT id, username, email, group_id, created_at FROM {table}")
                    else:
                        cursor.execute(f"SELECT * FROM {table}")
                    all_data[table] = cursor.fetchall()
                except Exception:
                    # Table might not exist, skip it
                    pass
            
            cursor.close()
            conn.close()
            
            # Generate export file
            if format_type == 'excel' and HAVE_PANDAS:
                from flask import make_response
                from io import BytesIO
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for table_name, data in all_data.items():
                        if data:
                            df = pd.DataFrame(data)
                            df.to_excel(writer, index=False, sheet_name=table_name[:31])  # Excel sheet name limit
                output.seek(0)
                
                response = make_response(output.read())
                response.headers["Content-Disposition"] = f"attachment; filename=full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                return response
            
            elif format_type == 'csv':
                import csv
                import zipfile
                from io import BytesIO, StringIO
                from flask import make_response
                
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for table_name, data in all_data.items():
                        if data:
                            si = StringIO()
                            fieldnames = data[0].keys()
                            writer = csv.DictWriter(si, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(data)
                            zip_file.writestr(f"{table_name}.csv", si.getvalue())
                
                zip_buffer.seek(0)
                response = make_response(zip_buffer.read())
                response.headers["Content-Disposition"] = f"attachment; filename=full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                response.headers["Content-type"] = "application/zip"
                return response
                
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'error')
    
    return render_template('export_all.html', title='Export All Data')


# ---- Email Settings Routes ----
@app.route('/settings/email', methods=['GET', 'POST'])
@login_required
@require_group('Admin')
def email_settings():
    if request.method == 'POST':
        # Save email configuration to environment or database
        email_enabled = request.form.get('email_enabled') == 'on'
        sender_email = request.form.get('sender_email')
        sender_password = request.form.get('sender_password')
        smtp_server = request.form.get('smtp_server')
        smtp_port = int(request.form.get('smtp_port', 587))
        
        try:
            # Save to database email_config table
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if config exists
            cursor.execute('SELECT id FROM email_config LIMIT 1')
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE email_config 
                    SET sender = %s, password = %s, smtp_server = %s, port = %s
                    WHERE id = %s
                ''', (sender_email, sender_password, smtp_server, smtp_port, existing[0]))
            else:
                cursor.execute('''
                    INSERT INTO email_config (sender, password, smtp_server, port)
                    VALUES (%s, %s, %s, %s)
                ''', (sender_email, sender_password, smtp_server, smtp_port))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update config in memory
            from config import EMAIL_CONFIG
            EMAIL_CONFIG['sender_email'] = sender_email
            EMAIL_CONFIG['sender_password'] = sender_password
            EMAIL_CONFIG['smtp_server'] = smtp_server
            EMAIL_CONFIG['smtp_port'] = smtp_port
            EMAIL_CONFIG['enabled'] = email_enabled
            
            flash('Email settings saved successfully!', 'success')
            return redirect(url_for('email_settings'))
            
        except Exception as e:
            flash(f'Failed to save email settings: {str(e)}', 'error')
    
    # Load current email configuration
    email_config = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM email_config LIMIT 1')
        db_config = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if db_config:
            email_config = {
                'sender_email': db_config.get('sender'),
                'smtp_server': db_config.get('smtp_server', 'smtp.gmail.com'),
                'smtp_port': db_config.get('port', 587),
                'enabled': True
            }
        else:
            from config import EMAIL_CONFIG
            email_config = EMAIL_CONFIG
    except Exception as e:
        print(f"Error loading email config: {e}")
        from config import EMAIL_CONFIG
        email_config = EMAIL_CONFIG
    
    return render_template('email_settings.html', email_config=email_config)


@app.route('/settings/email/test', methods=['POST'])
@login_required
@require_group('Admin')
def test_email():
    try:
        from utils.email_util import send_email
        
        sender_email = request.form.get('sender_email')
        sender_password = request.form.get('sender_password')
        smtp_server = request.form.get('smtp_server')
        smtp_port = int(request.form.get('smtp_port', 587))
        
        # Send test email to the sender's address
        subject = "Test Email from Asset Management System"
        body = """
This is a test email from your Asset Management System.

If you received this email, your email configuration is working correctly!

System Information:
- SMTP Server: {}
- SMTP Port: {}
- Timestamp: {}

Best regards,
Asset Management System
""".format(smtp_server, smtp_port, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        success = send_email(
            sender=sender_email,
            recipient=sender_email,
            subject=subject,
            body=body,
            smtp_server=smtp_server,
            port=smtp_port,
            password=sender_password
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ux-demo')
def ux_demo():
    """Demo page showcasing all UX features"""
    return render_template('ux_demo.html')


@app.route('/tailwind-showcase')
def tailwind_showcase():
    """Showcase page for Tailwind CSS components"""
    return render_template('tailwind_showcase.html', title='Tailwind CSS Showcase')


@app.route('/developer/code-generator')
@login_required
@require_group('Admin')
def code_generator():
    """Code generator interface"""
    try:
        from utils.code_generator import CodeGenerator
        generator = CodeGenerator()
        tables = generator.get_all_tables()
        generator.close()
        return render_template('code_generator.html', tables=tables, title='Code Generator')
    except Exception as e:
        flash(f'Error loading tables: {str(e)}', 'error')
        return render_template('code_generator.html', tables=[], title='Code Generator')


@app.route('/developer/generate', methods=['POST'])
@login_required
@require_group('Admin')
def generate_code():
    """Generate code based on table selection"""
    if not validate_csrf_token():
        return jsonify({'success': False, 'error': 'Invalid CSRF token'}), 403
    
    try:
        table_name = request.form.get('table')
        generate_routes = request.form.get('generate_routes') == 'on'
        generate_templates = request.form.get('generate_templates') == 'on'
        save_files = request.form.get('save_files') == 'on'
        
        from utils.code_generator import CodeGenerator
        generator = CodeGenerator()
        
        result = {
            'success': True,
            'table': table_name,
            'routes': '',
            'add_template': '',
            'list_template': ''
        }
        
        if generate_routes:
            result['routes'] = generator.generate_all_routes(table_name)
            
            if save_files:
                # Save to a separate routes file
                routes_file = f'/root/assetManagement/src/generated_routes_{table_name}.py'
                with open(routes_file, 'w') as f:
                    f.write("# Auto-generated routes\n")
                    f.write("# Copy these routes into app.py\n\n")
                    f.write(result['routes'])
                result['routes_file'] = routes_file
        
        if generate_templates:
            columns = generator.get_table_schema(table_name)
            result['add_template'] = generator.generate_add_template(table_name)
            result['list_template'] = generator.generate_list_template(table_name)
            
            if save_files:
                # Save template files
                add_file = f'/root/assetManagement/src/templates/{table_name}_add.html'
                list_file = f'/root/assetManagement/src/templates/{table_name}_list.html'
                
                with open(add_file, 'w') as f:
                    f.write(result['add_template'])
                with open(list_file, 'w') as f:
                    f.write(result['list_template'])
                
                result['add_template_file'] = add_file
                result['list_template_file'] = list_file
        
        generator.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    # Use configuration from config.py (supports environment variables)
    # For cloud deployment: host=0.0.0.0 allows external connections
    # Set FLASK_DEBUG=false in production environment
    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug']
    )