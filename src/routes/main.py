"""Main routes - Landing page and Dashboard"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify, Response
from functools import wraps
import csv
import io
from datetime import datetime

# Create blueprint
main_bp = Blueprint('main', __name__)

# These will be injected by app.py
system = None
get_db_connection = None

def init_main_routes(inventory_system, db_connection_func):
    """Initialize main routes with dependencies"""
    global system, get_db_connection
    system = inventory_system
    get_db_connection = db_connection_func

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('username'):
            from flask import flash
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('main.landing'))
        return f(*args, **kwargs)
    return wrapped

@main_bp.route("/")
def index():
    """Dashboard - Main entry point"""
    # If not logged in, show landing page
    if not session.get('username'):
        groups_list = sorted(system.groups.keys()) if system.groups else []
        return render_template('landing.html', groups=groups_list)
    
    # If logged in, show dashboard
    search_query = request.args.get('q', '').lower()
    items = system.inventory
    
    if search_query:
        items = {k: v for k, v in items.items() 
                if search_query in k.lower() 
                or search_query in (v.get('category','').lower()) 
                or search_query in (v.get('supplier','').lower())}
    
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
    
    # Calculate all metrics
    total_items = len(items)
    total_value = sum(item['quantity'] * item['price'] for item in items.values())
    low_stock_items = sum(1 for item in items.values() if item['quantity'] <= 5)
    unique_categories = len(set(item['category'] for item in items.values()))
    total_suppliers = len(system.suppliers)
    checked_out = sum(1 for item in items.values() if item.get('checked_out', False))
    inhouse_assets = total_items - checked_out
    pending_maintenance = sum(1 for item in items.values() if item.get('maintenance_status') == 'pending')
    
    # Get recent activity (last 10 items)
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

@main_bp.route("/landing")
def landing():
    """Public landing page with login form"""
    groups_list = sorted(system.groups.keys()) if system.groups else []
    return render_template('landing.html', groups=groups_list)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Alias for index - redirects to main dashboard"""
    return redirect(url_for('main.index'))

@main_bp.route("/dashboard/export/<format_type>")
@login_required
def dashboard_export(format_type):
    """Export dashboard data in various formats"""
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
            'Location': item.get('location', ''),
            'Supplier': item.get('supplier', ''),
            'Status': 'Checked Out' if item.get('checked_out') else 'In House'
        })
    
    if format_type == 'csv':
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write summary
        writer.writerow(['Dashboard Summary'])
        writer.writerow(['Metric', 'Value'])
        for key, value in dashboard_data.items():
            writer.writerow([key, value])
        
        writer.writerow([])  # Empty row
        writer.writerow(['Asset Details'])
        
        # Write asset details
        if asset_details:
            writer.writerow(asset_details[0].keys())
            for asset in asset_details:
                writer.writerow(asset.values())
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=dashboard_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
    
    elif format_type == 'json':
        return jsonify({
            'summary': dashboard_data,
            'assets': asset_details,
            'exported_at': datetime.now().isoformat(),
            'exported_by': user_id
        })
    
    else:
        from flask import flash
        flash('Invalid export format', 'error')
        return redirect(url_for('main.index'))
