# Route Configuration and Navigation Guide

## Overview

The Asset Management System has been configured with a comprehensive routing structure and role-based navigation system.

## Database Configuration

### Connection Pooling

The database now uses connection pooling for improved performance and reliability:

- **Location**: `src/db/connection.py`
- **Pool Size**: 10 connections (configurable via `DB_POOL_SIZE` environment variable)
- **Features**:
  - Automatic connection management
  - Connection reuse for better performance
  - Built-in error handling and recovery
  - Context manager support for safe database operations

### Usage Example

```python
from db.connection import get_db_cursor

# Using context manager (recommended)
with get_db_cursor(dictionary=True) as cursor:
    cursor.execute("SELECT * FROM assets")
    results = cursor.fetchall()
    # Automatic commit and connection cleanup
```

## Route Organization

### Current Structure

All routes are currently in `/home/assetManagement/src/app.py` (5184 lines). The system has been enhanced with:

1. **Database Connection Pooling**: Initialized at application startup
2. **Navigation System**: Role-based menu filtering
3. **Route Blueprints**: Prepared for future modularization

### Blueprint Structure (Prepared for Migration)

```
src/routes/
├── __init__.py          # Blueprint registration
├── main.py              # Landing page, dashboard
├── auth.py              # Login, logout, profile
├── assets.py            # Asset CRUD operations  
├── users.py             # User management
├── locations.py         # Location management
├── database.py          # Backup, restore, maintenance
├── contracts.py         # Contract management
└── reports.py           # Report generation
```

## Navigation System

### Role-Based Navigation

The navigation menu is now role-based and automatically filters menu items based on user permissions.

**Configuration**: `src/utils/navigation.py`

**Supported Roles**:
- `Admin`: Full system access
- `Manager`: Management operations
- `User`: Basic user operations
- `viewer`: Read-only access

### Menu Structure

```python
{
    'id': 'menu_id',
    'label': 'Menu Label',
    'icon': '🏠',
    'roles': ['Admin', 'Manager'],  # Who can see this menu
    'submenu': [...]  # Nested menu items
}
```

### Template Integration

The navigation menu is automatically injected into all templates via context processor:

```jinja2
{% for item in navigation_menu %}
    <li class="menu-item">
        <a href="#">{{ item.icon }} {{ item.label }}</a>
        {% if item.submenu %}
        <ul class="submenu">
            {% for subitem in item.submenu %}
            <li><a href="{{ subitem.url }}">{{ subitem.icon }} {{ subitem.label }}</a></li>
            {% endfor %}
        </ul>
        {% endif %}
    </li>
{% endfor %}
```

## Main Routes

### Authentication Routes
- `GET/POST /login` - User login
- `GET/POST /logout` - User logout
- `GET /profile` - View profile
- `GET/POST /change-profile` - Edit profile
- `GET /account-details` - Account information
- `GET /uploads/<filename>` - Serve uploaded files

### Dashboard Routes
- `GET /` - Main dashboard
- `GET /landing` - Public landing page
- `GET/POST /manage-dashboard` - Configure dashboard widgets

### Asset Management Routes
- `GET /assets` - List all assets
- `GET/POST /add` - Add new asset
- `GET/POST /update` - Update asset quantity
- `GET/POST /checkout` - Check out asset
- `GET/POST /checkin` - Check in asset
- `GET/POST /lease` - Lease asset
- `GET/POST /lease-return` - Return leased asset
- `GET/POST /maintenance` - Asset maintenance
- `GET/POST /move` - Move asset location
- `GET/POST /reserve` - Reserve asset
- `GET/POST /dispose` - Dispose of asset

### User Management Routes
- `GET/POST /users` - Manage users
- `POST /users/delete/<username>` - Delete user
- `GET/POST /groups` - Manage groups
- `GET/POST /assign-group` - Assign user to group

### Location Management Routes
- `GET /locations` - List locations
- `POST /locations/add` - Add location
- `GET/POST /locations/edit/<id>` - Edit location
- `POST /locations/delete/<id>` - Delete location
- `GET /categories` - List categories
- `GET /subcategories` - List subcategories

