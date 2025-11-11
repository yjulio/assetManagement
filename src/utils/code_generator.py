"""
Automatic Code Generator for Asset Management System
Generates CRUD routes, forms, and templates based on database schema
"""

import mysql.connector
from typing import Dict, List, Tuple
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set Flask to debug mode for config loading
os.environ['FLASK_DEBUG'] = 'true'

try:
    from config import DB_CONFIG as DATABASE_CONFIG
except:
    # Fallback simple config
    DATABASE_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'db_asset',
        'port': 3306
    }


class CodeGenerator:
    """Generate CRUD code automatically from database schema"""
    
    def __init__(self):
        self.conn = mysql.connector.connect(**DATABASE_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get column information for a table"""
        self.cursor.execute(f"DESCRIBE {table_name}")
        return self.cursor.fetchall()
    
    def get_all_tables(self) -> List[str]:
        """Get all table names in database"""
        self.cursor.execute("SHOW TABLES")
        return [list(row.values())[0] for row in self.cursor.fetchall()]
    
    def python_type_from_mysql(self, mysql_type: str) -> str:
        """Convert MySQL type to Python type hint"""
        type_map = {
            'int': 'int',
            'varchar': 'str',
            'text': 'str',
            'date': 'str',
            'datetime': 'str',
            'timestamp': 'str',
            'decimal': 'float',
            'tinyint': 'bool',
            'enum': 'str'
        }
        
        base_type = mysql_type.split('(')[0].lower()
        return type_map.get(base_type, 'str')
    
    def generate_form_field(self, column: Dict) -> str:
        """Generate HTML form field based on column type"""
        field_name = column['Field']
        field_type = column['Type']
        is_required = 'YES' if column['Null'] == 'NO' else ''
        
        # Skip auto-increment and timestamp fields
        if column['Extra'] in ['auto_increment', 'DEFAULT_GENERATED on update CURRENT_TIMESTAMP']:
            return ""
        
        # Determine input type
        if 'int' in field_type:
            input_type = 'number'
        elif 'date' in field_type:
            input_type = 'date'
        elif 'email' in field_name.lower():
            input_type = 'email'
        elif 'phone' in field_name.lower():
            input_type = 'tel'
        elif 'text' in field_type:
            return f'''        <div class="form-group">
            <label for="{field_name}">{field_name.replace('_', ' ').title()}{' *' if is_required else ''}</label>
            <textarea id="{field_name}" name="{field_name}" rows="3" {'required' if is_required else ''}></textarea>
        </div>'''
        else:
            input_type = 'text'
        
        return f'''        <div class="form-group">
            <label for="{field_name}">{field_name.replace('_', ' ').title()}{' *' if is_required else ''}</label>
            <input type="{input_type}" id="{field_name}" name="{field_name}" {'required' if is_required else ''}>
        </div>'''
    
    def generate_add_route(self, table_name: str, columns: List[Dict]) -> str:
        """Generate Flask route for adding records"""
        
        # Get non-auto fields
        fields = [col for col in columns if col['Extra'] != 'auto_increment' and 
                  (col['Default'] is None or 'CURRENT_TIMESTAMP' not in str(col['Default']))]
        field_names = [col['Field'] for col in fields]
        
        # Generate form data extraction
        form_extracts = []
        for col in fields:
            field_name = col['Field']
            form_extracts.append(f"        {field_name} = request.form.get('{field_name}', '').strip()")
        
        # Generate INSERT statement
        columns_str = ', '.join(field_names)
        placeholders = ', '.join(['%s'] * len(field_names))
        values_str = ', '.join(field_names)
        
        route_code = f'''
@app.route('/{table_name}/add', methods=['GET', 'POST'])
@login_required
def add_{table_name}():
    """Add new {table_name} record"""
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('{table_name}'))
        
        try:
{chr(10).join(form_extracts)}
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
            """, ({values_str}))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Record added successfully', 'success')
            return redirect(url_for('{table_name}'))
            
        except Exception as e:
            flash(f'Error adding record: {{str(e)}}', 'error')
            return redirect(url_for('add_{table_name}'))
    
    return render_template('{table_name}_add.html', title='Add {table_name.title()}')
