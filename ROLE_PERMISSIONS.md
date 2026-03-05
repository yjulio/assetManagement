# User Role Permissions Configuration

## Overview
This document outlines the access permissions for each user role in the Asset Management System.

## User Roles

### 1. Admin
**Full system access** - Can perform all operations

**Permissions:**
- ✅ Create, edit, and delete users
- ✅ Assign users to groups/roles
- ✅ View, add, edit, and delete assets
- ✅ Manage suppliers
- ✅ System configuration and settings
- ✅ Database backup and restore
- ✅ All reports (inventory, financial, depreciation, audit, etc.)
- ✅ Asset assignment and tracking
- ✅ Bulk operations
- ✅ Export data

### 2. Asset Officer
**Asset and inventory management** - Regular operations

**Permissions:**
- ✅ View all assets and inventory
- ✅ Add new assets
- ✅ Edit existing assets
- ✅ Assign assets to departments/locations
- ✅ Delete assets (single or bulk)
- ✅ View and manage suppliers
- ✅ View inventory reports
- ✅ View asset reports
- ❌ Create or manage users
- ❌ System configuration
- ❌ Database operations

### 3. Finance Officer
**Financial reporting and analysis** - Read-only with financial focus

**Permissions:**
- ✅ View all assets (including prices)
- ✅ View asset pricing information
- ✅ View depreciation calculations
- ✅ Access depreciation reports
- ✅ Access funding reports
- ✅ View inventory reports (with values)
- ✅ View asset reports (with financial data)
- ✅ View suppliers
- ❌ Add, edit, or delete assets
- ❌ Assign assets
- ❌ Create or manage users
- ❌ System configuration

## Key Route Protections

### Asset Management
- `/assets` - Admin, Asset Officer, Finance Officer
- `/view-asset/<name>` - Admin, Asset Officer, Finance Officer
- `/add` - Admin, Asset Officer
- `/edit-asset/<name>` - Admin, Asset Officer
- `/assign-asset/<name>` - Admin, Asset Officer
- `/delete-asset/<name>` - Admin, Asset Officer
- `/delete-selected-assets` - Admin, Asset Officer

### Reports
- `/reports/inventory` - Admin, Finance Officer, Asset Officer
- `/reports/asset` - Admin, Finance Officer, Asset Officer
- `/reports/depreciation` - Admin, Finance Officer
- `/reports/funding` - Admin, Finance Officer

### User Management
- `/users` - Admin only
- `/assign-group` - Admin only
- `/users/delete/<username>` - Admin only

### Suppliers
- `/suppliers` - Admin, Asset Officer, Finance Officer

### System Administration
- `/settings` - Admin only
- `/backup` - Admin only
- `/restore` - Admin only
- `/audit-log` - Admin only

## Login Requirements

All routes require authentication except:
- `/login` - Public
- `/landing` - Public (shows login form)

## Implementation Notes

The system uses the `@require_group()` decorator to enforce role-based access control:
```python
@require_group('Admin', 'Asset Officer', 'Finance Officer')
```

Users assigned to any of the specified groups will have access to the route.

## Creating Users with Roles

1. **Admin logs in**
2. Navigate to **Users** page
3. Create new user (username, email, password)
4. Navigate to **Assign Group** page
5. Select user and assign appropriate role:
   - Admin
   - Asset Officer
   - Finance Officer

## Database Structure

Roles are stored in the `groups` table:
```sql
SELECT * FROM `groups`;
+----+-----------------+-----------------------------------------------------------------------------+
| id | name            | description                                                                 |
+----+-----------------+-----------------------------------------------------------------------------+
|  1 | Admin           | Administrator group with full access                                        |
|  2 | Asset Officer   | Regular user role for managing assets and inventory                         |
|  3 | Finance Officer | Finance role with access to asset pricing, depreciation, and financial data |
+----+-----------------+-----------------------------------------------------------------------------+
```

User-role associations are stored in the `user_groups` table with foreign keys to both `users` and `groups`.