### Database Management Routes
- `GET /database` - Database management dashboard
- `GET /backup-restore` - Backup and restore interface
- `POST /backup/sql` - Create SQL backup
- `POST /restore/sql` - Restore from SQL backup
- `POST /database/optimize` - Optimize database
- `POST /database/check` - Check database integrity
- `POST /database/repair` - Repair database
- `POST /database/settings` - Update database settings

### Contract Management Routes
- `GET /contracts` - Contract dashboard
- `GET/POST /contracts/add` - Add new contract
- `POST /contracts/upload` - Upload contract document
- `GET /contracts/list` - List all contracts
- `GET /contracts/renewals` - Upcoming renewals
- `GET /contracts/expired` - Expired contracts
- `GET /contracts/licenses` - Software licenses

### Report Routes
- `GET /reports/*` - Various report types
- `GET /data-quality` - Data quality dashboard
- `POST /data-quality/clean` - Clean data
- `POST /data-quality/enrich` - Enrich data

### System Configuration Routes
- `GET/POST /company-info` - Company information
- `GET/POST /settings/email` - Email settings
- `GET/POST /settings/system` - System settings
- `GET/POST /suppliers` - Supplier management

## Role-Based Access Control

### Decorator Usage

```python
@app.route('/some-route')
@require_group('Admin', 'Manager')
def some_route():
    # Only accessible by Admin or Manager
    pass
```

### Available Decorators

1. **`@login_required`**: Requires any authenticated user
2. **`@require_group(*groups)`**: Requires user to belong to specific group(s)

## Environment Configuration

### Database Settings (`.env` file)
```bash
DB_HOST=localhost
DB_USER=user_asset
DB_PASSWORD=your_password
DB_NAME=db_asset
DB_PORT=3306
DB_POOL_SIZE=10  # Connection pool size
```

### Flask Settings
```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False  # Set to False in production
SECRET_KEY=your-secret-key-here
SESSION_LIFETIME=3600  # Session timeout in seconds
```

## Testing Routes

### Check Database Connection
```bash
cd /home/assetManagement
python3 test_db.py
```

### Start Application
```bash
cd /home/assetManagement/src
python3 app.py
```

### Access Routes
- Landing Page: http://localhost:5000/landing
- Dashboard: http://localhost:5000/ (requires login)
- Login: http://localhost:5000/login

## Security Features

1. **CSRF Protection**: All POST requests require CSRF token
2. **Session Management**: Secure session cookies with configurable timeout
3. **Password Hashing**: Passwords stored with Werkzeug security
4. **Role-Based Access**: All routes protected by role-based decorators
5. **SQL Injection Prevention**: Parameterized queries throughout
6. **Connection Pooling**: Prevents connection exhaustion attacks

## Performance Optimizations

1. **Connection Pooling**: Reuses database connections
2. **Session Caching**: User data cached in session
3. **Lazy Loading**: Dashboard widgets loaded on demand
4. **Query Optimization**: Efficient database queries with proper indexing

## Troubleshooting

### Database Connection Issues
```python
# Test connection
from db.connection import test_connection
from config import DB_CONFIG

if test_connection(DB_CONFIG):
    print("Connection successful!")
else:
    print("Connection failed!")
```

### Check Routes
```bash
# List all registered routes
cd /home/assetManagement/src
python3 -c "from app import app; print('\\n'.join([str(rule) for rule in app.url_map.iter_rules()]))"
```

### Debug Mode
Set in `.env`:
```bash
FLASK_DEBUG=True
```

## Migration Plan (Future)

To migrate from monolithic app.py to blueprint structure:

1. Routes remain functional in app.py
2. Gradually move route groups to blueprints
3. Update URL references in templates
4. Test each migration thoroughly
5. Remove legacy routes once verified

## Documentation Updates

- [ ] Update API documentation
- [ ] Create route testing suite
- [ ] Document all role permissions
- [ ] Create admin user guide
- [ ] Update deployment documentation

## Support

For issues or questions:
1. Check application logs: `/var/log/assetmanagement/`
2. Review error templates: `/home/assetManagement/src/templates/errors/`
3. Test database connectivity
4. Verify environment configuration
