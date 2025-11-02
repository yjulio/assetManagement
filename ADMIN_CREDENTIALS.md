# Admin Login Credentials

## Production Server: http://vbosasset.innovatelhubltd.com

### Administrator Account

**Username:** `admin`  
**Password:** `Admin@2025`  
**Email:** admin@vbos.gov.vu

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

## How to Reset Admin Password

If you need to reset the admin password, run:

```bash
cd /home/ubuntu/assetManagement
python3 create_admin.py
```

This will update the password to the default: `Admin@2025`

---

**Created:** November 2, 2025  
**Server:** 207.246.126.171  
**Domain:** vbosasset.innovatelhubltd.com
