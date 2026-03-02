from flask import Blueprint, render_template, request, flash, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image, ImageFilter, ImageOps
import os
import uuid
from datetime import datetime

simple_bp = Blueprint("simple", __name__)

def allowed_image_file(filename):
    """Check if file is PNG or JPG"""
    if not filename:
        return False
    return filename.lower().endswith(('.png', '.jpg', '.jpeg'))

def create_coloring_page(image):
    """Create high-contrast coloring page sized for 8.5x11" printing"""
    from PIL import ImageFilter, ImageOps, ImageEnhance
    
    # First, resize image to fit 8.5" x 11" at 300 DPI (2550 x 3300 pixels)
    # Maintain aspect ratio and center on white background
    target_width, target_height = 2550, 3300
    
    # Calculate scaling to fit within target dimensions
    scale = min(target_width / image.width, target_height / image.height)
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    
    # Resize image maintaining aspect ratio
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create white background and center the image
    final_img = Image.new('RGB', (target_width, target_height), 'white')
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    final_img.paste(resized, (x_offset, y_offset))
    
    # Convert to grayscale for edge detection
    gray = final_img.convert('L')
    
    # Super simple approach - just create a basic black and white version first
    # Let's see what we're working with
    
    # Very basic threshold - anything darker than middle gray becomes black
    def simple_black_white(x):
        return 0 if x < 128 else 255  # Simple middle threshold
    
    thick_edges = gray.point(simple_black_white, mode='L')
    
    # Create final result - start with pure white
    final_result = Image.new('RGB', (target_width, target_height), 'white')
    
    # Apply the black lines to the white background
    pixels = final_result.load()
    edge_pixels = thick_edges.load()
    
    for i in range(final_result.width):
        for j in range(final_result.height):
            if edge_pixels[i, j] < 128:  # If this pixel should be black
                pixels[i, j] = (0, 0, 0)  # Make it black
            # Otherwise leave it white (already white from background)
    
    return final_result

@simple_bp.route("/simple")
@login_required
def simple_upload():
    """Simple upload page"""
    return render_template("simple_convert.html")

@simple_bp.route("/simple", methods=["POST"])
@login_required
def process_simple():
    """Process single image file"""
    if 'image_file' not in request.files:
        flash("Please select an image file.", "danger")
        return render_template("simple_convert.html")
    
    file = request.files['image_file']
    
    if not file or not file.filename:
        flash("Please select an image file.", "danger")
        return render_template("simple_convert.html")
    
    if not allowed_image_file(file.filename):
        flash("Please upload a PNG or JPG file only.", "danger")
        return render_template("simple_convert.html")
    
    try:
        # Open and process image
        image = Image.open(file.stream)
        
        # Convert to coloring page
        coloring_page = create_coloring_page(image)
        
        # Save result
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_coloring_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        coloring_page.save(output_path, "PNG")
        
        # Show result page
        return render_template("simple_result.html", 
                             original_filename=filename,
                             output_filename=output_filename)
        
    except Exception as e:
        current_app.logger.error(f"Conversion error: {str(e)}")
        flash(f"Error processing image: {str(e)}", "danger")
        return render_template("simple_convert.html")

@simple_bp.route("/download-simple/<filename>")
@login_required
def download_simple(filename):
    """Download converted file"""
    try:
        file_path = os.path.join("outputs", filename)
        if not os.path.exists(file_path):
            flash("File not found.", "warning")
            return render_template("simple_convert.html")
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f"Download error: {str(e)}", "danger")
        return render_template("simple_convert.html")