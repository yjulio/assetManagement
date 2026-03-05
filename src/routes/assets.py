"""Asset management routes - CRUD, checkout, checkin, maintenance, disposal"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from functools import wraps

# Create blueprint
assets_bp = Blueprint('assets', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_assets_routes(inventory_system, csrf_validator):
    """Initialize assets routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

def require_group(*allowed_groups):
    """Decorator to require that the logged-in user belongs to one of the allowed groups."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            username = session.get('username')
            if not username:
                flash('Please log in to continue', 'warning')
                return redirect(url_for('auth.login'))
            user = system.users.get(username)
            if not user:
                flash('Unknown user', 'error')
                return redirect(url_for('auth.login'))
            user_groups = user.get('groups', set())
            if not any(group in user_groups for group in allowed_groups):
                flash('You do not have permission to perform this action', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Asset routes will be moved here from app.py
# Including: add, update, checkout, checkin, lease, lease-return, dispose, maintenance, move, reserve
