# Local XAMPP Development Setup

This guide helps you set up the Asset Management System on your local Windows machine with XAMPP.

## Prerequisites
- XAMPP installed with Apache and MySQL running
- Python 3.8+ installed
- Git installed

## Database Setup

1. **Create Database and User in XAMPP MySQL:**
   - Open phpMyAdmin (http://localhost/phpmyadmin)
   - Create database: `db_asset`
   - Create user: `user_asset`
   - Set password: `8.RvT2qhPC#VQkrd` (or your preferred password)
   - Grant all privileges on `db_asset` to `user_asset`

   Or use MySQL command line:
   ```sql
   CREATE DATABASE db_asset;
   CREATE USER 'user_asset'@'localhost' IDENTIFIED BY '8.RvT2qhPC#VQkrd';
   GRANT ALL PRIVILEGES ON db_asset.* TO 'user_asset'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **Update config.py for Local Development:**
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "user_asset",
       "password": "8.RvT2qhPC#VQkrd",  # or your password
       "database": "db_asset",
       "port": 3306  # Default XAMPP MySQL port
   }
   ```

## Setup Steps

1. **Clone/Pull the repository:**
   ```bash
   cd C:\xampp\htdocs  # or your preferred directory
   git clone https://github.com/yjulio/assetManagement.git
   # OR if already cloned:
   cd assetManagement
   git pull origin main
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Import database schema:**
   ```bash
   mysql -u user_asset -p db_asset < sql/create_database.sql
   ```

5. **Run Flask application:**
   ```bash
   cd src
   python app.py
   ```

6. **Access the application:**
   - Open browser: http://localhost:5000

## Differences: Server vs Local

### Server (Production)
- Uses systemd service to run Flask
- Nginx on port 80 as reverse proxy
- Database user: `user_asset`
- MySQL service managed by systemd

### Local (XAMPP)
- Run Flask manually with `python app.py`
- Access directly on port 5000
- XAMPP MySQL on default port 3306
- No reverse proxy needed

## Configuration Notes

The `config.py` file supports environment variables, so you can:
1. Create a `.env` file locally with different settings
2. Or modify `config.py` directly for local development
3. Keep production settings in environment variables on the server

## Syncing Changes

1. **Pull server changes to local:**
   ```bash
   git pull origin main
   ```

2. **Push local changes to server:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

3. **On server, pull updates:**
   ```bash
   cd /home/ubuntu/assetManagement
   git pull origin main
   sudo systemctl restart flask-asset-management.service
   ```

## Troubleshooting

- **MySQL Connection Issues:** Check XAMPP MySQL is running on port 3306
- **Port Already in Use:** Change FLASK_PORT in config.py or kill process using port 5000
- **Static Files Not Loading:** Flask serves static files automatically, no nginx needed locally

