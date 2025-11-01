# MySQL Database Setup Guide

## Option 1: Run the Setup Script (Recommended)

If you have MySQL root access, run:

```bash
cd /home/ubuntu/assetManagement
./setup_database.sh
```

You'll be prompted for the MySQL root password.

## Option 2: Manual MySQL Commands

Connect to MySQL as root and run:

```bash
mysql -u root -p << 'SQL'
CREATE DATABASE IF NOT EXISTS db_asset;
CREATE USER IF NOT EXISTS 'user_asset'@'localhost' IDENTIFIED BY '8.RvT2qhPC#VQkrd';
GRANT ALL PRIVILEGES ON db_asset.* TO 'user_asset'@'localhost';
FLUSH PRIVILEGES;
SHOW DATABASES LIKE 'db_asset';
SELECT User, Host FROM mysql.user WHERE User='user_asset';
SQL
```

## Option 3: Import Schema

After creating the database and user, import the schema:

```bash
mysql -u user_asset -p'8.RvT2qhPC#VQkrd' db_asset < sql/create_database.sql
```

## Verify Setup

Test the connection:

```bash
mysql -u user_asset -p'8.RvT2qhPC#VQkrd' db_asset -e "SHOW TABLES;"
```

## Run Flask App

Once the database is set up:

```bash
cd /home/ubuntu/assetManagement/src
source ../venv/bin/activate
python app.py
```

The app is already configured to use:
- User: user_asset
- Password: 8.RvT2qhPC#VQkrd
- Database: db_asset
