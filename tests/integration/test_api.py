import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


class TestAuthenticationEndpoints:

    def test_registration_page(self, client):
        response = client.get("/register")
        assert response.status_code == 200

    def test_login_page(self, client):
        response = client.get("/login")
        assert response.status_code == 200


class TestConverterEndpoints:

    def test_dashboard_requires_login(self, client):
        response = client.get("/convert/dashboard")
        assert response.status_code == 302

    def test_convert_page_requires_login(self, client):
        response = client.get("/convert/convert")
        assert response.status_code == 302


class TestStaticPages:

    def test_index_page(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_404_error(self, client):
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
