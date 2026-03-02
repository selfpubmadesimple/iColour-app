# iColour - PDF to Coloring Book Converter

## Overview

Flask-based web application that converts PDF documents and images into coloring book format. Users upload PDFs or images, which are processed through edge detection algorithms to create line art, and download results as PNG files or a ZIP archive.

## System Architecture

### Entry Point
- `main.py` imports `app` from `app_security.py` (Flask-Security-Too)
- Gunicorn serves on port 5000: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

### Backend
- **Framework**: Flask with Flask-Security-Too for authentication
- **Database**: PostgreSQL via `DATABASE_URL` env var, SQLAlchemy ORM
- **Models**: `models_security.py` (User, Role, Activity)
- **Image Processing**: PIL/Pillow for edge detection and line art conversion
- **PDF Processing**: PyMuPDF (fitz) for page extraction
- **Auth**: Flask-Security-Too (registration, login, roles) + optional Replit OAuth

### Frontend
- Jinja2 templates with Bootstrap 5 dark theme
- Feather Icons
- Custom CSS (`static/css/custom.css`) and JS (`static/js/main.js`)

### Key Files
```
main.py                    # Entry point
app_security.py            # Flask app config, security, blueprint registration
models_security.py         # User, Role, Activity models (SQLAlchemy)
routes/
  main.py                  # Home, about, dashboard redirect
  converter.py             # PDF/image conversion, preview, download
  dashboard.py             # Tools dashboard
simple_converter.py        # Simple single-image converter
utils.py                   # File validation, cleanup helpers
tools/file_upload/
  routes.py                # Drag-and-drop upload API
  storage.py               # Local/S3 file storage backend
app_replit.py              # Replit-specific Flask app (for Replit Auth)
models_replit.py           # Replit Auth models (OAuth, User)
replit_auth.py             # Replit OAuth blueprint
templates/                 # Jinja2 templates
static/                    # CSS, JS assets
tests/                     # Pytest test suite
```

### Authentication
- Primary: Flask-Security-Too (email/password registration and login)
- Secondary: Replit OAuth (optional, loaded via try/except)

### Database Schema
- **User**: email, username, password, roles, tracking fields, activities
- **Role**: name, description (admin, user)
- **Activity**: conversion history (filename, pages, duration, status)

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET` / `SECRET_KEY`: Flask session encryption
- `SECURITY_PASSWORD_SALT`: Flask-Security password salt
- `OPENAI_API_KEY`: Optional, for AI-enhanced conversion

## Dependencies
- Core: Flask, Flask-Security-Too, Flask-SQLAlchemy, Gunicorn
- Processing: PyMuPDF, Pillow (>=12.1.1), ReportLab
- Auth: Flask-Dance, OAuthLib, PyJWT
- Network: urllib3 (>=2.6.3), requests
- Storage: boto3 (optional S3 support)

## User Preferences
- Communication style: Simple, everyday language
- Authentication preference: Battle-tested systems over custom implementations
