"""
File upload routes with drag-and-drop interface
Integrates with the existing PDF converter and provides secure upload handling
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from werkzeug.utils import secure_filename
import os
from .storage import upload_file, get_download_url
from utils import allowed_file

file_upload_bp = Blueprint("file_upload", __name__, url_prefix="/tools/file_upload")

@file_upload_bp.route("/")
@login_required
def index():
    """Main file upload page with drag-and-drop interface"""
    return render_template("file_upload/upload.html")

@file_upload_bp.route("/api/upload", methods=["POST"])
@login_required
def api_upload():
    """
    API endpoint for file uploads
    Supports both form uploads and AJAX requests
    """
    try:
        # Validate CSRF token for AJAX requests
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'CSRF token validation failed'
            }), 400
        
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Please upload PDF files only.'
            }), 400
        
        # Determine file type for organization
        if file.filename and '.' in file.filename:
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            file_type = 'pdf' if file_extension == 'pdf' else 'general'
        else:
            file_type = 'general'
        
        # Upload file using storage backend
        result = upload_file(file, current_user.id, file_type)
        
        if result['success']:
            # Generate secure download URL
            download_url = get_download_url(result['file_path'])
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'file_path': result['file_path'],
                'file_url': download_url,
                'filename': secure_filename(file.filename) if file.filename else 'unknown',
                'storage_type': result.get('storage_type', 'local')
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@file_upload_bp.route("/api/validate", methods=["POST"])
@login_required
def api_validate():
    """
    Validate file before upload (size, type, etc.)
    Useful for client-side validation
    """
    try:
        data = request.get_json() or {}
        filename = data.get('filename', '')
        filesize = data.get('filesize', 0)
        
        # Check file type
        if not allowed_file(filename):
            return jsonify({
                'valid': False,
                'error': 'File type not supported. Please upload PDF files.'
            })
        
        # Check file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if filesize > max_size:
            return jsonify({
                'valid': False,
                'error': f'File too large. Maximum size is {max_size // (1024*1024)}MB.'
            })
        
        return jsonify({
            'valid': True,
            'message': 'File validation passed'
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Validation failed: {str(e)}'
        }), 500

@file_upload_bp.route("/history")
@login_required
def upload_history():
    return redirect(url_for("converter.dashboard"))