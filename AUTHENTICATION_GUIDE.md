# How to Protect All Pages with Login Authentication

## Current Setup
Your app already has a `@login_required` decorator at lines 116-123. 
This decorator checks if a user is logged in and redirects to login if not.

## Routes That Need Protection

### Option 1: Protect Individual Routes (Recommended)

Add `@login_required` decorator directly above each route function that should require login.

**Routes that currently DON'T have `@login_required` and need it:**

1. **Line 125** - `@app.route("/")` - Main dashboard/index page
   ```python
   @app.route("/")
   @login_required
   def index():
   ```

2. **Line 865** - `@app.route('/assets')` - Assets listing page
   ```python
   @app.route('/assets')
   @login_required
   def assets():
   ```

3. **Line 352** - `@app.route('/profile')` - Profile page (already has check, but should use decorator)

4. **Line 251** - `@app.route("/groups")` - Groups page

5. **Line 269** - `@app.route('/users')` - Users page

### Option 2: Use Flask's `before_request` Hook (Global Protection)

Add this code BEFORE your route definitions (around line 124, right before `@app.route("/")`):

```python
@app.before_request
def require_login():
    # List of routes that should NOT require login
    public_routes = ['login', 'static', 'logout']
    
    # Get the endpoint name
    endpoint = request.endpoint
    
    # Skip check for public routes and static files
    if endpoint in public_routes or request.path.startswith('/static/'):
        return None
    
    # Check if user is logged in
    if not session.get('username'):
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    
    return None
```

This will automatically protect ALL routes except:
- `/login` (login page itself)
- `/static/*` (static files like CSS, images)
- `/logout` (logout page)

### Which Option to Choose?

- **Option 1**: More control, protects routes one by one
- **Option 2**: Easier, protects everything automatically (recommended)

## Steps to Implement

1. **Open the file:** `/home/ubuntu/assetManagement/src/app.py`

2. **For Option 1 (Individual protection):**
   - Find each route that doesn't have `@login_required`
   - Add `@login_required` on the line before `def route_name():`
   - Make sure the login route (line 303) does NOT have this decorator
   - Make sure static files can still be accessed

3. **For Option 2 (Global protection - Recommended):**
   - Go to around line 124 (right before `@app.route("/")`)
   - Add the `@app.before_request` code block shown above
   - This protects ALL routes automatically

## Routes That Should Stay Public (No Protection)

- `/login` - Login page (line 303)
- `/static/*` - Static files (CSS, images, etc.)
- `/logout` - Logout page (optional, but usually safe)

## Testing After Implementation

1. Restart Flask service:
   ```bash
   sudo systemctl restart flask-asset-management.service
   ```

2. Test by:
   - Clearing browser cookies/session
   - Try accessing any page while logged out
   - Should redirect to `/login`
   - After login, should redirect back to requested page

## Notes

- The `@require_group('Admin')` decorator (lines 95-113) already includes login check
- Routes with `@require_group` don't need additional `@login_required`
- Static files should remain accessible without login
