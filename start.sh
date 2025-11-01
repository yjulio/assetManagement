#!/bin/bash
# Cloud Deployment Startup Script

echo "Starting Inventory Management System..."

# Set environment variables (if not using .env file)
export FLASK_HOST=${FLASK_HOST:-0.0.0.0}
export FLASK_PORT=${FLASK_PORT:-5000}
export FLASK_DEBUG=${FLASK_DEBUG:-false}

# Navigate to source directory
cd src

# Run the Flask application
python app.py
