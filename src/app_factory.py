"""Application factory and initialization
Centralizes app setup, blueprint registration, and dependency injection
"""

from flask import Flask, session
from config import FLASK_CONFIG, DB_CONFIG
from db.connection import init_connection_pool, get_connection
from utils.navigation import get_navigation_menu
import secrets
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """Application factory pattern
    
    Args:
        config: Optional configuration dictionary to override defaults
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.update(FLASK_CONFIG)
    if config:
        app.config.update(config)
    
    # Initialize database connection pool
    logger.info("Initializing database connection pool...")
    if not init_connection_pool(DB_CONFIG):
        logger.error("Failed to initialize database connection pool!")
        raise Exception("Database connection pool initialization failed")
    
    # Register context processors
    register_context_processors(app)
    
    # Register blueprints
    register_all_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    logger.info("Application initialization complete")
    return app

def register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def inject_csrf_token():
        """Inject CSRF token into all templates"""
        token = session.get('csrf_token')
        if not token:
            token = secrets.token_urlsafe(32)
            session['csrf_token'] = token
        return dict(csrf_token=token)
    
    @app.context_processor
    def inject_system_settings():
        """Inject site title, logo, and other system settings into all templates"""
        try:
            from AssetManagement import InventorySystem
            system = InventorySystem()
            settings = system.get_all_system_settings()
            return dict(
                site_title=settings.get('site_title', {}).get('value', 'Department of Local Authorities'),
                site_subtitle=settings.get('site_subtitle', {}).get('value', 'Asset Management System'),
                logo_path=settings.get('logo_path', {}).get('value', '/static/asset.png'),
                favicon_path=settings.get('favicon_path', {}).get('value', '/static/asset.png')
            )
        except Exception as e:
            logger.error(f"Error loading system settings: {e}")
            return dict(
                site_title='Department of Local Authorities',
                site_subtitle='Asset Management System',
                logo_path='/static/asset.png',
                favicon_path='/static/asset.png'
            )
    
    @app.context_processor
    def inject_navigation():
        """Inject role-based navigation menu into templates"""
        user_roles = session.get('groups', [])
        if not user_roles:
            user_roles = ['viewer']  # Default for non-logged-in users
        return dict(navigation_menu=get_navigation_menu(user_roles))

def register_all_blueprints(app):
    """Register all application blueprints"""
    from routes import register_blueprints
    register_blueprints(app)
    logger.info("All blueprints registered successfully")

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        logger.error(f"Internal server error: {error}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

def init_routes_dependencies(app, system, validate_csrf_func, db_conn_func):
    """Initialize route dependencies
    
    Args:
        app: Flask application instance
        system: InventorySystem instance
        validate_csrf_func: CSRF validation function
        db_conn_func: Database connection function
    """
    from routes.main import init_main_routes
    from routes.auth import init_auth_routes
    from routes.assets import init_assets_routes
    from routes.users import init_users_routes
    from routes.locations import init_locations_routes
    from routes.database import init_database_routes
    from routes.contracts import init_contracts_routes
    from routes.reports import init_reports_routes
    
    # Initialize each blueprint with dependencies
    init_main_routes(system, db_conn_func)
    init_auth_routes(system, validate_csrf_func, {'csv', 'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg', 'gif'})
    init_assets_routes(system, validate_csrf_func)
    init_users_routes(system, validate_csrf_func)
    init_locations_routes(system, validate_csrf_func)
    init_database_routes(system, validate_csrf_func)
    init_contracts_routes(system, validate_csrf_func)
    init_reports_routes(system, validate_csrf_func)
    
    logger.info("Route dependencies initialized")
