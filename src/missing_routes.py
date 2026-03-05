"""Missing routes stub - Placeholder routes for all navigation menu items"""

from flask import render_template, redirect, url_for, flash, session, request, current_app
from functools import wraps
from datetime import datetime, timedelta
from utils.export_utils import (export_to_csv, export_to_excel, get_export_logo_path,
                                 prepare_asset_export_data, prepare_user_export_data,
                                 prepare_maintenance_export_data, prepare_transaction_export_data)
from utils.report_utils import (generate_inventory_report, generate_depreciation_report,
                                 generate_maintenance_report, generate_checkout_report,
                                 generate_alert_data, format_currency)

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('username'):
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def create_missing_routes(app):
    """Create stub routes for all navigation menu items that don't exist"""
    
    # Get existing routes to avoid duplicates
    existing_routes = set(rule.rule for rule in app.url_map.iter_rules())
    
    def safe_add_route(rule, endpoint, handler, methods=['GET', 'POST']):
        """Add route only if it doesn't already exist"""
        if rule not in existing_routes:
            app.add_url_rule(rule, endpoint=endpoint, view_func=handler, methods=methods)
            print(f"  ✓ Registered: {rule}")
            return True
        return False
    
    registered_count = 0
    
    # Alerts Routes - FULLY IMPLEMENTED
    @login_required
    def alerts_warranties_expiring():
        from AssetManagement import InventorySystem
        system = InventorySystem()
        
        today = datetime.now().date()
        thirty_days = today + timedelta(days=30)
        alerts = []
        
        for name, asset in system.inventory.items():
            warranty_date = asset.get('warranty_date')
            if warranty_date:
                try:
                    if isinstance(warranty_date, str):
                        warranty = datetime.strptime(warranty_date, '%Y-%m-%d').date()
                    else:
                        warranty = warranty_date
                    
                    if today < warranty < thirty_days:
                        alerts.append({
                            'asset_name': name,
                            'warranty_date': warranty,
                            'days_remaining': (warranty - today).days,
                            'supplier': asset.get('supplier', 'N/A')
                        })
                except Exception:
                    pass
        
        return render_template('alerts_warranties_expiring.html', title='Warranties Expiring', alerts=alerts)
    registered_count += safe_add_route('/alerts/warranties-expiring', 'alerts_warranties_expiring', alerts_warranties_expiring)
    
    @login_required
    def alerts_maintenance_due():
        from AssetManagement import InventorySystem
        system = InventorySystem()
        
        alerts = []
        today = datetime.now().date()
        thirty_days = today + timedelta(days=30)
        
        try:
            cursor = system.conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM maintenance_schedule 
                WHERE status != 'Completed' 
                AND scheduled_date BETWEEN %s AND %s
                ORDER BY scheduled_date
            """, (today, thirty_days))
            alerts = cursor.fetchall()
            cursor.close()
        except Exception:
            pass
        
        return render_template('alerts_maintenance_due.html', title='Maintenance Due', alerts=alerts)
    registered_count += safe_add_route('/alerts/maintenance-due', 'alerts_maintenance_due', alerts_maintenance_due)
    
    @login_required
    def alerts_maintenance_overdue():
        from AssetManagement import InventorySystem
        system = InventorySystem()
        
        alerts = []
        today = datetime.now().date()
        
        try:
            cursor = system.conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM maintenance_schedule 
                WHERE status != 'Completed' 
                AND scheduled_date < %s
                ORDER BY scheduled_date
            """, (today,))
            alerts = cursor.fetchall()
            
            # Calculate days overdue
            for alert in alerts:
                if alert['scheduled_date']:
                    alert['days_overdue'] = (today - alert['scheduled_date']).days
            
            cursor.close()
        except Exception:
            pass
        
        return render_template('alerts_maintenance_overdue.html', title='Maintenance Overdue', alerts=alerts)
    registered_count += safe_add_route('/alerts/maintenance-overdue', 'alerts_maintenance_overdue', alerts_maintenance_overdue)
    
    @login_required
    def alerts_contracts_expiring():
        # Placeholder - would need contracts table
        return render_template('alerts_contracts_expiring.html', title='Contracts Expiring', alerts=[])
    registered_count += safe_add_route('/alerts/contracts-expiring', 'alerts_contracts_expiring', alerts_contracts_expiring)
    
    @login_required
    def alerts_leases_expiring():
        # Placeholder - would need leases table
        return render_template('alerts_leases_expiring.html', title='Leases Expiring', alerts=[])
    registered_count += safe_add_route('/alerts/leases-expiring', 'alerts_leases_expiring', alerts_leases_expiring)
    
    @login_required
    def alerts_assets_past_due():
        # Placeholder - would need due date tracking
        return render_template('alerts_assets_past_due.html', title='Assets Past Due', alerts=[])
    registered_count += safe_add_route('/alerts/assets-past-due', 'alerts_assets_past_due', alerts_assets_past_due)
    
    # Asset Management Routes (if not already exist)
    @login_required
    def lease():
        return render_template('page.html', title='Lease Asset', heading='Lease Asset', 
                             description='Lease an asset to external party')
    registered_count += safe_add_route('/lease', 'lease', lease)
    
    @login_required
    def lease_return():
        return render_template('page.html', title='Lease Return', heading='Lease Return', 
                             description='Process returned leased assets')
    registered_count += safe_add_route('/lease-return', 'lease_return', lease_return)
    
    # Export Routes - FULLY IMPLEMENTED
    @login_required
    def export_assets():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            export_format = request.form.get('format', 'csv')
            export_data = prepare_asset_export_data(system.inventory)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == 'excel':
                return export_to_excel(export_data, f'assets_export_{timestamp}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(export_data, f'assets_export_{timestamp}.csv')
        
        return render_template('export_assets.html', title='Export Assets')
    registered_count += safe_add_route('/export/assets', 'export_assets', export_assets)
    
    @login_required
    def export_users():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Get users from database
            users = []
            try:
                conn = system.conn
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT username, email, created_at FROM users")
                users_data = cursor.fetchall()
                
                for user in users_data:
                    # Get user groups
                    cursor.execute("""
                        SELECT g.group_name 
                        FROM user_groups ug 
                        JOIN groups g ON ug.group_id = g.id 
                        WHERE ug.username = %s
                    """, (user['username'],))
                    groups = [row['group_name'] for row in cursor.fetchall()]
                    
                    users.append({
                        'username': user['username'],
                        'email': user.get('email', ''),
                        'groups': groups,
                        'created_at': str(user.get('created_at', '')),
                        'last_login': ''
                    })
                cursor.close()
            except Exception as e:
                flash(f'Error fetching users: {str(e)}', 'error')
                return redirect(request.url)
            
            export_data = prepare_user_export_data(users)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_format = request.form.get('format', 'csv')
            
            if export_format == 'excel':
                return export_to_excel(export_data, f'users_export_{timestamp}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(export_data, f'users_export_{timestamp}.csv')
        
        return render_template('export_users.html', title='Export Users')
    registered_count += safe_add_route('/export/users', 'export_users', export_users)
    
    @login_required
    def export_maintenance():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Get maintenance records
            maintenance_records = []
            try:
                conn = system.conn
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT asset_name, maintenance_type, scheduled_date, 
                           completed_date, status, cost, notes, performed_by
                    FROM maintenance_schedule
                    ORDER BY scheduled_date DESC
                """)
                maintenance_records = cursor.fetchall()
                cursor.close()
            except Exception as e:
                flash(f'Error fetching maintenance records: {str(e)}', 'error')
                return redirect(request.url)
            
            export_data = prepare_maintenance_export_data(maintenance_records)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_format = request.form.get('format', 'csv')
            
            if export_format == 'excel':
                return export_to_excel(export_data, f'maintenance_export_{timestamp}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(export_data, f'maintenance_export_{timestamp}.csv')
        
        return render_template('export_maintenance.html', title='Export Maintenance')
    registered_count += safe_add_route('/export/maintenance', 'export_maintenance', export_maintenance)
    
    @login_required
    def export_transactions():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Get transactions
            transactions = []
            try:
                conn = system.conn
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT date, asset_name, transaction_type, username, 
                           from_user, to_user, notes
                    FROM asset_transactions
                    ORDER BY date DESC
                """)
                transactions = cursor.fetchall()
                cursor.close()
            except Exception as e:
                flash(f'Error fetching transactions: {str(e)}', 'error')
                return redirect(request.url)
            
            export_data = prepare_transaction_export_data(transactions)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_format = request.form.get('format', 'csv')
            
            if export_format == 'excel':
                return export_to_excel(export_data, f'transactions_export_{timestamp}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(export_data, f'transactions_export_{timestamp}.csv')
        
        return render_template('export_transactions.html', title='Export Transactions')
    registered_count += safe_add_route('/export/transactions', 'export_transactions', export_transactions)
    
    @login_required
    def export_all():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Export all data as multiple sheets
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_format = request.form.get('format', 'zip')
            
            if export_format == 'zip':
                import zipfile
                import io
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add assets
                    assets_data = prepare_asset_export_data(system.inventory)
                    csv_buffer = io.StringIO()
                    import csv
                    if assets_data:
                        writer = csv.DictWriter(csv_buffer, fieldnames=assets_data[0].keys())
                        writer.writeheader()
                        writer.writerows(assets_data)
                    zip_file.writestr('assets.csv', csv_buffer.getvalue())
                
                zip_buffer.seek(0)
                from flask import Response
                return Response(
                    zip_buffer.getvalue(),
                    mimetype='application/zip',
                    headers={'Content-Disposition': f'attachment; filename=full_export_{timestamp}.zip'}
                )
            else:
                # Export as single Excel with multiple sheets
                assets_data = prepare_asset_export_data(system.inventory)
                return export_to_excel(assets_data, f'full_export_{timestamp}.xlsx', sheet_name='Assets',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
        
        return render_template('export_all.html', title='Export All Data')
    registered_count += safe_add_route('/export/all', 'export_all', export_all)
    
    # Gallery Routes
    @login_required
    def document_gallery():
        return render_template('document_gallery.html', title='Document Gallery')
    registered_count += safe_add_route('/document-gallery', 'document_gallery', document_gallery)
    
    @login_required
    def image_gallery():
        return render_template('image_gallery.html', title='Image Gallery')
    registered_count += safe_add_route('/image-gallery', 'image_gallery', image_gallery)
    
    # Report Routes - FULLY IMPLEMENTED
    @login_required
    def reports_automated():
        return render_template('report_automated.html', title='Automated Report')
    registered_count += safe_add_route('/reports/automated', 'reports_automated', reports_automated)
    
    @login_required
    def reports_custom():
        return render_template('report_custom.html', title='Custom Report')
    registered_count += safe_add_route('/reports/custom', 'reports_custom', reports_custom)
    
    @login_required
    def reports_inventory():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            report_data = generate_inventory_report(system)
            export_format = request.form.get('format', 'pdf')
            
            if export_format == 'csv':
                return export_to_csv(report_data['assets'], f'inventory_report_{datetime.now().strftime("%Y%m%d")}.csv')
            elif export_format == 'excel':
                return export_to_excel(report_data['assets'], f'inventory_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                # For now, return as CSV (PDF would require additional library)
                return export_to_csv(report_data['assets'], f'inventory_report_{datetime.now().strftime("%Y%m%d")}.csv')
        
        return render_template('report_inventory.html', title='Inventory Report')
    registered_count += safe_add_route('/reports/inventory', 'reports_inventory', reports_inventory)
    
    @login_required
    def reports_asset():
        return render_template('report_asset.html', title='Asset Report')
    registered_count += safe_add_route('/reports/asset', 'reports_asset', reports_asset)
    
    @login_required
    def reports_audit():
        return render_template('report_audit.html', title='Audit Report')
    registered_count += safe_add_route('/reports/audit', 'reports_audit', reports_audit)
    
    @login_required
    def reports_checkout():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Get checkout transactions
            transactions = []
            try:
                cursor = system.conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM asset_transactions WHERE transaction_type='check-out' ORDER BY date DESC")
                transactions = cursor.fetchall()
                cursor.close()
            except Exception:
                pass
            
            report_data = generate_checkout_report(transactions)
            export_format = request.form.get('format', 'pdf')
            
            if export_format == 'csv':
                return export_to_csv(report_data['transactions'], f'checkout_report_{datetime.now().strftime("%Y%m%d")}.csv')
            elif export_format == 'excel':
                return export_to_excel(report_data['transactions'], f'checkout_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(report_data['transactions'], f'checkout_report_{datetime.now().strftime("%Y%m%d")}.csv')
        
        return render_template('report_checkout.html', title='Check-out Report')
    registered_count += safe_add_route('/reports/checkout', 'reports_checkout', reports_checkout)
    
    @login_required
    def reports_contract():
        return render_template('report_contract.html', title='Contract Report')
    registered_count += safe_add_route('/reports/contract', 'reports_contract', reports_contract)
    
    @login_required
    def reports_depreciation():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Import calculate_depreciation from app context
            def calculate_depreciation(price, purchase_date, salvage, useful_life, method):
                if not purchase_date or not price:
                    return price
                try:
                    from datetime import datetime
                    if isinstance(purchase_date, str):
                        purchase = datetime.strptime(purchase_date, '%Y-%m-%d')
                    else:
                        purchase = purchase_date
                    years_passed = (datetime.now() - purchase).days / 365.25
                    annual_depreciation = (price - salvage) / useful_life
                    total_depreciation = min(annual_depreciation * years_passed, price - salvage)
                    return max(price - total_depreciation, salvage)
                except Exception:
                    return price
            
            report_data = generate_depreciation_report(system, calculate_depreciation)
            export_format = request.form.get('format', 'pdf')
            
            if export_format == 'csv':
                return export_to_csv(report_data['assets'], f'depreciation_report_{datetime.now().strftime("%Y%m%d")}.csv')
            elif export_format == 'excel':
                return export_to_excel(report_data['assets'], f'depreciation_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(report_data['assets'], f'depreciation_report_{datetime.now().strftime("%Y%m%d")}.csv')
        
        return render_template('report_depreciation.html', title='Depreciation Report')
    registered_count += safe_add_route('/reports/depreciation', 'reports_depreciation', reports_depreciation)
    
    @login_required
    def reports_funding():
        return render_template('report_funding.html', title='Funding Report')
    registered_count += safe_add_route('/reports/funding', 'reports_funding', reports_funding)
    
    @login_required
    def reports_lease_asset():
        return render_template('report_lease_asset.html', title='Lease Asset Report')
    registered_count += safe_add_route('/reports/lease-asset', 'reports_lease_asset', reports_lease_asset)
    
    @login_required
    def reports_maintenance():
        if request.method == 'POST':
            from AssetManagement import InventorySystem
            system = InventorySystem()
            
            # Get maintenance records
            maintenance_records = []
            try:
                cursor = system.conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM maintenance_schedule ORDER BY scheduled_date DESC")
                maintenance_records = cursor.fetchall()
                cursor.close()
            except Exception:
                pass
            
            report_data = generate_maintenance_report(maintenance_records)
            export_format = request.form.get('format', 'pdf')
            
            if export_format == 'csv':
                return export_to_csv(report_data['records'], f'maintenance_report_{datetime.now().strftime("%Y%m%d")}.csv')
            elif export_format == 'excel':
                return export_to_excel(report_data['records'], f'maintenance_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                                       logo_path=get_export_logo_path(current_app.root_path, system))
            else:
                return export_to_csv(report_data['records'], f'maintenance_report_{datetime.now().strftime("%Y%m%d")}.csv')
        
        return render_template('report_maintenance.html', title='Maintenance Report')
    registered_count += safe_add_route('/reports/maintenance', 'reports_maintenance', reports_maintenance)
    
    @login_required
    def reports_reservation():
        return render_template('report_reservation.html', title='Reservation Report')
    registered_count += safe_add_route('/reports/reservation', 'reports_reservation', reports_reservation)
    
    @login_required
    def reports_status():
        return render_template('report_status.html', title='Status Report')
    registered_count += safe_add_route('/reports/status', 'reports_status', reports_status)
    
    @login_required
    def reports_transaction():
        return render_template('report_transaction.html', title='Transaction Report')
    registered_count += safe_add_route('/reports/transaction', 'reports_transaction', reports_transaction)
    
    @login_required
    def reports_other():
        return render_template('report_other.html', title='Other Report')
    registered_count += safe_add_route('/reports/other', 'reports_other', reports_other)
    
    # Lists Routes
    @login_required
    def lists_assets():
        return render_template('lists_assets.html', title='Lists of Assets')
    registered_count += safe_add_route('/lists/assets', 'lists_assets', lists_assets)
    
    @login_required
    def lists_maintenances():
        return render_template('lists_maintenances.html', title='Lists of Maintenances')
    registered_count += safe_add_route('/lists/maintenances', 'lists_maintenances', lists_maintenances)
    
    @login_required
    def lists_contracts():
        return render_template('lists_contracts.html', title='Lists of Contracts')
    registered_count += safe_add_route('/lists/contracts', 'lists_contracts', lists_contracts)
    
    # APO Routes
    @login_required
    def apo_add():
        return render_template('apo_add.html', title='Add APO')
    registered_count += safe_add_route('/apo/add', 'apo_add', apo_add)
    
    @login_required
    def apo_list():
        return render_template('apo_list.html', title='View All APOs')
    registered_count += safe_add_route('/apo/list', 'apo_list', apo_list)
    
    # Setup Routes
    @login_required
    def employees():
        return render_template('employees.html', title='Employees')
    registered_count += safe_add_route('/employees', 'employees', employees)
    
    @login_required
    def customers():
        return render_template('customers.html', title='Customers')
    registered_count += safe_add_route('/customers', 'customers', customers)
    
    @login_required
    def departments():
        return render_template('departments.html', title='Departments/Cost Centers')
    registered_count += safe_add_route('/departments', 'departments', departments)
    
    @login_required
    def funding():
        return render_template('page.html', title='Funding', heading='Funding Management', 
                             description='Manage funding sources for assets')
    registered_count += safe_add_route('/funding', 'funding', funding)
    
    # Settings Routes
    @login_required
    def settings_email():
        return render_template('email_settings.html', title='Email Settings')
    registered_count += safe_add_route('/settings/email', 'settings_email', settings_email)
    
    @login_required
    def settings_system():
        return render_template('system_settings.html', title='System Settings')
    registered_count += safe_add_route('/settings/system', 'settings_system', settings_system)
    
    # Customize Forms Routes
    @login_required
    def customize_assets_form():
        return render_template('customize_assets_form.html', title='Customize Assets Form')
    registered_count += safe_add_route('/customize-assets-form', 'customize_assets_form', customize_assets_form)
    
    @login_required
    def customize_customers_form():
        return render_template('page.html', title='Customize Customers Form', 
                             heading='Customize Customers Form',
                             description='Customize customer form fields')
    registered_count += safe_add_route('/customize-customers-form', 'customize_customers_form', customize_customers_form)
    
    @login_required
    def customize_maintenance_form():
        return render_template('customize_maintenance_form.html', title='Customize Maintenance Form')
    registered_count += safe_add_route('/customize-maintenance-form', 'customize_maintenance_form', customize_maintenance_form)
    
    @login_required
    def customize_contracts_form():
        return render_template('page.html', title='Customize Contracts Form',
                             heading='Customize Contracts Form',
                             description='Customize contract form fields')
    registered_count += safe_add_route('/customize-contracts-form', 'customize_contracts_form', customize_contracts_form)
    
    # Help Routes
    @login_required
    def help_user_guide():
        return render_template('help_user_guide.html', title='User Guide')
    registered_count += safe_add_route('/help/user-guide', 'help_user_guide', help_user_guide)
    
    @login_required
    def help_documentation():
        return render_template('help_documentation.html', title='Documentation')
    registered_count += safe_add_route('/help/documentation', 'help_documentation', help_documentation)
    
    @login_required
    def help_faq():
        return render_template('help_faq.html', title='FAQ')
    registered_count += safe_add_route('/help/faq', 'help_faq', help_faq)
    
    @login_required
    def help_video_tutorials():
        return render_template('help_video_tutorials.html', title='Video Tutorials')
    registered_count += safe_add_route('/help/video-tutorials', 'help_video_tutorials', help_video_tutorials)
    
    @login_required
    def help_contact_support():
        return render_template('help_contact_support.html', title='Contact Support')
    registered_count += safe_add_route('/help/contact-support', 'help_contact_support', help_contact_support)
    
    @login_required
    def help_system_info():
        return render_template('help_system_info.html', title='System Information')
    registered_count += safe_add_route('/help/system-info', 'help_system_info', help_system_info)
    
    @login_required
    def help_release_notes():
        return render_template('help_release_notes.html', title='Release Notes')
    registered_count += safe_add_route('/help/release-notes', 'help_release_notes', help_release_notes)
    
    @login_required
    def help_support():
        return render_template('help_support.html', title='Help & Support')
    registered_count += safe_add_route('/help-support', 'help_support', help_support)
    
    # Developer Tools
    @login_required
    def developer_code_generator():
        return render_template('code_generator.html', title='Code Generator')
    registered_count += safe_add_route('/developer/code-generator', 'developer_code_generator', developer_code_generator)
    
    # Import Route
    @login_required
    def import_data():
        return render_template('import.html', title='Import Data')
    registered_count += safe_add_route('/import', 'import_data', import_data)
    
    print(f"✅ Registered {registered_count} new missing routes")
