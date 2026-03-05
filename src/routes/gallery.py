"""Gallery routes - Document and Image galleries with upload functionality"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime

# Create blueprint
gallery_bp = Blueprint('gallery', __name__)

# These will be injected by app.py
system = None
validate_csrf_token = None

def init_gallery_routes(inventory_system, csrf_validator):
    """Initialize gallery routes with dependencies"""
    global system, validate_csrf_token
    system = inventory_system
    validate_csrf_token = csrf_validator

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        from flask import session
        if not session.get('username'):
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapped

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@gallery_bp.route('/document-gallery')
@login_required
def document_gallery():
    """Display document gallery"""
    # Get upload directory
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'documents')
    
    # Create directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    # Get list of documents
    documents = []
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if os.path.isfile(os.path.join(upload_dir, filename)):
                file_path = os.path.join(upload_dir, filename)
                file_stat = os.stat(file_path)
                documents.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'url': url_for('gallery.download_document', filename=filename)
                })
    
    # Sort by modified date (newest first)
    documents.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('document_gallery.html', title='Document Gallery', documents=documents)

@gallery_bp.route('/document-gallery/upload', methods=['POST'])
@login_required
def upload_document():
    """Handle document upload"""
    if not validate_csrf_token():
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('gallery.document_gallery'))
    
    if 'document' not in request.files:
        flash('No file selected', 'warning')
        return redirect(url_for('gallery.document_gallery'))
    
    file = request.files['document']
    
    if file.filename == '':
        flash('No file selected', 'warning')
        return redirect(url_for('gallery.document_gallery'))
    
    # Allowed document extensions
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'}
    
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid overwriting
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        flash(f'Document "{filename}" uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed: PDF, DOC, DOCX, XLS, XLSX, TXT, CSV', 'error')
    
    return redirect(url_for('gallery.document_gallery'))

@gallery_bp.route('/document-gallery/download/<filename>')
@login_required
def download_document(filename):
    """Download a document"""
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'documents')
    return send_from_directory(upload_dir, filename, as_attachment=True)

@gallery_bp.route('/document-gallery/delete/<filename>', methods=['POST'])
@login_required
def delete_document(filename):
    """Delete a document"""
    if not validate_csrf_token():
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('gallery.document_gallery'))
    
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'documents')
    file_path = os.path.join(upload_dir, filename)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'Document "{filename}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting document: {str(e)}', 'error')
    else:
        flash('Document not found', 'error')
    
    return redirect(url_for('gallery.document_gallery'))

@gallery_bp.route('/image-gallery')
@login_required
def image_gallery():
    """Display image gallery"""
    # Get upload directory
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
    
    # Create directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    # Get list of images
    images = []
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if os.path.isfile(os.path.join(upload_dir, filename)):
                file_path = os.path.join(upload_dir, filename)
                file_stat = os.stat(file_path)
                images.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'url': url_for('gallery.view_image', filename=filename),
                    'thumb_url': url_for('gallery.view_image', filename=filename)
                })
    
    # Sort by modified date (newest first)
    images.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('image_gallery.html', title='Image Gallery', images=images)

@gallery_bp.route('/image-gallery/upload', methods=['POST'])
@login_required
def upload_image():
    """Handle image upload"""
    if not validate_csrf_token():
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('gallery.image_gallery'))
    
    if 'image' not in request.files:
        flash('No file selected', 'warning')
        return redirect(url_for('gallery.image_gallery'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected', 'warning')
        return redirect(url_for('gallery.image_gallery'))
    
    # Allowed image extensions
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid overwriting
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        flash(f'Image "{filename}" uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, WEBP', 'error')
    
    return redirect(url_for('gallery.image_gallery'))

@gallery_bp.route('/image-gallery/view/<filename>')
@login_required
def view_image(filename):
    """View an image"""
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
    return send_from_directory(upload_dir, filename)

@gallery_bp.route('/image-gallery/delete/<filename>', methods=['POST'])
@login_required
def delete_image(filename):
    """Delete an image"""
    if not validate_csrf_token():
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('gallery.image_gallery'))
    
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
    file_path = os.path.join(upload_dir, filename)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'Image "{filename}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting image: {str(e)}', 'error')
    else:
        flash('Image not found', 'error')
    
    return redirect(url_for('gallery.image_gallery'))
