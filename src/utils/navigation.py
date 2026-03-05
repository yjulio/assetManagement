"""Navigation configuration for role-based menus
This module defines the navigation structure with role-based access control
"""

# Navigation structure with role-based permissions
NAVIGATION_MENU = [
    {
        'id': 'dashboard',
        'label': 'Dashboard',
        'icon': '🏠',
        'roles': ['Admin', 'Manager', 'User', 'viewer'],
        'submenu': [
            {
                'label': 'View Dashboard',
                'icon': '📊',
                'url': '/',
                'roles': ['Admin', 'Manager', 'User', 'viewer']
            },
            {
                'label': 'Manage Dashboard',
                'icon': '⚙️',
                'url': '/manage-dashboard',
                'roles': ['Admin', 'Manager']
            }
        ]
    },
    {
        'id': 'alerts',
        'label': 'Alerts',
        'icon': '🔔',
        'badge': '!',
        'roles': ['Admin', 'Manager', 'User'],
        'submenu': [
            {'label': 'Assets Past Due', 'icon': '⏰', 'url': '/alerts/assets-past-due', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Contracts Expiring', 'icon': '📄', 'url': '/alerts/contracts-expiring', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Leases Expiring', 'icon': '🏢', 'url': '/alerts/leases-expiring', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Maintenance Due', 'icon': '🔧', 'url': '/alerts/maintenance-due', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Maintenance Overdue', 'icon': '⚠️', 'url': '/alerts/maintenance-overdue', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Warranties Expiring', 'icon': '🛡️', 'url': '/alerts/warranties-expiring', 'roles': ['Admin', 'Manager', 'User']}
        ]
    },
    {
        'id': 'assets',
        'label': 'Assets',
        'icon': '📦',
        'roles': ['Admin', 'Manager', 'User'],
        'submenu': [
            {'label': 'List of Assets', 'icon': '📋', 'url': '/assets', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Add an Asset', 'icon': '➕', 'url': '/add', 'roles': ['Admin', 'Manager']},
            {'label': 'Update Quantity', 'icon': '🔄', 'url': '/update', 'roles': ['Admin', 'Manager']},
            {'label': 'Check Out', 'icon': '📤', 'url': '/checkout', 'roles': ['Admin', 'Manager']},
            {'label': 'Check In', 'icon': '📥', 'url': '/checkin', 'roles': ['Admin', 'Manager']},
            {'label': 'Lease', 'icon': '📝', 'url': '/lease', 'roles': ['Admin', 'Manager']},
            {'label': 'Lease Return', 'icon': '↩️', 'url': '/lease-return', 'roles': ['Admin', 'Manager']},
            {'label': 'Maintenance', 'icon': '🔧', 'url': '/maintenance', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Move', 'icon': '🚚', 'url': '/move', 'roles': ['Admin', 'Manager']},
            {'label': 'Reserve', 'icon': '🔖', 'url': '/reserve', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Dispose', 'icon': '🗑️', 'url': '/dispose', 'roles': ['Admin', 'Manager']}
        ]
    },
    {
        'id': 'tools',
        'label': 'Tools',
        'icon': '🛠️',
        'roles': ['Admin', 'Manager', 'User'],
        'submenu': [
            {'label': 'LPO Lookup', 'icon': '🔍', 'url': '/lookup/lpo', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Data Quality', 'icon': '📊', 'url': '/data-quality', 'roles': ['Admin', 'Manager']},
            {'label': 'Import Data', 'icon': '📥', 'url': '/import', 'roles': ['Admin', 'Manager']},
            {
                'label': 'Export Data',
                'icon': '📤',
                'roles': ['Admin', 'Manager', 'User'],
                'submenu': [
                    {'label': 'Export Assets', 'icon': '📦', 'url': '/export/assets', 'roles': ['Admin', 'Manager', 'User']},
                    {'label': 'Export Users', 'icon': '👤', 'url': '/export/users', 'roles': ['Admin']},
                    {'label': 'Export Maintenance', 'icon': '🔧', 'url': '/export/maintenance', 'roles': ['Admin', 'Manager']},
                    {'label': 'Export Transactions', 'icon': '💳', 'url': '/export/transactions', 'roles': ['Admin', 'Manager']},
                    {'label': 'Export All Data', 'icon': '📋', 'url': '/export/all', 'roles': ['Admin']}
                ]
            },
            {'label': 'Document Gallery', 'icon': '📄', 'url': '/document-gallery', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Image Gallery', 'icon': '🖼️', 'url': '/image-gallery', 'roles': ['Admin', 'Manager', 'User']}
        ]
    },
    {
        'id': 'reports',
        'label': 'Reports',
        'icon': '📊',
        'roles': ['Admin', 'Manager', 'User', 'viewer'],
        'submenu': [
            {'label': 'Automated Report', 'icon': '🤖', 'url': '/reports/automated', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Custom Report', 'icon': '✏️', 'url': '/reports/custom', 'roles': ['Admin', 'Manager']},
            {'label': 'Inventory Report', 'icon': '📦', 'url': '/reports/inventory', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Asset Report', 'icon': '🏷️', 'url': '/reports/asset', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Audit Report', 'icon': '🔍', 'url': '/reports/audit', 'roles': ['Admin', 'Manager']},
            {'label': 'Check-out Report', 'icon': '📤', 'url': '/reports/checkout', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Contract Report', 'icon': '📄', 'url': '/reports/contract', 'roles': ['Admin', 'Manager']},
            {'label': 'Depreciation Report', 'icon': '📉', 'url': '/reports/depreciation', 'roles': ['Admin', 'Manager']},
            {'label': 'Funding Report', 'icon': '💵', 'url': '/reports/funding', 'roles': ['Admin', 'Manager']},
            {'label': 'Lease Asset Report', 'icon': '📝', 'url': '/reports/lease-asset', 'roles': ['Admin', 'Manager']},
            {'label': 'Maintenance Report', 'icon': '🔧', 'url': '/reports/maintenance', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Reservation Report', 'icon': '🔖', 'url': '/reports/reservation', 'roles': ['Admin', 'Manager']},
            {'label': 'Status Report', 'icon': '📊', 'url': '/reports/status', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Transaction Report', 'icon': '💳', 'url': '/reports/transaction', 'roles': ['Admin', 'Manager']},
            {'label': 'Other Report', 'icon': '📋', 'url': '/reports/other', 'roles': ['Admin', 'Manager']}
        ]
    },
    {
        'id': 'lists',
        'label': 'Lists',
        'icon': '📋',
        'roles': ['Admin', 'Manager', 'User', 'viewer'],
        'submenu': [
            {'label': 'Lists of Assets', 'icon': '📦', 'url': '/lists/assets', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Lists of Maintenances', 'icon': '🔧', 'url': '/lists/maintenances', 'roles': ['Admin', 'Manager', 'User']},
            {'label': 'Lists of Contracts', 'icon': '📄', 'url': '/lists/contracts', 'roles': ['Admin', 'Manager']}
        ]
    },
    {
        'id': 'advanced',
        'label': 'Advanced',
        'icon': '⚙️',
        'roles': ['Admin', 'Manager'],
        'submenu': [
            {
                'label': 'Contracts/Licenses',
                'icon': '📄',
                'roles': ['Admin', 'Manager'],
                'submenu': [
                    {'label': 'Add Contract', 'icon': '➕', 'url': '/contracts/add', 'roles': ['Admin', 'Manager']},
                    {'label': 'View All Contracts', 'icon': '📋', 'url': '/contracts/list', 'roles': ['Admin', 'Manager']},
                    {'label': 'Upcoming Renewals', 'icon': '⏰', 'url': '/contracts/renewals', 'roles': ['Admin', 'Manager']},
                    {'label': 'Expired Contracts', 'icon': '⚠️', 'url': '/contracts/expired', 'roles': ['Admin', 'Manager']},
                    {'label': 'Software Licenses', 'icon': '🔑', 'url': '/contracts/licenses', 'roles': ['Admin', 'Manager']}
                ]
            },
            {
                'label': 'Asset Purchase Orders',
                'icon': '📝',
                'roles': ['Admin', 'Manager'],
                'submenu': [
                    {'label': 'Add APO', 'icon': '➕', 'url': '/apo/add', 'roles': ['Admin', 'Manager']},
                    {'label': 'View All APOs', 'icon': '📋', 'url': '/apo/list', 'roles': ['Admin', 'Manager']}
                ]
            },
            {'label': 'Funding', 'icon': '💵', 'url': '/funding', 'roles': ['Admin', 'Manager']}
        ]
    },
    {
        'id': 'setup',
        'label': 'Setup/Configuration',
        'icon': '🔧',
        'roles': ['Admin', 'Manager'],
        'submenu': [
            {'label': 'Users', 'icon': '👤', 'url': '/users', 'roles': ['Admin']},
            {'label': 'Groups', 'icon': '🔗', 'url': '/groups', 'roles': ['Admin']},
            {'label': 'Employees', 'icon': '👨‍💼', 'url': '/employees', 'roles': ['Admin', 'Manager']},
            {'label': 'Customers', 'icon': '🙋', 'url': '/customers', 'roles': ['Admin', 'Manager']},
            {'label': 'Suppliers', 'icon': '🏢', 'url': '/suppliers', 'roles': ['Admin', 'Manager']},
            {'label': 'Company Info', 'icon': '🏢', 'url': '/company-info', 'roles': ['Admin']},
            {'label': 'Locations', 'icon': '📍', 'url': '/locations', 'roles': ['Admin', 'Manager']},
            {'label': 'Departments/Cost Centers', 'icon': '🏛️', 'url': '/departments', 'roles': ['Admin', 'Manager']},
            {'label': 'Categories', 'icon': '🏷️', 'url': '/categories', 'roles': ['Admin', 'Manager']},
            {'label': 'Subcategories', 'icon': '📑', 'url': '/subcategories', 'roles': ['Admin', 'Manager']},
            {'label': 'Assign Group', 'icon': '🔗', 'url': '/assign-group', 'roles': ['Admin']},
            {'label': 'Email Settings', 'icon': '📧', 'url': '/settings/email', 'roles': ['Admin']},
            {'label': 'System Settings', 'icon': '⚙️', 'url': '/settings/system', 'roles': ['Admin']},
            {
                'label': 'Database',
                'icon': '💾',
                'roles': ['Admin'],
                'submenu': [
                    {'label': 'Backup & Restore', 'icon': '💾', 'url': '/database', 'roles': ['Admin']},
                    {'label': 'Legacy Backup/Restore', 'icon': '🔄', 'url': '/backup-restore', 'roles': ['Admin']}
                ]
            },
            {
                'label': 'Customize Forms',
                'icon': '📝',
                'roles': ['Admin'],
                'submenu': [
                    {'label': 'Assets Form', 'icon': '📦', 'url': '/customize-assets-form', 'roles': ['Admin']},
                    {'label': 'Customers Form', 'icon': '👥', 'url': '/customize-customers-form', 'roles': ['Admin']},
                    {'label': 'Maintenance Form', 'icon': '🔧', 'url': '/customize-maintenance-form', 'roles': ['Admin']},
                    {'label': 'Contracts Form', 'icon': '📄', 'url': '/customize-contracts-form', 'roles': ['Admin']}
                ]
            }
        ]
    },
    {
        'id': 'help',
        'label': 'Help & Support',
        'icon': '❓',
        'roles': ['Admin', 'Manager', 'User', 'viewer'],
        'submenu': [
            {'label': 'User Guide', 'icon': '📖', 'url': '/help/user-guide', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Documentation', 'icon': '📚', 'url': '/help/documentation', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'FAQ', 'icon': '❓', 'url': '/help/faq', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Video Tutorials', 'icon': '🎥', 'url': '/help/video-tutorials', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'Contact Support', 'icon': '📧', 'url': '/help/contact-support', 'roles': ['Admin', 'Manager', 'User', 'viewer']},
            {'label': 'System Information', 'icon': 'ℹ️', 'url': '/help/system-info', 'roles': ['Admin']},
            {'label': 'Release Notes', 'icon': '📋', 'url': '/help/release-notes', 'roles': ['Admin', 'Manager', 'User', 'viewer']}
        ]
    }
]

def filter_menu_by_roles(menu, user_roles):
    """Filter navigation menu based on user roles
    
    Args:
        menu: The navigation menu structure
        user_roles: List or set of roles the user has
        
    Returns:
        Filtered menu structure containing only items the user can access
    """
    filtered_menu = []
    
    for item in menu:
        # Check if user has permission for this menu item
        if not any(role in item.get('roles', []) for role in user_roles):
            continue
            
        filtered_item = {k: v for k, v in item.items() if k != 'submenu'}
        
        # Filter submenu items
        if 'submenu' in item:
            filtered_submenu = []
            for subitem in item['submenu']:
                if any(role in subitem.get('roles', []) for role in user_roles):
                    # Check for nested submenu
                    if 'submenu' in subitem:
                        filtered_subitem = {k: v for k, v in subitem.items() if k != 'submenu'}
                        nested_filtered = []
                        for nested in subitem['submenu']:
                            if any(role in nested.get('roles', []) for role in user_roles):
                                nested_filtered.append(nested)
                        if nested_filtered:
                            filtered_subitem['submenu'] = nested_filtered
                            filtered_submenu.append(filtered_subitem)
                    else:
                        filtered_submenu.append(subitem)
            
            if filtered_submenu:
                filtered_item['submenu'] = filtered_submenu
                filtered_menu.append(filtered_item)
        else:
            filtered_menu.append(filtered_item)
    
    return filtered_menu

def get_navigation_menu(user_roles=None):
    """Get navigation menu filtered by user roles
    
    Args:
        user_roles: List or set of roles the user has. If None, returns full menu.
        
    Returns:
        Navigation menu structure
    """
    if user_roles is None:
        return NAVIGATION_MENU
    
    return filter_menu_by_roles(NAVIGATION_MENU, user_roles)
