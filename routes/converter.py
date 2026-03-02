import os
import uuid
import tempfile
import io
import zipfile
import json
from datetime import datetime

# CRITICAL: JSON module import and usage - DO NOT MODIFY
# This fixes the "name 'json' is not defined" error that caused PDF processing failures
# The json module is imported globally above and used directly throughout the file
# Any changes to JSON handling must maintain this pattern to prevent regressions
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageOps
from models_security import db, Activity
from utils import allowed_file, get_file_info
from tools.file_upload.storage import upload_file as storage_upload_file

converter_bp = Blueprint("converter", __name__)

@converter_bp.route("/")
@converter_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard showing recent activities and statistics"""
    recent_activities = current_user.get_recent_activities(limit=5)
    total_conversions = current_user.get_total_conversions()
    total_pages = current_user.get_total_pages_converted()
    
    return render_template(
        "dashboard_simple.html",
        recent_activities=recent_activities,
        total_conversions=total_conversions,
        total_pages=total_pages,
    )

@converter_bp.route("/convert", methods=["GET", "POST"])
@login_required
def convert():
    """Main conversion page - supports PDF and image uploads"""
    if request.method == "POST":
        current_app.logger.info(f"POST request received - form data: {dict(request.form)}")
        current_app.logger.info(f"Files in request: {list(request.files.keys())}")
        
        # Determine upload type based on form data
        upload_type = request.form.get('upload_type', 'pdf')
        current_app.logger.info(f"Upload type: {upload_type}")
        
        if upload_type == 'pdf':
            # Handle PDF upload
            if "pdf_file" in request.files and request.files["pdf_file"] and request.files["pdf_file"].filename:
                file = request.files["pdf_file"]
                
                # Check file size (100MB limit)
                if file.content_length and file.content_length > 100 * 1024 * 1024:
                    return render_template("file_too_large.html")
                
                # Validate PDF file type
                if not file.filename or not file.filename.lower().endswith('.pdf'):
                    flash("Please select a valid PDF file.", "danger")
                    return render_template("convert.html")
                
                # Process PDF directly - no redirects
                return process_pdf_upload(file)
            else:
                flash("Please select a PDF file to upload.", "warning")
                return render_template("convert.html")
                
        elif upload_type == 'images':
            # Handle image upload
            if "image_files" in request.files:
                files = request.files.getlist("image_files")
                valid_files = [f for f in files if f and f.filename]
                
                if not valid_files:
                    flash("Please select at least one image file to upload.", "warning")
                    return render_template("convert.html")
                
                # Check if preview mode is enabled
                preview_mode = 'preview_mode' in request.form
                
                # Process images directly - no redirects
                return process_image_upload(valid_files, preview_mode)
            else:
                flash("Please select image files to upload.", "warning")
                return render_template("convert.html")
        
        # If we get here, something went wrong
        current_app.logger.warning("Reached fallback case - no valid files found")
        flash("Please select files to upload.", "warning")
        return render_template("convert.html")

    # GET request - show clean form
    current_app.logger.info("GET request - showing convert form")
    return render_template("convert.html")

def process_pdf_upload(file):
    """Process PDF file and convert to coloring book - NO REDIRECTS"""
    try:
        current_app.logger.info(f"Starting PDF processing for file: {file.filename}")
        start_time = datetime.now()
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Save uploaded file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Check file exists and size
        if not os.path.exists(file_path):
            flash("File upload failed. Please try again.", "danger")
            return render_template("convert.html")
        
        # Open PDF and extract pages
        pdf_document = fitz.open(file_path)
        total_pages = len(pdf_document)
        
        if total_pages == 0:
            flash("The PDF file appears to be empty or corrupted.", "danger")
            return render_template("convert.html")
        
        # Create output directory with session tracking
        session_id = str(uuid.uuid4())
        output_dir = f"outputs/{session_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        converted_pages = []
        
        # Process each page
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            # Use get_pixmap for newer PyMuPDF versions, fallback to getPixmap
            try:
                pix = page.get_pixmap()
            except AttributeError:
                pix = page.getPixmap()
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image for processing
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Apply line art conversion
            line_art_image = create_line_art(pil_image)
            
            # Save as PNG
            page_filename = f"page_{page_num + 1:03d}_coloring.png"
            page_path = os.path.join(output_dir, page_filename)
            line_art_image.save(page_path, "PNG")
            
            converted_pages.append(page_filename)
        
        pdf_document.close()
        
        # Create ZIP file with all converted pages
        zip_filename = f"coloring_book_{session_id}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for page_file in converted_pages:
                page_path = os.path.join(output_dir, page_file)
                zipf.write(page_path, page_file)
        
        # Log activity
        processing_duration = (datetime.now() - start_time).total_seconds()
        activity = Activity()
        activity.user_id = current_user.id
        activity.filename = filename
        activity.pages_converted = total_pages
        activity.processing_duration = processing_duration
        activity.output_filename = zip_filename
        activity.status = "completed"
        db.session.add(activity)
        db.session.commit()
        
        # Clean up original file
        os.remove(file_path)
        
        # Return success page with download link
        return render_template(
            "conversion_complete.html",
            zip_filename=zip_filename,
            session_id=session_id,
            total_pages=total_pages,
            processing_time=processing_duration
        )
        
    except Exception as e:
        current_app.logger.error(f"PDF conversion error: {str(e)}")
        flash(f"An error occurred during conversion: {str(e)}", "danger")
        return render_template("convert.html")

def process_image_upload(files, preview_mode):
    """Process image files and convert to coloring book - NO REDIRECTS"""
    try:
        if preview_mode:
            # Handle preview mode - step by step processing
            return process_images_with_preview(files)
        else:
            # Handle batch mode - process all at once
            return process_images_batch(files)
            
    except Exception as e:
        current_app.logger.error(f"Image conversion error: {str(e)}")
        flash(f"An error occurred during conversion: {str(e)}", "danger")
        return render_template("convert.html")

def process_images_with_preview(files):
    """Process images with step-by-step preview and approval"""
    session_id = str(uuid.uuid4())
    
    # Create session directory to store files temporarily
    session_dir = f"outputs/session_{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    
    # Store session data for preview workflow (without binary data)
    session_data = {
        'session_id': session_id,
        'files': [],
        'current_index': 0,
        'approved_images': []
    }
    
    # Process and store files to disk (not in memory)
    for i, file in enumerate(files):
        if allowed_image_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Save file to session directory
            file_path = os.path.join(session_dir, f"input_{i}_{filename}")
            file.save(file_path)
            
            session_data['files'].append({
                'filename': filename,
                'file_path': file_path,
                'index': i
            })
    
    if not session_data['files']:
        flash("No valid image files found.", "warning")
        return render_template("convert.html")
    
    # Start preview with first image
    return show_image_preview(session_data, 0)

def show_image_preview(session_data, image_index):
    """Show preview of single image for approval"""
    if image_index >= len(session_data['files']):
        # All images processed, create final output
        return finalize_image_conversion(session_data)
    
    file_info = session_data['files'][image_index]
    
    # Create temp directories
    session_id = session_data['session_id']
    temp_dir = f"outputs/preview_{session_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Load and convert image from file path
    pil_image = Image.open(file_info['file_path'])
    line_art_image = create_line_art(pil_image)
    
    # Save both original and converted for preview
    base_name = os.path.splitext(file_info['filename'])[0]
    original_path = os.path.join(temp_dir, f"{base_name}_original.png")
    converted_path = os.path.join(temp_dir, f"{base_name}_coloring.png")
    
    pil_image.save(original_path, "PNG")
    line_art_image.save(converted_path, "PNG")
    
    # Show preview template - session_data now serializable
    return render_template(
        "image_preview.html",
        session_data=json.dumps(session_data),
        current_index=image_index,
        total_images=len(session_data['files']),
        filename=file_info['filename'],
        original_image=f"preview_{session_id}/{base_name}_original.png",
        converted_image=f"preview_{session_id}/{base_name}_coloring.png"
    )

def process_images_batch(files):
    """Process all images at once without preview"""
    start_time = datetime.now()
    session_id = str(uuid.uuid4())
    output_dir = f"outputs/{session_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    converted_images = []
    
    for file in files:
        # Validate image file
        if not allowed_image_file(file.filename):
            continue
            
        filename = secure_filename(file.filename)
        
        # Load image
        pil_image = Image.open(file.stream)
        
        # Apply line art conversion
        line_art_image = create_line_art(pil_image)
        
        # Save as PNG
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_coloring.png"
        output_path = os.path.join(output_dir, output_filename)
        line_art_image.save(output_path, "PNG")
        
        converted_images.append(output_filename)
    
    if not converted_images:
        flash("No valid images were processed.", "warning")
        return render_template("convert.html")
    
    # Create ZIP file
    zip_filename = f"coloring_images_{session_id}.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img_file in converted_images:
            img_path = os.path.join(output_dir, img_file)
            zipf.write(img_path, img_file)
    
    # Log activity
    processing_duration = (datetime.now() - start_time).total_seconds()
    activity = Activity()
    activity.user_id = current_user.id
    activity.filename = f"batch_images_{len(files)}"
    activity.pages_converted = len(converted_images)
    activity.processing_duration = processing_duration
    activity.output_filename = zip_filename
    activity.status = "completed"
    db.session.add(activity)
    db.session.commit()
    
    # Return success page with download link
    return render_template(
        "conversion_complete.html",
        zip_filename=zip_filename,
        session_id=session_id,
        total_pages=len(converted_images),
        processing_time=processing_duration
    )

def finalize_image_conversion(session_data):
    """Create final ZIP with all approved images"""
    start_time = datetime.now()
    session_id = session_data['session_id']
    output_dir = f"outputs/{session_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    approved_files = []
    
    # Copy approved images to final output
    for approved in session_data['approved_images']:
        source_path = approved['converted_path']
        target_filename = approved['filename']
        target_path = os.path.join(output_dir, target_filename)
        
        # Copy file
        with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
            dst.write(src.read())
        
        approved_files.append(target_filename)
    
    if not approved_files:
        flash("No images were approved for conversion.", "warning")
        return render_template("convert.html")
    
    # Create ZIP file
    zip_filename = f"approved_coloring_images_{session_id}.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img_file in approved_files:
            img_path = os.path.join(output_dir, img_file)
            zipf.write(img_path, img_file)
    
    # Log activity
    processing_duration = (datetime.now() - start_time).total_seconds()
    activity = Activity()
    activity.user_id = current_user.id
    activity.filename = f"preview_approved_{len(approved_files)}"
    activity.pages_converted = len(approved_files)
    activity.processing_duration = processing_duration
    activity.output_filename = zip_filename
    activity.status = "completed"
    db.session.add(activity)
    db.session.commit()
    
    # Clean up preview files
    preview_dir = f"outputs/preview_{session_id}"
    if os.path.exists(preview_dir):
        import shutil
        shutil.rmtree(preview_dir)
    
    # Return success page
    return render_template(
        "conversion_complete.html",
        zip_filename=zip_filename,
        session_id=session_id,
        total_pages=len(approved_files),
        processing_time=processing_duration
    )

def create_line_art(image):
    """Convert image to bold line art suitable for a coloring book"""
    from PIL import ImageEnhance

    gray = image.convert('L')

    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)

    smoothed = gray.filter(ImageFilter.GaussianBlur(radius=1.5))

    edges1 = smoothed.filter(ImageFilter.FIND_EDGES)
    edges2 = smoothed.filter(ImageFilter.Kernel(
        size=(3, 3),
        kernel=[-1, -1, -1, -1, 8, -1, -1, -1, -1],
        scale=1,
        offset=0
    ))
    edges3 = smoothed.filter(ImageFilter.CONTOUR)

    from PIL import ImageChops
    combined = ImageChops.darker(edges1, edges2)
    combined = ImageChops.darker(combined, edges3)

    inverted = ImageOps.invert(combined)

    def apply_threshold(x):
        return 255 if x > 200 else 0
    binary = inverted.point(apply_threshold, mode='1')

    clean = binary.convert('L')
    clean = clean.filter(ImageFilter.MinFilter(size=3))
    clean = clean.filter(ImageFilter.MaxFilter(size=3))

    def final_threshold(x):
        return 255 if x > 128 else 0
    clean = clean.point(final_threshold, mode='1')

    result = clean.convert('RGB')
    return result

def allowed_image_file(filename):
    """Check if file is an allowed image type"""
    if not filename:
        return False
    
    allowed_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.tiff', '.tif', '.webp', '.svg', '.psd'
    }
    
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

@converter_bp.route("/download/<session_id>/<filename>")
@login_required
def download_file(session_id, filename):
    """Download converted file"""
    try:
        file_path = os.path.join("outputs", session_id, filename)
        
        if not os.path.exists(file_path):
            flash("File not found. It may have been cleaned up.", "warning")
            return redirect(url_for("converter.convert"))
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        flash("Error downloading file.", "danger")
        return redirect(url_for("converter.convert"))

@converter_bp.route("/progress/<session_id>")
@login_required
def check_progress(session_id):
    """Check conversion progress for a session"""
    return jsonify({"status": "complete", "progress": 100}), 200

@converter_bp.route("/preview_image/<path:image_path>")
@login_required
def serve_preview_image(image_path):
    """Serve preview images"""
    try:
        full_path = os.path.join("outputs", image_path)
        if os.path.exists(full_path):
            return send_file(full_path)
        else:
            return "Image not found", 404
    except Exception as e:
        current_app.logger.error(f"Preview image error: {str(e)}")
        return "Error serving image", 500

@converter_bp.route("/handle_preview", methods=["POST"])
@login_required
def handle_preview_action():
    """Handle preview actions (approve, regenerate, skip, etc.)"""
    try:
        action = request.form.get('action')
        session_data = json.loads(request.form.get('session_data', '{}'))
        current_index = int(request.form.get('current_index', 0))
        adjustments = json.loads(request.form.get('adjustments', '{}'))
        
        if action == 'approve':
            # Add current image to approved list
            file_info = session_data['files'][current_index]
            base_name = os.path.splitext(file_info['filename'])[0]
            converted_path = f"outputs/preview_{session_data['session_id']}/{base_name}_coloring.png"
            
            session_data['approved_images'].append({
                'filename': f"{base_name}_coloring.png",
                'converted_path': converted_path,
                'adjustments': adjustments
            })
            
            # Move to next image
            return show_image_preview(session_data, current_index + 1)
            
        elif action == 'regenerate':
            # Regenerate current image with new settings
            return regenerate_image_with_settings(session_data, current_index, adjustments)
            
        elif action == 'skip':
            # Skip current image, move to next
            return show_image_preview(session_data, current_index + 1)
            
        elif action == 'previous':
            # Go back to previous image
            if current_index > 0:
                return show_image_preview(session_data, current_index - 1)
            else:
                return show_image_preview(session_data, current_index)
        
        # Default: continue to next image
        return show_image_preview(session_data, current_index + 1)
        
    except Exception as e:
        current_app.logger.error(f"Preview action error: {str(e)}")
        flash(f"Error processing preview action: {str(e)}", "danger")
        return render_template("convert.html")

def regenerate_image_with_settings(session_data, image_index, adjustments):
    """Regenerate image with specific settings"""
    file_info = session_data['files'][image_index]
    session_id = session_data['session_id']
    temp_dir = f"outputs/preview_{session_id}"
    
    # Load original image from file path
    pil_image = Image.open(file_info['file_path'])
    
    # Apply line art conversion with custom settings
    line_art_image = create_line_art_with_settings(pil_image, adjustments)
    
    # Save updated converted image
    base_name = os.path.splitext(file_info['filename'])[0]
    converted_path = os.path.join(temp_dir, f"{base_name}_coloring.png")
    line_art_image.save(converted_path, "PNG")
    
    # Show updated preview
    return render_template(
        "image_preview.html",
        session_data=json.dumps(session_data),
        current_index=image_index,
        total_images=len(session_data['files']),
        filename=file_info['filename'],
        original_image=f"preview_{session_id}/{base_name}_original.png",
        converted_image=f"preview_{session_id}/{base_name}_coloring.png"
    )

def create_line_art_with_settings(image, adjustments):
    """Create line art with custom settings"""
    from PIL import ImageEnhance, ImageChops

    gray = image.convert('L')

    contrast_level = adjustments.get('contrast', 'medium')
    contrast_boost = {
        'low': 1.5,
        'medium': 2.0,
        'high': 2.5
    }.get(contrast_level, 2.0)

    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(contrast_boost)

    thickness = adjustments.get('lineThickness', 'medium')
    blur_radius = {
        'thin': 1.0,
        'medium': 1.5,
        'thick': 2.0,
        'very-thick': 2.5
    }.get(thickness, 1.5)

    smoothed = gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    edges1 = smoothed.filter(ImageFilter.FIND_EDGES)
    edges2 = smoothed.filter(ImageFilter.Kernel(
        size=(3, 3),
        kernel=[-1, -1, -1, -1, 8, -1, -1, -1, -1],
        scale=1,
        offset=0
    ))
    edges3 = smoothed.filter(ImageFilter.CONTOUR)

    combined = ImageChops.darker(edges1, edges2)
    combined = ImageChops.darker(combined, edges3)

    inverted = ImageOps.invert(combined)

    threshold = {
        'low': 220,
        'medium': 200,
        'high': 180
    }.get(contrast_level, 200)

    def apply_adjustable_threshold(x):
        return 255 if x > threshold else 0
    binary = inverted.point(apply_adjustable_threshold, mode='1')

    min_size = {
        'thin': 1,
        'medium': 3,
        'thick': 3,
        'very-thick': 5
    }.get(thickness, 3)

    clean = binary.convert('L')
    clean = clean.filter(ImageFilter.MinFilter(size=min_size))
    clean = clean.filter(ImageFilter.MaxFilter(size=min_size))

    def final_threshold(x):
        return 255 if x > 128 else 0
    clean = clean.point(final_threshold, mode='1')

    result = clean.convert('RGB')
    return result