#!/bin/bash
# Deployment script for Asset Management System
# Server: 207.246.126.171
# Domain: vbosasset.innovatelhubltd.com

echo "🚀 Deploying to production server..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVER_USER="root"
SERVER_IP="207.246.126.171"
APP_DIR="/home/ubuntu/assetManagement"
SERVICE_NAME="flask_asset_management"

echo -e "${YELLOW}Step 1: Pulling latest changes from Git...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/assetManagement
git pull origin main
ENDSSH

echo -e "${GREEN}✓ Code updated${NC}"

echo -e "${YELLOW}Step 2: Installing/updating dependencies...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/assetManagement
pip3 install -r requirements.txt
ENDSSH

echo -e "${GREEN}✓ Dependencies updated${NC}"

echo -e "${YELLOW}Step 3: Restarting Flask application...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
# Check if service exists and restart
if systemctl is-active --quiet flask_asset_management; then
    systemctl restart flask_asset_management
    echo "Service restarted"
elif pgrep -f "python.*app.py" > /dev/null; then
    # Kill old process
    pkill -f "python.*app.py"
    # Start new process
    cd /home/ubuntu/assetManagement/src
    nohup python3 app.py > /tmp/flask_app.log 2>&1 &
    echo "Process restarted"
else
    # Start new process
    cd /home/ubuntu/assetManagement/src
    nohup python3 app.py > /tmp/flask_app.log 2>&1 &
    echo "Process started"
fi
ENDSSH

echo -e "${GREEN}✓ Application restarted${NC}"

echo -e "${YELLOW}Step 4: Reloading Nginx...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
if command -v nginx > /dev/null; then
    nginx -t && systemctl reload nginx
    echo "Nginx reloaded"
fi
ENDSSH

echo -e "${GREEN}✓ Nginx reloaded${NC}"

echo -e "${YELLOW}Step 5: Checking application status...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✓ Flask application is running"
    pgrep -f "python.*app.py"
else
    echo "✗ Flask application is NOT running"
    echo "Check logs: tail -f /tmp/flask_app.log"
fi
ENDSSH

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Access your application at:"
echo "  → http://207.246.126.171:5000"
echo "  → http://vbosasset.innovatelhubltd.com"
echo ""
echo "To check logs:"
echo "  ssh ${SERVER_USER}@${SERVER_IP} 'tail -f /tmp/flask_app.log'"
echo ""
