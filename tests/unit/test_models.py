import pytest

from models_security import db, Activity, User


class TestUserModel:

    def test_user_creation(self, test_app):
        import uuid
        with test_app.app_context():
            user = User()
            user.email = "newuser@example.com"
            user.username = "newuser"
            user.password = "hashed_placeholder"
            user.active = True
            user.fs_uniquifier = str(uuid.uuid4())

            assert user.email == "newuser@example.com"
            assert user.username == "newuser"
            assert user.active is True

    def test_user_representation(self, test_app):
        user = User()
        user.email = "repr@example.com"
        assert str(user) == "<User repr@example.com>"

    def test_user_relationships(self, test_app, test_user):
        with test_app.app_context():
            activity = Activity()
            activity.user_id = test_user.id
            activity.filename = "test.pdf"
            activity.pages_converted = 5
            activity.processing_duration = 120.5
            activity.output_filename = "test_output.zip"
            activity.status = "completed"
            db.session.add(activity)
            db.session.commit()

            user = db.session.get(User, test_user.id)
            assert activity in user.activities.all()

    def test_get_total_conversions(self, test_app, test_user):
        with test_app.app_context():
            assert test_user.get_total_conversions() == 0

            for i in range(3):
                activity = Activity()
                activity.user_id = test_user.id
                activity.filename = f"test{i}.pdf"
                activity.pages_converted = i + 1
                activity.processing_duration = 60.0
                activity.output_filename = f"test{i}_output.zip"
                activity.status = "completed"
                db.session.add(activity)
            db.session.commit()

            assert test_user.get_total_conversions() == 3

    def test_get_total_pages_converted(self, test_app, test_user):
        with test_app.app_context():
            assert test_user.get_total_pages_converted() == 0

            page_counts = [3, 5, 7]
            for i, pages in enumerate(page_counts):
                activity = Activity()
                activity.user_id = test_user.id
                activity.filename = f"test{i}.pdf"
                activity.pages_converted = pages
                activity.processing_duration = 60.0
                activity.output_filename = f"test{i}_output.zip"
                activity.status = "completed"
                db.session.add(activity)
            db.session.commit()

            assert test_user.get_total_pages_converted() == 15


class TestActivityModel:

    def test_activity_creation(self, test_app, test_user):
        activity = Activity()
        activity.user_id = test_user.id
        activity.filename = "test.pdf"
        activity.pages_converted = 5
        activity.processing_duration = 120.5
        activity.output_filename = "test_output.zip"
        activity.status = "completed"

        assert activity.filename == "test.pdf"
        assert activity.pages_converted == 5
        assert activity.status == "completed"

    def test_activity_representation(self, test_app, test_user):
        activity = Activity()
        activity.user_id = test_user.id
        activity.filename = "test.pdf"
        activity.pages_converted = 5
        activity.processing_duration = 120.5
        activity.output_filename = "test_output.zip"
        assert str(activity) == "<Activity test.pdf - 5 pages>"

    def test_get_formatted_duration_seconds(self, test_app):
        activity = Activity()
        activity.processing_duration = 45.7
        assert activity.get_formatted_duration() == "45.7 seconds"

    def test_get_formatted_duration_minutes(self, test_app):
        activity = Activity()
        activity.processing_duration = 125.0
        assert activity.get_formatted_duration() == "2m 5s"

    def test_get_formatted_duration_hours(self, test_app):
        activity = Activity()
        activity.processing_duration = 3725.0
        assert activity.get_formatted_duration() == "1h 2m"

    def test_activity_statuses(self, test_app, test_user):
        with test_app.app_context():
            statuses = ["completed", "failed", "processing"]
            for status in statuses:
                activity = Activity()
                activity.user_id = test_user.id
                activity.filename = f"test_{status}.pdf"
                activity.pages_converted = 5 if status == "completed" else 0
                activity.processing_duration = 120.0
                activity.output_filename = "test_output.zip" if status == "completed" else ""
                activity.status = status
                if status == "failed":
                    activity.error_message = "Test error message"
                db.session.add(activity)
            db.session.commit()

            activities = Activity.query.filter_by(user_id=test_user.id).all()
            assert len(activities) == 3
            status_list = [a.status for a in activities]
            assert "completed" in status_list
            assert "failed" in status_list
            assert "processing" in status_list
