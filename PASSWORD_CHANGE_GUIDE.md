# Admin Password Management Guide

## Current Admin Credentials

**Username:** `admin`  
**Current Password:** `Admin@2025`  
**Email:** minomoya626@gmail.com

⚠️ **Important:** Change the default password for security!

---

## How to Change Admin Password

### Option 1: Interactive Password Change (Most Secure) ✅

**Recommended for production environments**

```bash
cd /root/assetManagement
python3 change_admin_password.py
```

**Features:**
- ✅ Hidden password input (no screen echo)
- ✅ Password confirmation
- ✅ Strength validation
- ✅ Supports any username
- ✅ Secure and user-friendly

**Example Session:**
```
============================================================
ADMIN PASSWORD CHANGE UTILITY
============================================================

Enter username (default: admin): admin

✓ User 'admin' found

Enter new password: ************
Confirm new password: ************
✓ Password is strong

============================================================
✅ SUCCESS! Password changed successfully.
============================================================

New login credentials:
  Username: admin
  Password: ************

⚠️  Please save your password securely!
```

### Option 2: Quick Password Reset

**Fast password change with command-line argument**

```bash
cd /root/assetManagement
python3 reset_admin_password.py "YourNewPassword@2025"
```

**Examples:**
```bash
# Set password to SecurePass@2025
python3 reset_admin_password.py "SecurePass@2025"

# Set password to MySecret123!
python3 reset_admin_password.py "MySecret123!"

# Set password to P@ssw0rd2025
python3 reset_admin_password.py "P@ssw0rd2025"
```

**Output:**
```
✅ SUCCESS!
Password for user 'admin' has been updated.

New login credentials:
  Username: admin
  Password: YourNewPassword@2025
```

### Option 3: Reset to Default

**Reset to factory default password (Admin@2025)**

```bash
cd /root/assetManagement
python3 create_admin.py
```

⚠️ **Use only for recovery or initial setup!**

---

## Password Requirements

For secure passwords, use the interactive method which enforces:

✅ **Minimum 8 characters**  
✅ **At least one uppercase letter** (A-Z)  
✅ **At least one lowercase letter** (a-z)  
✅ **At least one number** (0-9)  
✅ **At least one special character** (!@#$%^&*)

### Good Password Examples:
- `SecurePass@2025` ✓
- `Admin#NewP@ss123` ✓
- `MyStr0ng!P@ssword` ✓
- `VBOS$Asset2025` ✓

### Bad Password Examples:
- `password` ❌ (too weak, no uppercase/numbers/special chars)
- `Admin123` ❌ (no special characters)
- `admin@2025` ❌ (no uppercase)
- `PASSWORD!` ❌ (no lowercase or numbers)

---

## Troubleshooting

### Error: User does not exist

```
❌ ERROR: User 'admin' does not exist!

Available users:
  - admin
  - testuser
```

**Solution:** Use one of the available usernames listed

### Error: Database connection failed

```
ERROR: Can't connect to MySQL server
```

**Solution:** 
1. Check MySQL is running: `systemctl status mysql`
2. Verify database password: `DB_PASSWORD='change-this-password'`
3. Check database exists: `mysql -u user_asset -p -e "SHOW DATABASES;"`

### Error: Passwords do not match

```
❌ Passwords do not match. Please try again.
```

**Solution:** Type the same password in both prompts

### Error: Password too weak

```
❌ Password must contain at least one uppercase letter
Please try again.
```

**Solution:** Follow password requirements listed above

---

## Security Best Practices

1. **Change default password immediately** after installation
2. **Use strong passwords** with mixed characters
3. **Don't share passwords** via email or chat
4. **Store passwords securely** using a password manager
5. **Change passwords regularly** (every 90 days)
6. **Don't reuse passwords** from other systems
7. **Log out** when leaving workstation unattended

---

## Command Reference

### List All Scripts

```bash
ls -la /root/assetManagement/*admin*.py
```

**Output:**
```
-rwxr-xr-x change_admin_password.py   # Interactive password change
-rwxr-xr-x reset_admin_password.py    # Quick password reset
-rwxr-xr-x create_admin.py            # Create/reset to default
-rw-r--r-- src/seed_admin.py          # Initial setup script
```

### Check Admin User Exists

```bash
cd /root/assetManagement
python3 -c "
import sys
sys.path.insert(0, 'src')
from AssetManagement import InventorySystem
s = InventorySystem()
print('Admin user exists:', 'admin' in s.users)
print('All users:', list(s.users.keys()))
"
```

### Test Login (via command line)

```bash
cd /root/assetManagement
python3 -c "
import sys
sys.path.insert(0, 'src')
from AssetManagement import InventorySystem
from werkzeug.security import check_password_hash
s = InventorySystem()
username = 'admin'
password = 'Admin@2025'
user = s.users.get(username)
if user:
    pw_hash = s.cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    result = s.cursor.fetchone()
    if result:
        print('Password valid:', check_password_hash(result[0], password))
"
```

---

## Web Interface Password Change

Users can also change their password through the web interface:

1. Log in to http://207.246.126.171:5000
2. Click on **Profile** (top right)
3. Click **Change Password**
4. Enter current password
5. Enter new password (twice)
6. Click **Update Password**

---

## For Production Deployment

When deploying to production server:

1. **Immediately change default password:**
   ```bash
   python3 change_admin_password.py
   ```

2. **Set strong SECRET_KEY:**
   ```bash
   export SECRET_KEY="$(openssl rand -hex 32)"
   echo "SECRET_KEY='$(openssl rand -hex 32)'" >> .env
   ```

3. **Update database password:**
   ```bash
   export DB_PASSWORD="your-secure-database-password"
   ```

4. **Document credentials securely** in password manager

5. **Test login** before closing session

---

## Files Created

- `change_admin_password.py` - Interactive password change with validation
- `reset_admin_password.py` - Quick command-line password reset
- `create_admin.py` - Create admin user with default password
- `PASSWORD_CHANGE_GUIDE.md` - This guide

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Change password (secure) | `python3 change_admin_password.py` |
| Reset password (quick) | `python3 reset_admin_password.py "NewPass@123"` |
| Reset to default | `python3 create_admin.py` |
| Test login | Access web interface at :5000 |

---

**Last Updated:** November 4, 2025  
**Server:** 207.246.126.171  
**Domain:** vbosasset.innovatelhubltd.com
