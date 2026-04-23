"""Tests for authentication endpoints: register and login."""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


pytestmark = pytest.mark.django_db


class TestRegisterView:
    URL = "/api/auth/register/"

    def test_register_creates_user_and_returns_token(self, api_client):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass123",
        }
        res = api_client.post(self.URL, payload, format="json")
        assert res.status_code == 201
        data = res.json()
        assert "token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "new@example.com"
        # User actually created
        assert User.objects.filter(username="newuser").exists()
        # Token is valid
        assert Token.objects.filter(key=data["token"]).exists()

    def test_register_without_email(self, api_client):
        payload = {"username": "noemail", "password": "strongpass123"}
        res = api_client.post(self.URL, payload, format="json")
        assert res.status_code == 201
        assert res.json()["user"]["email"] == ""

    def test_register_duplicate_username_rejected(self, api_client):
        User.objects.create_user(username="taken", password="pass12345678")
        payload = {"username": "taken", "password": "newpass12345"}
        res = api_client.post(self.URL, payload, format="json")
        assert res.status_code == 400

    def test_register_short_password_rejected(self, api_client):
        payload = {"username": "shortpw", "password": "abc"}
        res = api_client.post(self.URL, payload, format="json")
        assert res.status_code == 400

    def test_register_missing_username_rejected(self, api_client):
        payload = {"password": "strongpass123"}
        res = api_client.post(self.URL, payload, format="json")
        assert res.status_code == 400

    def test_register_missing_password_rejected(self, api_client):
        payload = {"username": "nopw"}
        res = api_client.post(self.URL, payload, format="json")
        assert res.status_code == 400


class TestLoginView:
    URL = "/api/auth/login/"

    def test_login_returns_token(self, api_client):
        User.objects.create_user(username="loginuser", password="mypass12345")
        res = api_client.post(
            self.URL,
            {"username": "loginuser", "password": "mypass12345"},
            format="json",
        )
        assert res.status_code == 200
        data = res.json()
        assert "token" in data
        assert data["user"]["username"] == "loginuser"

    def test_login_invalid_password_rejected(self, api_client):
        User.objects.create_user(username="loginuser2", password="rightpass123")
        res = api_client.post(
            self.URL,
            {"username": "loginuser2", "password": "wrongpass"},
            format="json",
        )
        assert res.status_code == 401
        assert "Invalid credentials" in res.json()["detail"]

    def test_login_nonexistent_user_rejected(self, api_client):
        res = api_client.post(
            self.URL,
            {"username": "ghost", "password": "doesntmatter"},
            format="json",
        )
        assert res.status_code == 401

    def test_login_missing_fields_rejected(self, api_client):
        res = api_client.post(self.URL, {}, format="json")
        assert res.status_code == 400

    def test_token_authenticates_requests(self, api_client):
        """Verify the token from login actually works for authed requests."""
        User.objects.create_user(username="tokentest", password="tokenpass123")
        login_res = api_client.post(
            self.URL,
            {"username": "tokentest", "password": "tokenpass123"},
            format="json",
        )
        token = login_res.json()["token"]

        # Use the token to create a category (requires auth)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        create_res = api_client.post(
            "/api/categories/",
            {"name": "Token Cat"},
            format="json",
        )
        assert create_res.status_code == 201


class TestTokenAuthentication:
    def test_token_header_grants_write_access(self, token_client):
        res = token_client.post(
            "/api/categories/",
            {"name": "Via Token"},
            format="json",
        )
        assert res.status_code == 201

    def test_invalid_token_rejected(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Token invalid-token-value")
        res = api_client.post(
            "/api/categories/",
            {"name": "Bad Token Cat"},
            format="json",
        )
        assert res.status_code == 401
