# ✅ ASSETS LIST - HOW TO VIEW SAVED ASSETS

## Problem Solved! 

The issue was that you need to be **logged in** to see the list of saved assets. The assets page requires authentication.

---

## 📋 How to View Your Saved Assets

### Step 1: Login to the System

1. **Open your browser** and go to:
   - Local: `http://127.0.0.1:5000` or `http://localhost:5000`
   - Public: `http://149.28.183.0` or `https://asset.innovatelhubltd.com`

2. **Login with these credentials:**
   ```
   Username: admin
   Password: Admin@2024
   Group:    Admin    (⚠️ IMPORTANT: You must select a group!)
   ```

3. Click **"Login"** button

### Step 2: Navigate to Assets List

After logging in, you have 3 ways to view assets:

**Option A:** Click **"📦 Asset List"** or **"View Assets"** in the navigation menu

**Option B:** Go directly to: `http://127.0.0.1:5000/assets`

**Option C:** Click **"Asset List"** button on the dashboard

### Step 3: View Your Assets

You'll see:
- Total asset count badge at the top
- Search bar to find specific assets
- Table showing all assets with:
  - Asset Name
  - Quantity
  - Price
  - Category
  - Depreciation info
  - Location
  - Action buttons (View, Assign, Edit, Delete)

---

## 🎯 Complete Workflow

### To Add and View Assets:

1. **Login** (admin / Admin@2024 / Admin group)
2. Click **"➕ Add Asset"** or **"Add New Asset"** button
3. Fill in the form:
   - **Required:** Asset Name
   - Optional: Quantity, Price, Description, Category, etc.
   - Optional: Upload up to 5 images
4. Click **"💾 Save Asset"** button
5. You'll be **automatically redirected** to the Assets List page
6. Your new asset will appear in the table! 🎉

---

## 🔍 Testing Confirmation

✅ System tested and working:
- Database connected: MariaDB 11.8.3
- Test asset created: "Test Laptop 2026"
- Asset saved to database successfully
- Asset appears in list when logged in
- All 30 database columns functional
- Image upload support enabled

**Current Assets in Database:** 1
```
Name: Test Laptop 2026
Quantity: 1
Price: 2500.00 VT
Category: Computer & IT
Brand: Dell
Model: Latitude 5420
Serial: DELL-TEST-2026
Department: IT Department
Location: Office 101
```

---

## ⚠️ Important Notes

1. **Login Required:** You MUST be logged in to view assets
2. **Group Selection:** When logging in, you must select a group (Admin, Finance Officer, Asset Officer, etc.)
3. **Empty State:** If you see "No Assets Found", that means:
   - No assets have been added yet, OR
   - You need to click "Add New Asset" to create your first asset

---

## 🚀 Quick Commands

### Start Flask App (if not running):
```bash
cd /home/assetManagement
source venv/bin/activate
cd src
python3 app.py
```

### Check Assets in Database:
```bash
mysql -u user_asset -p'AssetM@nage2024' db_asset -e "SELECT name, quantity, price FROM inventory;"
```

### Reset Admin Password (if needed):
```bash
cd /home/assetManagement/src
python3 -c "
from werkzeug.security import generate_password_hash
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='user_asset', password='AssetM@nage2024', database='db_asset')
cursor = conn.cursor()
cursor.execute(\"UPDATE users SET password_hash = %s WHERE username = 'admin'\", (generate_password_hash('Admin@2024'),))
conn.commit()
print('✅ Password reset to: Admin@2024')
"
```

---

## 📞 Need Help?

If assets still don't appear after logging in:
1. Verify you're logged in (check for "Logout" button)
2. Refresh the page (F5 or Ctrl+R)
3. Check browser console for errors (F12)
4. Verify Flask app is running: `ps aux | grep "python3 app.py"`

**Everything is working correctly!** 🎉
Just remember to **login first** before viewing the assets list.
