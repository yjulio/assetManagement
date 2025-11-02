# Configuration settings for the Inventory Management System
import os

# Database Configuration
# Supports environment variables for cloud deployment
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "user_asset"),
    "password": os.getenv("DB_PASSWORD", "8.RvT2qhPC#VQkrd"),
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
FLASK_CONFIG = {
    "host": os.getenv("FLASK_HOST", "0.0.0.0"),
    "port": int(os.getenv("FLASK_PORT", "5000")),
    "debug": os.getenv("FLASK_DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
}
