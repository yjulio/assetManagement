# 🤖 Automatic Code Generator

Generate complete CRUD operations automatically from your database schema!

## 🌟 Features

- **Automatic Route Generation**: Creates Flask routes for Create, Read, Update, Delete operations
- **Template Generation**: Generates Bootstrap-styled HTML templates with forms and tables
- **Type-Safe**: Automatically detects column types and creates appropriate input fields
- **Validation**: Includes CSRF protection, required field validation, and error handling
- **Modern UI**: Uses Bootstrap 5 with responsive design and modern styling
- **CLI & Web Interface**: Use via command line or through web interface

## 🚀 Quick Start

### Web Interface (Recommended)

1. Login as Admin
2. Navigate to **Developer Tools** → **Code Generator** in the sidebar
3. Select a table from the dropdown
4. Choose what to generate (Routes, Templates, or both)
5. Click "Generate Code"
6. Copy the code or save files directly to disk!

### Command Line Interface

```bash
# Generate everything for a table
./generate.py employees --all

# Generate only routes
./generate.py departments --routes --save

# Generate only templates
./generate.py inventory --templates

# View all options
./generate.py
```

## 📋 What Gets Generated?

### Flask Routes (4 routes per table)

1. **List Route** (`/table_name`): Display all records with pagination
2. **Add Route** (`/table_name/add`): Form to create new records
3. **Edit Route** (`/table_name/edit/<id>`): Form to update existing records
4. **Delete Route** (`/table_name/delete/<id>`): Delete with confirmation

### HTML Templates (2-3 templates per table)

1. **Add Template** (`table_name_add.html`): Form with all fields
2. **List Template** (`table_name_list.html`): Table view with actions
3. **Edit Template** (`table_name_edit.html`): Pre-filled form

## 🎯 Example Usage

### Generate Code for "employees" Table

```bash
./generate.py employees --all
```

This creates:
- `src/generated_routes_employees.py` - 4 Flask routes
- `src/templates/employees_add.html` - Add form
- `src/templates/employees_list.html` - List view

### Generated Routes Include:

```python
@app.route('/employees')
def employees():
    """List all employees"""
    # List logic here

@app.route('/employees/add', methods=['GET', 'POST'])
def add_employees():
    """Add new employee"""
    # Add logic here

@app.route('/employees/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_employees(record_id):
    """Edit employee"""
    # Edit logic here

@app.route('/employees/delete/<int:record_id>', methods=['POST'])
def delete_employees(record_id):
    """Delete employee"""
    # Delete logic here
```

## 🔧 How It Works

1. **Schema Detection**: Connects to database and reads table structure
2. **Type Mapping**: Maps MySQL types to appropriate HTML input types
   - `VARCHAR` → `<input type="text">`
   - `INT` → `<input type="number">`
   - `DATE` → `<input type="date">`
   - `TEXT` → `<textarea>`
   - Email fields → `<input type="email">`
   - Phone fields → `<input type="tel">`

3. **Code Generation**: Creates routes and templates with:
   - Form validation
   - CSRF tokens
   - Error handling
   - Flash messages
   - Responsive design

## 📚 Integration Steps

1. **Generate Code**: Use web interface or CLI
2. **Copy Routes**: Add generated routes to `src/app.py`
3. **Templates**: Already saved to `src/templates/` if using --save
4. **Test**: Restart Flask and navigate to new routes
5. **Customize**: Modify generated code as needed

## ⚙️ Configuration

The generator uses your existing database configuration from `src/config.py`:

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_asset'
}
```

## 🎨 Customization

Generated code is fully customizable:

- **Routes**: Add authentication, custom validation, business logic
- **Templates**: Modify HTML, add JavaScript, change styling
- **Fields**: Hide/show fields, add custom input types
- **Actions**: Add export, import, bulk operations

## 🔒 Security Features

All generated code includes:

- ✅ CSRF token validation
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection (Jinja2 auto-escaping)
- ✅ Authentication required decorators
- ✅ Input validation

## 💡 Pro Tips

1. **Start Simple**: Generate code, then customize incrementally
2. **Version Control**: Commit generated code before modifications
3. **Test First**: Always test generated routes before customization
4. **Backup**: Keep generated files as reference
5. **Iterate**: Use generator for new tables, then refine

## 📊 Supported Field Types

| MySQL Type | HTML Input | Notes |
|------------|------------|-------|
| INT, BIGINT | number | Min/max validation |
| VARCHAR | text | Length validation |
| TEXT | textarea | Multi-line input |
| DATE | date | Date picker |
| DATETIME | datetime-local | Date + time |
| DECIMAL | number | Step=0.01 for decimals |
| ENUM | select | Dropdown from options |
| EMAIL fields | email | Email validation |
| PHONE fields | tel | Phone format |

## 🚨 Limitations

- Does not generate complex relationships (foreign keys shown as IDs)
- File uploads require manual implementation
- Complex validation rules need custom code
- Assumes standard primary key naming (id)

## 🔄 Workflow Example

```bash
# 1. Generate code for new feature
./generate.py products --all

# 2. Copy routes to app.py
cat src/generated_routes_products.py >> src/app.py

# 3. Restart Flask
# Flask auto-reloads if in debug mode

# 4. Test
# Navigate to http://yourserver/products

# 5. Customize as needed
# Edit templates and routes
```

## 🎓 Learning Resource

The generated code follows best practices and can serve as:

- **Learning Tool**: See how CRUD operations work
- **Template**: Use as starting point for custom features
- **Reference**: Copy patterns to other parts of app
- **Time Saver**: Focus on business logic, not boilerplate

## 🤝 Contributing

To improve the generator:

1. Edit `src/utils/code_generator.py`
2. Add new templates or improve existing ones
3. Test with different table structures
4. Submit improvements

## 📞 Support

- **Documentation**: `/help/documentation`
- **FAQ**: `/help/faq`
- **Contact**: Use Help & Support menu

## 🎉 Examples of What You Can Build

With the code generator, you can quickly create:

- Employee management system
- Product catalog
- Customer database
- Order tracking
- Project management
- Ticketing system
- Content management
- Any CRUD application!

## ⚡ Performance

- **Fast**: Generates code in seconds
- **Efficient**: Creates optimized SQL queries
- **Scalable**: Works with tables of any size
- **Reliable**: Tested with various schemas

---

**Made with ❤️ for rapid development**

*Save time. Write less code. Focus on what matters.*
