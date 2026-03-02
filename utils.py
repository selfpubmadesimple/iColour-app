import os
import time
from datetime import datetime, timedelta

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    """Check if file has allowed extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files(directory, max_age_hours=24):
    """Remove files older than max_age_hours"""
    try:
        cutoff_time = time.time() - (max_age_hours * 3600)

        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                except OSError:
                    pass

            # Remove empty directories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except OSError:
                    pass
    except Exception:
        pass  # Ignore cleanup errors


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def get_file_info(file_path):
    """Get file information including size and modification time"""
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "exists": True,
        }
    except OSError:
        return {"exists": False}


def validate_pdf_file(file_path):
    """Basic validation of PDF file"""
    try:
        import fitz

        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()

        if page_count == 0:
            return False, "PDF file is empty"
        if page_count > 20:
            return False, f"PDF has {page_count} pages. Maximum 20 pages allowed."

        return True, f"Valid PDF with {page_count} pages"
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"
