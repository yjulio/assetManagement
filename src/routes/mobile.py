"""Mobile features routes - QR codes, scanning, signatures, offline support"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file, current_app, session
from werkzeug.utils import secure_filename
from functools import wraps
import os
import io
import base64
from datetime import datetime

# Create blueprint
mobile_bp = Blueprint('mobile', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_mobile_routes(inventory_system, csrf_validator):
    """Initialize mobile routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('username'):
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapped

# QR Code Generation and Scanning
@mobile_bp.route('/qr-scanner')
@login_required
def qr_scanner():
    """Mobile QR code scanner interface"""
    return render_template('mobile/qr_scanner.html', title='QR Code Scanner')

@mobile_bp.route('/generate-qr/<asset_name>')
@login_required
def generate_qr(asset_name):
    """Generate QR code for an asset"""
    try:
        import qrcode
        from io import BytesIO
        
        # Get asset details
        asset = system.inventory.get(asset_name)
        if not asset:
            flash('Asset not found', 'error')
            return redirect(url_for('main.index'))
        
        # Create QR code data (JSON format)
        import json
        qr_data = json.dumps({
            'name': asset_name,
            'category': asset.get('category', ''),
            'location': asset.get('location', ''),
            'serial': asset.get('serial_number', ''),
            'asset_tag': asset.get('asset_tag', ''),
            'url': url_for('mobile.asset_details', asset_name=asset_name, _external=True)
        })
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except ImportError:
        # If qrcode not installed, generate a simple data URL
        flash('QR code generation requires the qrcode library', 'warning')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f'Error generating QR code: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@mobile_bp.route('/asset-qr-codes')
@login_required
def asset_qr_codes():
    """Display all assets with QR codes"""
    assets = system.inventory
    return render_template('mobile/asset_qr_codes.html', 
                          title='Asset QR Codes', 
                          assets=assets)

@mobile_bp.route('/scan-result', methods=['POST'])
@login_required
def scan_result():
    """Process scanned QR code data"""
    if not validate_csrf_token():
        return jsonify({'success': False, 'error': 'Invalid CSRF token'}), 403
    
    try:
        import json
        scan_data = request.json.get('data', '')
        
        # Try to parse as JSON (our format)
        try:
            asset_data = json.loads(scan_data)
            asset_name = asset_data.get('name')
            
            if asset_name and asset_name in system.inventory:
                return jsonify({
                    'success': True,
                    'redirect': url_for('mobile.asset_details', asset_name=asset_name)
                })
        except json.JSONDecodeError:
            # If not JSON, treat as asset tag or barcode
            # Search for asset by tag or serial number
            for name, asset in system.inventory.items():
                if (asset.get('asset_tag') == scan_data or 
                    asset.get('serial_number') == scan_data or
                    asset.get('barcode') == scan_data):
                    return jsonify({
                        'success': True,
                        'redirect': url_for('mobile.asset_details', asset_name=name)
                    })
        
        return jsonify({
            'success': False,
            'error': 'Asset not found'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Asset Details with Mobile View
@mobile_bp.route('/asset/<asset_name>')
@login_required
def asset_details(asset_name):
    """Mobile-optimized asset details view"""
    asset = system.inventory.get(asset_name)
    if not asset:
        flash('Asset not found', 'error')
        return redirect(url_for('main.index'))
    
    # Get asset documents
    doc_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'documents')
    documents = []
    if os.path.exists(doc_dir):
        for filename in os.listdir(doc_dir):
            if os.path.isfile(os.path.join(doc_dir, filename)):
                documents.append({
                    'name': filename,
                    'url': url_for('mobile.download_asset_document', 
                                  asset_name=asset_name, filename=filename)
                })
    
    # Get asset photos
    photo_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'photos')
    photos = []
    if os.path.exists(photo_dir):
        for filename in os.listdir(photo_dir):
            if os.path.isfile(os.path.join(photo_dir, filename)):
                photos.append({
                    'name': filename,
                    'url': url_for('mobile.view_asset_photo', 
                                  asset_name=asset_name, filename=filename)
                })
    
    return render_template('mobile/asset_details.html',
                          title=f'Asset: {asset_name}',
                          asset_name=asset_name,
                          asset=asset,
                          documents=documents,
                          photos=photos)

# Asset Photo Gallery
@mobile_bp.route('/asset/<asset_name>/photos')
@login_required
def asset_photo_gallery(asset_name):
    """Asset-specific photo gallery"""
    asset = system.inventory.get(asset_name)
    if not asset:
        flash('Asset not found', 'error')
        return redirect(url_for('main.index'))
    
    photo_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'photos')
    photos = []
    
    if os.path.exists(photo_dir):
        for filename in os.listdir(photo_dir):
            file_path = os.path.join(photo_dir, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                photos.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'url': url_for('mobile.view_asset_photo', asset_name=asset_name, filename=filename),
                    'thumb_url': url_for('mobile.view_asset_photo', asset_name=asset_name, filename=filename)
                })
    
    photos.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('mobile/asset_photo_gallery.html',
                          title=f'{asset_name} - Photos',
                          asset_name=asset_name,
                          asset=asset,
                          photos=photos)

