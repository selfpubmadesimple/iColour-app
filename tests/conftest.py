import os
import tempfile

import pytest

from app_security import app
from models_security import db, Activity, User


@pytest.fixture
def test_app():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECURITY_PASSWORD_HASH"] = "pbkdf2_sha256"
    app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
    app.config["OUTPUT_FOLDER"] = tempfile.mkdtemp()

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_user(test_app):
    from flask_security import hash_password
    import uuid

    with test_app.app_context():
        user = User()
        user.email = "test@example.com"
        user.username = "testuser"
        user.password = hash_password("testpass123")
        user.active = True
        user.fs_uniquifier = str(uuid.uuid4())

        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_pdf_path():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    pdf_path = tempfile.mktemp(suffix=".pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Sample PDF for testing")
    c.showPage()
    c.save()

    yield pdf_path

    if os.path.exists(pdf_path):
        os.remove(pdf_path)


@pytest.fixture
def sample_image_data():
    import io
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.getvalue()
