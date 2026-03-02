import os
from unittest.mock import MagicMock, patch

import pytest

from models_security import db, Activity, User


class TestUserRegistrationWorkflow:

    def test_registration_page_accessible(self, client):
        response = client.get("/register")
        assert response.status_code == 200

    def test_login_page_accessible(self, client):
        response = client.get("/login")
        assert response.status_code == 200


class TestUserActivityTracking:

    def test_activity_tracking(self, test_app, test_user):
        with test_app.app_context():
            for i in range(3):
                activity = Activity()
                activity.user_id = test_user.id
                activity.filename = f"test{i}.pdf"
                activity.pages_converted = i + 1
                activity.processing_duration = (i + 1) * 30.0
                activity.output_filename = f"test{i}_output.zip"
                activity.status = "completed"
                db.session.add(activity)
            db.session.commit()

            user = db.session.get(User, test_user.id)
            assert user.get_total_conversions() == 3
            assert user.get_total_pages_converted() == 6


class TestErrorHandlingWorkflow:

    def test_authentication_required_workflow(self, client):
        protected_routes = [
            "/convert/convert",
            "/convert/dashboard",
        ]
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302