@mobile_bp.route('/asset/<asset_name>/photos/upload', methods=['POST'])
@login_required
def upload_asset_photo(asset_name):
    """Upload photo for specific asset"""
    if not validate_csrf_token():
        return jsonify({'success': False, 'error': 'Invalid CSRF token'}), 403
    
    asset = system.inventory.get(asset_name)
    if not asset:
        return jsonify({'success': False, 'error': 'Asset not found'}), 404
    
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        photo_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'photos')
        os.makedirs(photo_dir, exist_ok=True)
        
        file_path = os.path.join(photo_dir, filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded successfully',
            'url': url_for('mobile.view_asset_photo', asset_name=asset_name, filename=filename)
        })
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@mobile_bp.route('/asset/<asset_name>/photos/<filename>')
@login_required
def view_asset_photo(asset_name, filename):
    """View asset photo"""
    photo_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'photos')
    return send_file(os.path.join(photo_dir, filename))

# Asset Document Upload (Invoice, Warranty, etc.)
@mobile_bp.route('/asset/<asset_name>/documents/upload', methods=['POST'])
@login_required
def upload_asset_document(asset_name):
    """Upload document for specific asset (invoice, warranty, manual, etc.)"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('mobile.asset_details', asset_name=asset_name))
    
    asset = system.inventory.get(asset_name)
    if not asset:
        flash('Asset not found', 'error')
        return redirect(url_for('main.index'))
    
    if 'document' not in request.files:
        flash('No file provided', 'warning')
        return redirect(url_for('mobile.asset_details', asset_name=asset_name))
    
    file = request.files['document']
    doc_type = request.form.get('document_type', 'other')
    
    if file.filename == '':
        flash('No file selected', 'warning')
        return redirect(url_for('mobile.asset_details', asset_name=asset_name))
    
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv', 'png', 'jpg', 'jpeg'}
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{doc_type}_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        doc_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'documents')
        os.makedirs(doc_dir, exist_ok=True)
        
        file_path = os.path.join(doc_dir, filename)
        file.save(file_path)
        
        flash(f'{doc_type.title()} document uploaded successfully!', 'success')
    else:
        flash('Invalid file type', 'error')
    
    return redirect(url_for('mobile.asset_details', asset_name=asset_name))

@mobile_bp.route('/asset/<asset_name>/documents/<filename>')
@login_required
def download_asset_document(asset_name, filename):
    """Download asset document"""
    doc_dir = os.path.join(current_app.root_path, '..', 'uploads', 'assets', asset_name, 'documents')
    return send_file(os.path.join(doc_dir, filename), as_attachment=True)

# Digital Signature for Asset Handover
@mobile_bp.route('/handover/<asset_name>')
@login_required
def asset_handover(asset_name):
    """Asset handover form with digital signature"""
    asset = system.inventory.get(asset_name)
    if not asset:
        flash('Asset not found', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('mobile/asset_handover.html',
                          title=f'Handover: {asset_name}',
                          asset_name=asset_name,
                          asset=asset)

@mobile_bp.route('/handover/<asset_name>/submit', methods=['POST'])
@login_required
def submit_handover(asset_name):
    """Process asset handover with signature"""
    if not validate_csrf_token():
        return jsonify({'success': False, 'error': 'Invalid CSRF token'}), 403
    
    try:
        asset = system.inventory.get(asset_name)
        if not asset:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        # Get form data
        recipient_name = request.form.get('recipient_name', '').strip()
        recipient_email = request.form.get('recipient_email', '').strip()
        handover_notes = request.form.get('notes', '').strip()
        signature_data = request.form.get('signature')  # Base64 encoded signature
        
        if not recipient_name or not signature_data:
            return jsonify({'success': False, 'error': 'Name and signature required'}), 400
        
        # Save signature image
        signature_dir = os.path.join(current_app.root_path, '..', 'uploads', 'signatures')
        os.makedirs(signature_dir, exist_ok=True)
        
        # Decode base64 signature
        signature_filename = f"handover_{asset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        signature_path = os.path.join(signature_dir, signature_filename)
        
        # Remove data URL prefix if present
        if ',' in signature_data:
            signature_data = signature_data.split(',')[1]
        
        with open(signature_path, 'wb') as f:
            f.write(base64.b64decode(signature_data))
        
        # Record handover in database
        from db.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO asset_handovers 
            (asset_name, recipient_name, recipient_email, notes, signature_path, 
             handed_over_by, handover_date)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (asset_name, recipient_name, recipient_email, handover_notes, 
              signature_filename, session.get('username')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Update asset status
        # system.checkout_asset(asset_name, recipient_name)
        
        return jsonify({
            'success': True,
            'message': 'Asset handover completed successfully',
            'redirect': url_for('mobile.asset_details', asset_name=asset_name)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Offline Support - Service Worker and PWA Manifest
@mobile_bp.route('/manifest.json')
def pwa_manifest():
    """PWA manifest for offline support"""
    manifest = {
        "name": "DLA Asset Management",
        "short_name": "DLA Assets",
        "description": "Department of Local Authorities Asset Management System",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#4ca1af",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/asset.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/asset.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest)

@mobile_bp.route('/sw.js')
def service_worker():
    """Service worker for offline functionality"""
    return current_app.send_static_file('js/service-worker.js')

@mobile_bp.route('/offline')
def offline_page():
    """Offline fallback page"""
    return render_template('mobile/offline.html', title='Offline Mode')
