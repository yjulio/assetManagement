# Admin Login Credentials

## Production Server: http://vbosasset.innovatelhubltd.com

### Administrator Account

**Username:** `admin`  
**Password:** `NewAdmin@2025` ⚠️ **CHANGED on November 4, 2025**  
**Previous Password:** ~~`Admin@2025`~~ (deprecated)  
**Email:** minomoya626@gmail.com

---

## Security Notes

1. **Change the password** after first login for security
2. The admin user has full access to all system features
3. Admin is assigned to the "Admin" group with administrator privileges

---

## How to Create Additional Admin Users

Run the following command on the server:

```bash
cd /home/ubuntu/assetManagement
python3 create_admin.py
```

This will create/update the admin user with the default password.

---

## How to Change Admin Password

### Method 1: Interactive Password Change (Recommended)

For secure password change with validation:

```bash
cd /root/assetManagement
python3 change_admin_password.py
```

This interactive script will:
- Prompt for username (default: admin)
- Ask for new password (hidden input)
- Confirm password
- Validate password strength:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- Update password in database

### Method 2: Quick Password Reset

To set a specific password directly:

```bash
cd /root/assetManagement
python3 reset_admin_password.py "YourNewPassword@2025"
```

**Example:**
```bash
python3 reset_admin_password.py "SecurePass@2025"
```

### Method 3: Reset to Default Password

To reset to the default password `Admin@2025`:

```bash
cd /root/assetManagement
python3 create_admin.py
```

⚠️ **Security Note:** Always change from default password in production!

---

**Created:** November 2, 2025  
**Server:** 207.246.126.171  
**Domain:** vbosasset.innovatelhubltd.com
