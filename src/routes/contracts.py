"""Contract management routes"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from functools import wraps

# Create blueprint
contracts_bp = Blueprint('contracts', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_contracts_routes(inventory_system, csrf_validator):
    """Initialize contracts routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

# Contract management routes will be moved here from app.py
# Including: contracts, contracts/add, contracts/upload, contracts/list, contracts/renewals, contracts/expired, contracts/licenses
