#!/bin/bash
# Script to create database and user for Asset Management System
# Run this script with MySQL root access

echo "Setting up database and user for Asset Management System..."

mysql -u root -p << 'EOF'
-- Create database
CREATE DATABASE IF NOT EXISTS db_asset;

-- Create user
CREATE USER IF NOT EXISTS 'user_asset'@'localhost' IDENTIFIED BY '8.RvT2qhPC#VQkrd';

-- Grant privileges
GRANT ALL PRIVILEGES ON db_asset.* TO 'user_asset'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES LIKE 'db_asset';
SELECT User, Host FROM mysql.user WHERE User='user_asset';

EOF

if [ $? -eq 0 ]; then
    echo "Database and user created successfully!"
    echo "Database: db_asset"
    echo "User: user_asset"
    echo "Password: 8.RvT2qhPC#VQkrd"
else
    echo "Error setting up database. Please check MySQL root password."
    exit 1
fi

