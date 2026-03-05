"""Routes package for Asset Management System
Organizes all routes into logical blueprints for better maintainability
"""

from flask import Blueprint

# Import all blueprints
from routes.auth import auth_bp
from routes.assets import assets_bp
from routes.users import users_bp
from routes.locations import locations_bp
from routes.database import database_bp
from routes.contracts import contracts_bp
from routes.reports import reports_bp
from routes.main import main_bp
from routes.gallery import gallery_bp
from routes.mobile import mobile_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    
    # Main routes (landing, dashboard)
    app.register_blueprint(main_bp)
    
    # Authentication routes (login, logout, profile)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Asset management routes
    app.register_blueprint(assets_bp, url_prefix='/assets')
    
    # User and group management routes
    app.register_blueprint(users_bp, url_prefix='/users')
    
    # Location and category management routes
    app.register_blueprint(locations_bp, url_prefix='/locations')
    
    # Database management routes
    app.register_blueprint(database_bp, url_prefix='/database')
    
    # Contract management routes
    app.register_blueprint(contracts_bp, url_prefix='/contracts')
    
    # Reports and exports routes
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Gallery routes
    app.register_blueprint(gallery_bp)
    
    # Mobile features routes (QR, signatures, offline)
    app.register_blueprint(mobile_bp, url_prefix='/mobile')

__all__ = [
    'register_blueprints',
    'auth_bp',
    'assets_bp',
    'users_bp',
    'locations_bp',
    'database_bp',
    'contracts_bp',
    'reports_bp',
    'main_bp',
    'gallery_bp',
    'mobile_bp'
]
