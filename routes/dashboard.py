"""
Main dashboard routes for the hybrid microtools platform.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def main_dashboard():
    """Main tools library dashboard."""
    
    user_stats = {
        'total_conversions': current_user.get_total_conversions(),
        'total_pages': current_user.get_total_pages_converted(),
    }
    
    # Define available tools (only include working routes)
    tools = [
        {
            'id': 'coloring_page',
            'name': 'PDF to Coloring Book',
            'description': 'Transform full-color PDF illustrations into beautiful coloring books using AI technology.',
            'icon': 'book-open',
            'route': 'converter.dashboard',
            'status': 'active',
            'category': 'AI Tools'
        }
    ]
    
    # Group tools by category
    tools_by_category = {}
    for tool in tools:
        category = tool['category']
        if category not in tools_by_category:
            tools_by_category[category] = []
        tools_by_category[category].append(tool)
    
    return render_template(
        'dashboard.html',
        user_stats=user_stats,
        tools_by_category=tools_by_category,
        page_title='Tools Library'
    )


@dashboard_bp.route("/tools")
@login_required
def tools_library():
    """Alias for main dashboard."""
    return redirect(url_for('dashboard.main_dashboard'))