'''
        return route_code
    
    def generate_edit_route(self, table_name: str, columns: List[Dict]) -> str:
        """Generate Flask route for editing records"""
        
        # Find primary key
        pk_field = next((col['Field'] for col in columns if col['Key'] == 'PRI'), 'id')
        
        # Get non-auto fields
        fields = [col for col in columns if col['Extra'] != 'auto_increment' and 
                  (col['Default'] is None or 'CURRENT_TIMESTAMP' not in str(col['Default']))]
        field_names = [col['Field'] for col in fields]
        
        # Generate UPDATE SET clause
        set_clause = ', '.join([f"{field} = %s" for field in field_names])
        
        route_code = f'''
@app.route('/{table_name}/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_{table_name}(record_id):
    """Edit {table_name} record"""
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('{table_name}'))
        
        try:
            {chr(10).join([f"            {field} = request.form.get('{field}', '').strip()" for field in field_names])}
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE {table_name} 
                SET {set_clause}
                WHERE {pk_field} = %s
            """, ({', '.join(field_names)}, record_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Record updated successfully', 'success')
            return redirect(url_for('{table_name}'))
            
        except Exception as e:
            flash(f'Error updating record: {{str(e)}}', 'error')
            return redirect(url_for('edit_{table_name}', record_id=record_id))
    
    # GET request - load record
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM {table_name} WHERE {pk_field} = %s", (record_id,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if record:
            return render_template('{table_name}_edit.html', record=record, title='Edit {table_name.title()}')
        else:
            flash('Record not found', 'error')
            return redirect(url_for('{table_name}'))
    except Exception as e:
        flash(f'Error loading record: {{str(e)}}', 'error')
        return redirect(url_for('{table_name}'))
'''
        return route_code
    
    def generate_list_route(self, table_name: str, columns: List[Dict]) -> str:
        """Generate Flask route for listing records"""
        
        route_code = f'''
@app.route('/{table_name}')
@login_required
def {table_name}():
    """List all {table_name} records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM {table_name} ORDER BY id DESC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('{table_name}_list.html', records=records, title='{table_name.title()}')
    except Exception as e:
        flash(f'Error loading records: {{str(e)}}', 'error')
        return render_template('{table_name}_list.html', records=[], title='{table_name.title()}')
'''
        return route_code
    
    def generate_delete_route(self, table_name: str, columns: List[Dict]) -> str:
        """Generate Flask route for deleting records"""
        
        pk_field = next((col['Field'] for col in columns if col['Key'] == 'PRI'), 'id')
        
        route_code = f'''
