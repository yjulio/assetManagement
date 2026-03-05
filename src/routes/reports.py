"""Report generation and export routes"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify, Response
from functools import wraps
import csv
import io
from datetime import datetime

# Create blueprint
reports_bp = Blueprint('reports', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_reports_routes(inventory_system, csrf_validator):
    """Initialize reports routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

# Report generation routes will be moved here from app.py
# Including: data-quality, data-quality/clean, data-quality/enrich, manage-dashboard, company-info
