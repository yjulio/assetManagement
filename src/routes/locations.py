"""Location and category management routes"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from functools import wraps

# Create blueprint
locations_bp = Blueprint('locations', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_locations_routes(inventory_system, csrf_validator):
    """Initialize locations routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

# Location management routes will be moved here from app.py
# Including: locations, locations/add, locations/edit, locations/delete, categories, subcategories
