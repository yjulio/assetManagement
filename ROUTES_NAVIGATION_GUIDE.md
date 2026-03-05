# Routes and Navigation Configuration Guide

## Overview
This document describes the reorganized route structure and navigation system for the Asset Management application.

## Route Structure

The application routes are now organized into logical blueprints for better maintainability:

### 1. Main Routes (`routes/main.py`)
- `/` - Dashboard (index)
- `/landing` - Public landing page
- `/dashboard` - Dashboard alias
- `/dashboard/export/<format>` - Export dashboard data

### 2. Authentication Routes (`routes/auth.py`)
Prefix: `/auth`
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/profile` - View profile
- `/auth/change-profile` - Update profile
- `/auth/account-details` - Account details
- `/auth/uploads/<filename>` - Serve uploaded files

### 3. Assets Routes (`routes/assets.py`)
Prefix: `/assets`
- `/assets` - List all assets
- `/assets/add` - Add new asset
- `/assets/update` - Update asset quantity
- `/assets/checkout` - Check out asset
- `/assets/checkin` - Check in asset
- `/assets/lease` - Lease asset
- `/assets/lease-return` - Return leased asset
- `/assets/maintenance` - Asset maintenance
- `/assets/move` - Move asset
- `/assets/reserve` - Reserve asset
- `/assets/dispose` - Dispose asset

### 4. Users & Groups Routes (`routes/users.py`)
Prefix: `/users`
- `/users` - List users
- `/users/add` - Add new user
- `/users/delete/<username>` - Delete user
- `/users/assign-group` - Assign user to group
- `/users/groups` - Manage groups

### 5. Locations Routes (`routes/locations.py`)
Prefix: `/locations`
- `/locations` - List locations
- `/locations/add` - Add location
- `/locations/edit/<id>` - Edit location
- `/locations/delete/<id>` - Delete location
- `/locations/categories` - Manage categories
- `/locations/subcategories` - Manage subcategories

### 6. Database Routes (`routes/database.py`)
Prefix: `/database`
- `/database` - Database management dashboard
- `/database/backup` - Create backup
- `/database/restore` - Restore from backup
- `/database/optimize` - Optimize database
- `/database/check` - Check database integrity
- `/database/repair` - Repair database tables
- `/database/settings` - Database settings

### 7. Contracts Routes (`routes/contracts.py`)
Prefix: `/contracts`
- `/contracts` - Contracts dashboard
- `/contracts/add` - Add new contract
- `/contracts/list` - List all contracts
- `/contracts/renewals` - Upcoming renewals
- `/contracts/expired` - Expired contracts
- `/contracts/licenses` - Software licenses
- `/contracts/upload` - Upload contract document

### 8. Reports Routes (`routes/reports.py`)
Prefix: `/reports`
- `/reports/automated` - Automated reports
- `/reports/custom` - Custom report builder
- `/reports/inventory` - Inventory report
- `/reports/asset` - Asset report
- `/reports/audit` - Audit report
- `/reports/checkout` - Checkout report
- `/reports/contract` - Contract report
- `/reports/depreciation` - Depreciation report
- `/reports/maintenance` - Maintenance report
- And more...

## Database Connection Pooling

The database connection has been upgraded to use MySQL connection pooling for better performance and reliability.

### Configuration
Connection pool is configured in `src/config.py`:
```python
DB_CONFIG = {
    "pool_name": "asset_pool",
    "pool_size": 10,  # Adjust based on your needs
    "pool_reset_session": True,
    ...
}
```

### Usage
```python
from db.connection import get_db_cursor

# Using context manager (recommended)
with get_db_cursor(dictionary=True) as cursor:
    cursor.execute("SELECT * FROM assets")
    results = cursor.fetchall()
    # Connection automatically committed and closed
```

## Navigation System

### Role-Based Navigation
The navigation menu is now dynamically generated based on user roles defined in `src/utils/navigation.py`.

### User Roles
- **Admin**: Full access to all features
- **Manager**: Access to most features except user management and system settings
- **User**: Access to view and basic operations
- **Viewer**: Read-only access

### Navigation Configuration
The navigation structure is defined in `NAVIGATION_MENU` in `src/utils/navigation.py`. Each menu item includes:
- `label`: Display name
- `icon`: Emoji icon
- `url`: Route URL
- `roles`: List of roles that can access this item
- `submenu`: Optional nested menu items

### Template Integration
Navigation is automatically injected into all templates via context processor:
```html
{% for item in navigation_menu %}
  <li>
    <a href="{{ item.url }}">{{ item.icon }} {{ item.label }}</a>
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

## Implementation Status

### Completed
- ✅ Routes package structure created
- ✅ Blueprint files created for all route categories
- ✅ Database connection pooling implemented
- ✅ Navigation configuration system created
- ✅ Main routes blueprint completed
- ✅ Authentication routes blueprint completed
- ✅ Role-based navigation filtering

### In Progress
- 🔄 Migrating routes from app.py to blueprints
- 🔄 Updating templates to use new route structure

### To Do
- ⏳ Complete asset routes implementation
- ⏳ Complete user management routes
- ⏳ Complete location routes
- ⏳ Complete database management routes
- ⏳ Complete contracts routes
- ⏳ Complete reports routes
- ⏳ Update all template links to use url_for with blueprint names
- ⏳ Test all routes and navigation
- ⏳ Create migration guide for existing data

## Migration Guide

### For Developers

1. **Update Template Links**
   Old: `<a href="/login">Login</a>`
   New: `<a href="{{ url_for('auth.login') }}">Login</a>`

2. **Update Redirects**
   Old: `redirect('/dashboard')`
   New: `redirect(url_for('main.index'))`

3. **Import Blueprints**
   ```python
   from routes.auth import auth_bp
   app.register_blueprint(auth_bp, url_prefix='/auth')
   ```

### URL Changes

Most URLs will remain the same, but some will have new prefixes:
- `/login` → `/auth/login`
- `/logout` → `/auth/logout`
- `/profile` → `/auth/profile`

For backward compatibility, you can add URL rules:
```python
app.add_url_rule('/login', view_func=lambda: redirect(url_for('auth.login')))
```

## Benefits of New Structure

1. **Better Organization**: Routes grouped by functionality
2. **Easier Maintenance**: Smaller, focused files instead of one 5000+ line file
3. **Role-Based Security**: Navigation automatically filtered by user role
4. **Scalability**: Easy to add new routes and features
5. **Performance**: Connection pooling improves database performance
6. **Testability**: Blueprints are easier to test in isolation
7. **Code Reuse**: Shared decorators and utilities in each blueprint

## Configuration Files

- `src/config.py` - Main application configuration
- `src/app_factory.py` - Application factory and initialization
- `src/db/connection.py` - Database connection management
- `src/utils/navigation.py` - Navigation configuration
- `src/routes/__init__.py` - Blueprint registration

## Next Steps

1. Complete migration of routes from app.py to blueprints
2. Update all templates to use blueprint-aware URL generation
3. Add backward compatibility routes if needed
4. Test all functionality
5. Update deployment scripts
6. Create user documentation for new features
