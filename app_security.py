import os
import uuid
from flask import Flask
from flask_mail import Mail
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from models_security import db, User, Role

# Create app
app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
    SECURITY_PASSWORD_SALT=os.environ.get("SECURITY_PASSWORD_SALT", "dev-salt-change-in-production"),
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
    SQLALCHEMY_ENGINE_OPTIONS={
        "pool_recycle": 300,
        "pool_pre_ping": True,
    },
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    
    # File upload configuration
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100MB max file size
    UPLOAD_FOLDER="uploads",
    OUTPUT_FOLDER="outputs",
    
    # Flask-Security-Too settings
    SECURITY_REGISTERABLE=True,
    SECURITY_TRACKABLE=True,
    SECURITY_RECOVERABLE=False,  # Disable password recovery for now (no email configured)
    SECURITY_CHANGEABLE=True,
    SECURITY_CONFIRMABLE=False,  # Disable email confirmation for now
    SECURITY_SEND_REGISTER_EMAIL=False,
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=None,
    SECURITY_EMAIL_VALIDATOR_ARGS={"check_deliverability": False},
    SECURITY_PASSWORD_HASH="pbkdf2_sha256",  # Use simpler hashing method
    SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED=("An account with this email address already exists. Please use a different email or try logging in.", "error"),
    SECURITY_FLASH_MESSAGES=True,
    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT="converter.dashboard",
    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT="main.index",
    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT="converter.dashboard",
    
    # Mail settings (optional - for password recovery)
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "localhost"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"],
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
)

# Proxy fix for deployment
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize extensions
db.init_app(app)
mail = Mail(app)
csrf = CSRFProtect(app)

# Create upload and output directories
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Initialize database function
def create_user():
    try:
        db.create_all()
        
        # Create default roles if they don't exist
        if not user_datastore.find_role("admin"):
            user_datastore.create_role(name="admin", description="Administrator")
        if not user_datastore.find_role("user"):
            user_datastore.create_role(name="user", description="Regular User")
        
        # Create a default admin user if none exists
        if not user_datastore.find_user(email="admin@example.com"):
            admin_user = user_datastore.create_user(
                email="admin@example.com",
                username="admin",
                password="password123",  # Change this in production!
                fs_uniquifier=str(uuid.uuid4()),
                active=True
            )
            user_datastore.add_role_to_user(admin_user, "admin")
            user_datastore.add_role_to_user(admin_user, "user")
        
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")
        db.session.rollback()

# Error handlers for file upload issues
@app.errorhandler(413)
def request_entity_too_large(error):
    from flask import flash, redirect, url_for, render_template
    return render_template('file_too_large.html'), 413

@app.errorhandler(500) 
def internal_error(error):
    db.session.rollback()
    from flask import render_template
    return render_template("base.html", error_message="Internal server error"), 500

# Initialize database immediately 
with app.app_context():
    create_user()

# Import routes after app setup to avoid circular imports
from routes.main import main_bp
from routes.converter import converter_bp
from routes.dashboard import dashboard_bp
from tools.file_upload.routes import file_upload_bp
from simple_converter import simple_bp

# Register main application blueprints
app.register_blueprint(main_bp)
app.register_blueprint(converter_bp, url_prefix="/convert")
app.register_blueprint(dashboard_bp)
app.register_blueprint(file_upload_bp)
app.register_blueprint(simple_bp)

# Optional: Add Replit Auth as alternative (battle-tested authentication)
try:
    from replit_auth import make_replit_blueprint, ReplitOAuth  # noqa: F401
    with app.app_context():
        db.create_all()
    replit_bp = make_replit_blueprint()
    app.register_blueprint(replit_bp, url_prefix="/replit_auth")
    app.logger.info("Replit Auth available at /replit_auth/login")
except ImportError as e:
    app.logger.info(f"Replit Auth not available: {e}")
except Exception as e:
    app.logger.warning(f"Could not initialize Replit Auth: {e}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)