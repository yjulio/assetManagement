# Cloud Deployment Guide
# Inventory Management System

## 🚀 Deployment Options

### Option 1: Manual Cloud Server Deployment

#### Prerequisites:
- Cloud server (AWS EC2, Azure VM, DigitalOcean Droplet, etc.)
- Python 3.8+
- MySQL database
- Public IP address

#### Steps:

1. **Clone or upload project to server**
   ```bash
   # Via Git
   git clone <your-repo-url>
   cd inventory-management-system
   
   # Or upload via SFTP/SCP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

4. **Set up MySQL database**
   ```bash
   mysql -u root -p
   CREATE DATABASE db_asset;
   USE db_asset;
   SOURCE sql/create_database.sql;
   exit;
   ```

5. **Configure firewall to allow port 5000**
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 5000/tcp
   
   # CentOS/RHEL
   sudo firewall-cmd --add-port=5000/tcp --permanent
   sudo firewall-cmd --reload
   ```

6. **Run the application**
   ```bash
   # Development
   cd src
   python app.py
   
   # Production (with Gunicorn)
   gunicorn --bind 0.0.0.0:5000 --chdir src app:app
   ```

7. **Access your application**
   ```
   http://YOUR_PUBLIC_IP:5000
   ```

### Option 2: Using Gunicorn (Production)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --chdir src app:app
   ```

3. **Create systemd service (Linux)**
   ```bash
   sudo nano /etc/systemd/system/inventory.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Inventory Management System
   After=network.target

   [Service]
   User=your-user
   WorkingDirectory=/path/to/inventory-management-system
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --chdir src app:app

   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl enable inventory
   sudo systemctl start inventory
   ```

### Option 3: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "src/app.py"]
```

Build and run:
```bash
docker build -t inventory-system .
docker run -p 5000:5000 --env-file .env inventory-system
```

### Option 4: Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Add MySQL addon**
   ```bash
   heroku addons:create cleardb:ignite
   ```

3. **Set environment variables**
   ```bash
   heroku config:set FLASK_HOST=0.0.0.0
   heroku config:set FLASK_PORT=5000
   heroku config:set FLASK_DEBUG=false
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 5: Railway Deployment

1. **Connect GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Railway will auto-deploy from Procfile**

### Option 6: AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 22.04 recommended)
2. **Configure Security Group** - Allow inbound on port 5000
3. **Connect via SSH**
   ```bash
   ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
   ```
4. **Follow Manual Cloud Server steps above**

### Option 7: DigitalOcean Droplet

1. **Create Droplet** (Ubuntu 22.04)
2. **Add firewall rule** for port 5000
3. **SSH to droplet**
4. **Follow Manual Cloud Server steps**

## 🔒 Security Considerations

1. **Change secret key**
   - Generate random key: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Set in `.env` file

2. **Use HTTPS** (production)
   - Set up Nginx reverse proxy with SSL
   - Use Let's Encrypt for free SSL certificates

3. **Database security**
   - Use strong passwords
   - Restrict database access to application server only
   - Enable SSL for database connections

4. **Environment variables**
   - Never commit `.env` file to Git
   - Use cloud provider's secret management

## 📝 Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_HOST | Server host address | 0.0.0.0 |
| FLASK_PORT | Server port | 5000 |
| FLASK_DEBUG | Debug mode (true/false) | false |
| SECRET_KEY | Flask secret key | (required) |
| DB_HOST | MySQL host | localhost |
| DB_USER | MySQL user | root |
| DB_PASSWORD | MySQL password | (empty) |
| DB_NAME | Database name | db_asset |
| DB_PORT | MySQL port | 3306 |

## 🌐 Accessing Your Application

After deployment:
- **Local network**: `http://SERVER_IP:5000`
- **Public internet**: `http://YOUR_PUBLIC_IP:5000`
- **With domain**: `http://yourdomain.com` (after DNS setup)

## 📊 Monitoring

- Check application logs
- Monitor server resources (CPU, RAM, disk)
- Set up uptime monitoring (UptimeRobot, Pingdom)

## 🔄 Updates

To update deployed application:
```bash
git pull
pip install -r requirements.txt
sudo systemctl restart inventory  # If using systemd
```
