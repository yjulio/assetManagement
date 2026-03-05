"""Authentication routes - Login, Logout, Profile management"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import mysql.connector

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None
ALLOWED_EXTENSIONS = None

def init_auth_routes(inventory_system, csrf_validator, allowed_exts):
    """Initialize auth routes with dependencies"""
    global system, validate_csrf_token, ALLOWED_EXTENSIONS
    system = inventory_system
    validate_csrf_token = csrf_validator
    ALLOWED_EXTENSIONS = allowed_exts

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('username'):
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapped

def get_current_user():
    """Get current logged-in user data"""
    username = session.get('username')
    if not username:
        return None
    user = system.users.get(username)
    if not user:
        return None
    return {
        'username': username,
        'name': user.get('name', ''),
        'email': user.get('email',''),
        'profile_picture': user.get('profile_picture', None),
        'groups': list(user.get('groups', set())),
        'created_at': user.get('created_at', None)
    }

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # If already logged in, redirect to dashboard
    if session.get('username'):
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if not validate_csrf_token():
            error = 'Invalid security token. Please try again.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        group = request.form.get('group','').strip()
        
        if not username or not password or not group:
            error = 'Please fill in all fields.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        user = system.users.get(username)
        if not user:
            error = 'Invalid username or password.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        # Check if user belongs to the selected group
        user_groups = user.get('groups', set())
        if group not in user_groups:
            error = f'This account does not have {group} privileges.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
        
        pw_hash = user.get('password_hash')
        if pw_hash and check_password_hash(pw_hash, password):
            session['username'] = username
            session['group'] = group
            session['groups'] = list(user_groups)  # Store all user groups
            flash(f'Welcome to Department of Local Authorities Asset Management System, {username}!', 'success')
            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            error = 'Invalid username or password.'
            groups_list = sorted(system.groups.keys())
            return render_template('landing.html', error=error, groups=groups_list)
    
    # GET request - show landing page with login form
    groups_list = sorted(system.groups.keys())
    return render_template('landing.html', groups=groups_list)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Handle user logout"""
    # Support POST with CSRF validation (secure) and GET for backward compatibility
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid logout request. Please try again.', 'error')
            return redirect(url_for('main.landing'))
    
    # Clear all session data
    username = session.get('username', 'User')
    session.clear()
    
    # Redirect to landing page
    return redirect(url_for('main.landing'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile"""
    user = get_current_user()
    if not user:
        flash('Please log in to view your profile', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('profile.html', title='My Profile', user=user)

@auth_bp.route('/change-profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    """Handle profile updates"""
    user = get_current_user()
    if not user:
        flash('Please log in to change your profile', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('auth.change_profile'))
        
        try:
            name = request.form.get('name','').strip()
            email = request.form.get('email','').strip()
            password = request.form.get('password','')
            
            # Update name in DB and cache
            system.users[user['username']]['name'] = name
            system.cursor.execute("UPDATE users SET name=%s WHERE username=%s", (name, user['username']))
            
            # Update email in DB and cache
            system.users[user['username']]['email'] = email
            system.cursor.execute("UPDATE users SET email=%s WHERE username=%s", (email, user['username']))
            
            # Update password if provided
            if password:
                pw_hash = generate_password_hash(password)
                system.users[user['username']]['password_hash'] = pw_hash
                system.cursor.execute("UPDATE users SET password_hash=%s WHERE username=%s", (pw_hash, user['username']))
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                pic = request.files['profile_picture']
                if pic and pic.filename:
                    ext = os.path.splitext(pic.filename)[1].lower()
                    if ext in ['.jpg','.jpeg','.png','.gif','.bmp']:
                        filename = f"profile_{user['username']}{ext}"
                        save_path = os.path.join(current_app.static_folder, filename)
                        pic.save(save_path)
                        url_path = f"/static/{filename}"
                        system.users[user['username']]['profile_picture'] = url_path
                        system.cursor.execute("UPDATE users SET profile_picture=%s WHERE username=%s", (url_path, user['username']))
            
            system.conn.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
        except mysql.connector.Error as e:
            system.conn.rollback()
            flash('Database error: Unable to update profile. Please try again.', 'error')
            current_app.logger.error(f'Database error in change_profile: {e}')
            return redirect(url_for('auth.change_profile'))
        except Exception as e:
            system.conn.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'error')
            current_app.logger.error(f'Error in change_profile: {e}')
            return redirect(url_for('auth.change_profile'))
    
    return render_template('change_profile.html', title='Change Profile', user=user)

@auth_bp.route('/account-details')
@login_required
def account_details():
    """Display account details"""
    user = get_current_user()
    if not user:
        flash('Please log in to view account details', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('account_details.html', title='Account Details', user=user)

@auth_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    return send_from_directory(upload_folder, filename)
