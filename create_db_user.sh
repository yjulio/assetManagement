#!/bin/bash
# Script to create database and user for Asset Management System
# This script will prompt for MySQL root password

echo "Setting up database and user for Asset Management System..."
echo "You will be prompted for your MySQL root password."
echo ""

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
    echo ""
    echo "✅ Database and user created successfully!"
    echo "Database: db_asset"
    echo "User: user_asset"
    echo "Password: 8.RvT2qhPC#VQkrd"
    echo ""
    echo "Now importing schema..."
    mysql -u user_asset -p'8.RvT2qhPC#VQkrd' db_asset < sql/create_database.sql
    if [ $? -eq 0 ]; then
        echo "✅ Schema imported successfully!"
    else
        echo "⚠️  Schema import had issues, but database is created"
    fi
else
    echo ""
    echo "❌ Error setting up database. Please check your MySQL root password."
    exit 1
fi

