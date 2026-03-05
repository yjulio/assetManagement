"""Database management routes - backup, restore, maintenance"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from functools import wraps

# Create blueprint
database_bp = Blueprint('database', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_database_routes(inventory_system, csrf_validator):
    """Initialize database routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

# Database management routes will be moved here from app.py
# Including: database, backup-restore, backup/sql, restore/sql, database/optimize, database/check, database/repair, database/settings
