#!/bin/bash
# Script to reset MySQL root password and create database/user
# Run this script with sudo

echo "Resetting MySQL root password and setting up database..."

# Stop MySQL
sudo systemctl stop mysql
sudo pkill -9 mysqld mysqld_safe 2>/dev/null
sleep 2

# Create socket directory if needed
sudo mkdir -p /var/run/mysqld
sudo chown mysql:mysql /var/run/mysqld

# Start MySQL in safe mode
echo "Starting MySQL in safe mode..."
sudo mysqld_safe --skip-grant-tables --skip-networking > /tmp/mysql_reset.log 2>&1 &
sleep 8

# Reset root password
echo "Resetting root password..."
mysql << 'EOF'
USE mysql;
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '8.RvT2qhPC#VQkrd';
FLUSH PRIVILEGES;
SELECT 'Password reset complete' AS status;
EOF

# Stop safe mode and restart normally
echo "Restarting MySQL normally..."
sudo pkill -9 mysqld mysqld_safe 2>/dev/null
sleep 3
sudo systemctl start mysql
sleep 5

# Test connection and create database/user
echo "Creating database and user..."
mysql -u root -p'8.RvT2qhPC#VQkrd' << 'EOF'
CREATE DATABASE IF NOT EXISTS db_asset;
CREATE USER IF NOT EXISTS 'user_asset'@'localhost' IDENTIFIED BY '8.RvT2qhPC#VQkrd';
GRANT ALL PRIVILEGES ON db_asset.* TO 'user_asset'@'localhost';
FLUSH PRIVILEGES;
SHOW DATABASES LIKE 'db_asset';
SELECT User, Host FROM mysql.user WHERE User='user_asset';
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Database and user created."
    echo "Importing schema..."
    mysql -u user_asset -p'8.RvT2qhPC#VQkrd' db_asset < sql/create_database.sql
    echo "✅ Setup complete!"
else
    echo "❌ Error in setup"
    exit 1
fi

