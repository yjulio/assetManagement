#!/bin/bash
# Quick deployment commands for 207.246.126.171

# Run these commands on the SERVER (207.246.126.171)

cd /home/ubuntu/assetManagement

# Pull latest changes
git pull origin main

# Install dependencies
pip3 install -r requirements.txt

# Restart the application
# Option 1: If using systemd service
sudo systemctl restart flask_asset_management

# Option 2: If running as background process
pkill -f "python.*app.py"
cd /home/ubuntu/assetManagement/src
nohup python3 app.py > /tmp/flask_app.log 2>&1 &

# Reload nginx
sudo nginx -t && sudo systemctl reload nginx

# Check status
ps aux | grep python
curl -I http://localhost:5000
