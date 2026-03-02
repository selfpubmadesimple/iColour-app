from flask import Blueprint, render_template, redirect, url_for
from flask_security import current_user, login_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Home page route"""
    if current_user.is_authenticated:
        return redirect(url_for("converter.dashboard"))
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Redirect dashboard to converter dashboard"""
    return redirect(url_for("converter.dashboard"))

@main_bp.route("/about")
def about():
    return render_template("index.html")