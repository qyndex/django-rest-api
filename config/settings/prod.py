"""Production settings."""
import os

from .base import *  # noqa: F401, F403

DEBUG = False

# In production DJANGO_SECRET_KEY must be set — fail fast with a clear message.
_secret = os.environ.get("DJANGO_SECRET_KEY", "")
if not _secret:
    raise RuntimeError(
        "DJANGO_SECRET_KEY environment variable is not set. "
        "Set it before starting the production server."
    )
SECRET_KEY = _secret  # noqa: F405  (overrides base.py)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if h.strip()
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "app"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() in (
    "1",
    "true",
    "yes",
)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
