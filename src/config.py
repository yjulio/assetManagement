# Configuration settings for the Inventory Management System
import os
import sys
import secrets

# Database Configuration
# Supports environment variables for cloud deployment
# WARNING: Set DB_PASSWORD in environment variables for production!
db_password = os.getenv("DB_PASSWORD")
if not db_password:
    if os.getenv("FLASK_DEBUG", "False").lower() == "true":
        # Use default password only in debug mode
        db_password = "change-this-password"
    else:
        # In production, require environment variable
        print("ERROR: DB_PASSWORD environment variable is required in production mode!")
        print("Please set DB_PASSWORD in your environment or .env file")
        sys.exit(1)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "user_asset"),
    "password": db_password,
    "database": os.getenv("DB_NAME", "db_asset"),
    "port": int(os.getenv("DB_PORT", "3306")),
    # Connection pooling and security settings
    "pool_name": "asset_pool",
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "pool_reset_session": True,
    "use_pure": False,  # Use C extension for better performance
    "autocommit": False,  # Prevent SQL injection via auto-commit
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci"
}

# Email Configuration
EMAIL_CONFIG = {
    "sender_email": os.getenv("EMAIL_SENDER", None),
    "sender_password": os.getenv("EMAIL_PASSWORD", None),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "enabled": os.getenv("EMAIL_ENABLED", "False").lower() == "true"
}

# Flask Configuration
# WARNING: Set SECRET_KEY in environment variables for production!
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    if os.getenv("FLASK_DEBUG", "False").lower() == "true":
        # Use default secret key only in debug mode
        secret_key = "dev-secret-key-change-in-production"
    else:
        # In production, require environment variable
        print("ERROR: SECRET_KEY environment variable is required in production mode!")
        print("Please set SECRET_KEY in your environment or .env file")
        sys.exit(1)

FLASK_CONFIG = {
    "host": os.getenv("FLASK_HOST", "0.0.0.0"),
    "port": int(os.getenv("FLASK_PORT", "5000")),
    "debug": os.getenv("FLASK_DEBUG", "False").lower() == "true",
    "secret_key": secret_key,
    # Session security
    "SESSION_COOKIE_SECURE": not os.getenv("FLASK_DEBUG", "False").lower() == "true",  # HTTPS only in production
    "SESSION_COOKIE_HTTPONLY": True,  # Prevent XSS access to session cookie
    "SESSION_COOKIE_SAMESITE": "Lax",  # CSRF protection
    "PERMANENT_SESSION_LIFETIME": int(os.getenv("SESSION_LIFETIME", "3600")),  # 1 hour default
    # Security headers (when Flask-Talisman is enabled)
    "TALISMAN_FORCE_HTTPS": not os.getenv("FLASK_DEBUG", "False").lower() == "true",
    "TALISMAN_FORCE_HTTPS_PERMANENT": False,
    # Upload security
    "MAX_CONTENT_LENGTH": int(os.getenv("MAX_UPLOAD_SIZE", str(16 * 1024 * 1024))),  # 16MB default
    "UPLOAD_FOLDER": os.getenv("UPLOAD_FOLDER", "/root/assetManagement/uploads"),
    "ALLOWED_EXTENSIONS": {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "xls", "xlsx", "csv", "txt"},
    # Rate limiting
    "RATELIMIT_ENABLED": os.getenv("RATELIMIT_ENABLED", "True").lower() == "true",
    "RATELIMIT_DEFAULT": os.getenv("RATELIMIT_DEFAULT", "200 per hour"),
    "RATELIMIT_STORAGE_URL": os.getenv("REDIS_URL", "memory://"),  # Use Redis in production
    # CSRF Protection
    "WTF_CSRF_ENABLED": True,
    "WTF_CSRF_TIME_LIMIT": int(os.getenv("CSRF_TIME_LIMIT", "3600")),  # 1 hour
    "WTF_CSRF_SSL_STRICT": not os.getenv("FLASK_DEBUG", "False").lower() == "true"
}

# Backup & Restore Configuration
BACKUP_CONFIG = {
    "backup_dir": os.getenv("BACKUP_DIR", "/root/assetManagement/backups/"),
    "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
    "auto_backup_enabled": os.getenv("AUTO_BACKUP_ENABLED", "false").lower() == "true",
    "auto_backup_time": os.getenv("AUTO_BACKUP_TIME", "02:00"),
    "optimize_on_backup": os.getenv("OPTIMIZE_ON_BACKUP", "true").lower() == "true",
    "max_backup_size_mb": int(os.getenv("MAX_BACKUP_SIZE_MB", "1000")),
    "allowed_formats": ["sql", "excel", "csv"]
}

# Database Management Settings
DATABASE_SETTINGS = {
    "enable_query_logging": os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true",
    "connection_pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "connection_timeout": int(os.getenv("DB_TIMEOUT", "30")),
    "enable_auto_optimize": os.getenv("ENABLE_AUTO_OPTIMIZE", "false").lower() == "true"
}
