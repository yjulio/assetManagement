# Configuration settings for the Inventory Management System
import os
import sys

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
    "port": int(os.getenv("DB_PORT", "3306"))
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
    "secret_key": secret_key
}