@app.route('/{table_name}/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_{table_name}(record_id):
    """Delete {table_name} record"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('{table_name}'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM {table_name} WHERE {pk_field} = %s", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Record deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting record: {{str(e)}}', 'error')
    
    return redirect(url_for('{table_name}'))
'''
        return route_code
    
    def generate_all_routes(self, table_name: str) -> str:
        """Generate complete CRUD routes for a table"""
        columns = self.get_table_schema(table_name)
        
        code = f"# Auto-generated CRUD routes for {table_name}\n"
        code += self.generate_list_route(table_name, columns)
        code += self.generate_add_route(table_name, columns)
        code += self.generate_edit_route(table_name, columns)
        code += self.generate_delete_route(table_name, columns)
        
        return code
    
    def generate_add_template(self, table_name: str) -> str:
        """Generate HTML template for add form"""
        columns = self.get_table_schema(table_name)
        
        form_fields = []
        for col in columns:
            field_html = self.generate_form_field(col)
            if field_html:
                form_fields.append(field_html)
        
        template = f'''{{%extends 'base.html'%}}
{{%block content%}}
<div class="content-header">
    <h2>➕ Add {table_name.replace('_', ' ').title()}</h2>
    <p>Create a new {table_name} record</p>
</div>

<div class="card-modern">
    <form method="POST" action="{{{{url_for('add_{table_name}')}}}}" class="form-grid">
        <input type="hidden" name="csrf_token" value="{{{{generate_csrf_token()}}}}">
        
{chr(10).join(form_fields)}
        
        <div class="form-actions" style="grid-column: 1 / -1;">
            <button type="submit" class="btn-primary-modern">➕ Add Record</button>
            <a href="{{{{url_for('{table_name}')}}}}" class="btn-secondary-modern">Cancel</a>
        </div>
    </form>
</div>
{{%endblock%}}
'''
        return template
    
    def generate_list_template(self, table_name: str) -> str:
        """Generate HTML template for list view"""
        columns = self.get_table_schema(table_name)
        
        # Generate table headers
        headers = []
        for col in columns:
            if col['Extra'] != 'auto_increment' or col['Field'] == 'id':
                headers.append(f"            <th>{col['Field'].replace('_', ' ').title()}</th>")
        headers.append("            <th>Actions</th>")
        
        # Generate table cells
        cells = []
        for col in columns:
            if col['Extra'] != 'auto_increment' or col['Field'] == 'id':
                cells.append(f"            <td>{{{{record.{col['Field']} or '-'}}}}</td>")
        
        template = f'''{{%extends 'base.html'%}}
{{%block content%}}
<div class="content-header">
    <h2>📋 {table_name.replace('_', ' ').title()}</h2>
    <div>
        <a href="{{{{url_for('add_{table_name}')}}}}" class="btn-primary-modern">➕ Add New</a>
    </div>
</div>

<div class="card-modern">
    {{%if records%}}
    <div class="table-responsive">
        <table class="table-modern">
            <thead>
                <tr>
{chr(10).join(headers)}
                </tr>
            </thead>
            <tbody>
                {{%for record in records%}}
                <tr>
{chr(10).join(cells)}
                    <td>
                        <a href="{{{{url_for('edit_{table_name}', record_id=record.id)}}}}" class="btn-sm btn-primary-modern">✏️ Edit</a>
                        <form method="POST" action="{{{{url_for('delete_{table_name}', record_id=record.id)}}}}" style="display:inline;" onsubmit="return confirm('Are you sure?');">
                            <input type="hidden" name="csrf_token" value="{{{{generate_csrf_token()}}}}">
                            <button type="submit" class="btn-sm btn-danger-modern">🗑️ Delete</button>
                        </form>
                    </td>
                </tr>
                {{%endfor%}}
            </tbody>
        </table>
    </div>
    {{%else%}}
    <div class="alert alert-info-modern">
        No records found. <a href="{{{{url_for('add_{table_name}')}}}}">Add the first one</a>
    </div>
    {{%endif%}}
</div>
{{%endblock%}}
'''
        return template
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Command-line interface for code generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CRUD code automatically')
    parser.add_argument('table', help='Table name to generate code for')
    parser.add_argument('--routes', action='store_true', help='Generate route code')
    parser.add_argument('--templates', action='store_true', help='Generate template files')
    parser.add_argument('--all', action='store_true', help='Generate everything')
    
    args = parser.parse_args()
    
    generator = CodeGenerator()
    
    try:
        if args.all or args.routes:
            print(f"\n{'='*80}")
            print(f"ROUTES FOR {args.table}")
            print(f"{'='*80}")
            print(generator.generate_all_routes(args.table))
        
        if args.all or args.templates:
            print(f"\n{'='*80}")
            print(f"ADD TEMPLATE FOR {args.table}")
            print(f"{'='*80}")
            print(generator.generate_add_template(args.table))
            
            print(f"\n{'='*80}")
            print(f"LIST TEMPLATE FOR {args.table}")
            print(f"{'='*80}")
            print(generator.generate_list_template(args.table))
    
    finally:
        generator.close()


if __name__ == '__main__':
    main()
