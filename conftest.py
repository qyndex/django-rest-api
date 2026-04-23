"""
Project-wide pytest fixtures.

Fixtures defined here are available to every test module without explicit
imports.  Per-app fixtures (factories etc.) live in apps/*/tests/conftest.py.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def admin_user(db) -> User:
    """A superuser that can hit any endpoint."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass",
    )


@pytest.fixture
def regular_user(db) -> User:
    """A standard (non-staff) user."""
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="userpass",
    )


@pytest.fixture
def auth_client(api_client: APIClient, regular_user: User) -> APIClient:
    """DRF test client authenticated as a regular user."""
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: User) -> APIClient:
    """DRF test client authenticated as a superuser."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user_token(regular_user: User) -> str:
    """Return a token string for the regular user."""
    token, _ = Token.objects.get_or_create(user=regular_user)
    return token.key


@pytest.fixture
def token_client(api_client: APIClient, user_token: str) -> APIClient:
    """DRF test client authenticated via Token header."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {user_token}")
    return api_client
