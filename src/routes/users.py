"""User and group management routes"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from functools import wraps

# Create blueprint
users_bp = Blueprint('users', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_users_routes(inventory_system, csrf_validator):
    """Initialize users routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

# User management routes will be moved here from app.py
# Including: users, users/delete, assign-group, groups
