import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security.core import UserMixin, RoleMixin

db = SQLAlchemy()

# Define models
roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Flask-Security tracking fields
    current_login_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    current_login_ip = db.Column(db.String(100))
    last_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)
    
    # Relationships
    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
    )
    activities = db.relationship(
        "Activity", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def get_recent_activities(self, limit=10):
        """Get user's recent conversion activities"""
        return self.activities.order_by(Activity.created_at.desc()).limit(limit)

    def get_total_conversions(self):
        """Get total number of conversions by this user"""
        return self.activities.count()

    def get_total_pages_converted(self):
        """Get total number of pages converted by this user"""
        return (
            db.session.query(db.func.sum(Activity.pages_converted))
            .filter_by(user_id=self.id)
            .scalar()
            or 0
        )

    def __repr__(self):
        return f"<User {self.email}>"


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    pages_converted = db.Column(db.Integer, nullable=False)
    processing_duration = db.Column(db.Float, nullable=False)  # Duration in seconds
    output_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(20), default="completed"
    )  # completed, failed, processing
    error_message = db.Column(db.Text, nullable=True)

    def get_formatted_duration(self):
        """Return processing duration in human-readable format"""
        if self.processing_duration < 60:
            return f"{self.processing_duration:.1f} seconds"
        elif self.processing_duration < 3600:
            minutes = int(self.processing_duration // 60)
            seconds = int(self.processing_duration % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(self.processing_duration // 3600)
            minutes = int((self.processing_duration % 3600) // 60)
            return f"{hours}h {minutes}m"

    def __repr__(self):
        return f"<Activity {self.filename} - {self.pages_converted} pages>"