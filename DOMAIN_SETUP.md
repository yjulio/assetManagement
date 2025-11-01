# Domain Configuration Guide

## Domain: innovatelhubltd.vbosasset.com

### DNS Configuration

1. **Point your domain DNS to this server:**
   - Type: A Record
   - Name: innovatelhubltd (or @)
   - Value: YOUR_SERVER_IP
   - TTL: 3600 (or default)

   Also create A record for www:
   - Type: A Record
   - Name: www
   - Value: YOUR_SERVER_IP
   - TTL: 3600

2. **Check DNS propagation:**
   ```bash
   dig innovatelhubltd.vbosasset.com
   nslookup innovatelhubltd.vbosasset.com
   ```

### SSL Certificate Setup (HTTPS)

Once DNS is working, install SSL certificate:

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d innovatelhubltd.vbosasset.com -d www.innovatelhubltd.vbosasset.com

# Certbot will:
# - Automatically configure nginx for HTTPS
# - Set up HTTP to HTTPS redirect
# - Configure automatic renewal
```

### Manual SSL Configuration

If you prefer to configure SSL manually, edit:
```bash
sudo nano /etc/nginx/sites-available/asset_management
```

Add SSL configuration:
```nginx
server {
    listen 443 ssl;
    server_name innovatelhubltd.vbosasset.com www.innovatelhubltd.vbosasset.com;
    
    ssl_certificate /etc/letsencrypt/live/innovatelhubltd.vbosasset.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/innovatelhubltd.vbosasset.com/privkey.pem;
    
    # ... rest of configuration
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name innovatelhubltd.vbosasset.com www.innovatelhubltd.vbosasset.com;
    return 301 https://$server_name$request_uri;
}
```

### Verify Configuration

1. **Test HTTP:**
   ```bash
   curl -I http://innovatelhubltd.vbosasset.com
   ```

2. **Test HTTPS (after SSL setup):**
   ```bash
   curl -I https://innovatelhubltd.vbosasset.com
   ```

3. **Check nginx configuration:**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Current Configuration

- **Domain:** innovatelhubltd.vbosasset.com
- **Nginx Config:** /etc/nginx/sites-available/asset_management
- **Flask App:** Running on port 5000 (proxied by nginx)
- **HTTP Port:** 80
- **HTTPS Port:** 443 (after SSL setup)
