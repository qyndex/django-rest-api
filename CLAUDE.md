# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django REST API built with Django 5.x, Python 3.13, and Django REST Framework. Features Category and Product models with full CRUD via ModelViewSets, token-based authentication, search/ordering filters, and pagination.

## Commands

```bash
pip install -r requirements.txt          # Install dependencies
python manage.py runserver               # Start dev server (http://localhost:8000)
python manage.py migrate                 # Apply migrations
python manage.py seed                    # Seed database with sample data
python manage.py seed --clear            # Clear and re-seed
python manage.py createsuperuser         # Create admin user
pytest                                   # Run tests (uses pytest.ini)
pytest -k test_auth                      # Run auth tests only
ruff check .                             # Lint
ruff format .                            # Format
```

## Architecture

- `manage.py` -- Django management entry point
- `config/` -- Django settings (split: base/dev/prod), URLs, WSGI
- `config/settings/base.py` -- Shared settings (REST framework, auth, pagination)
- `config/settings/dev.py` -- SQLite, DEBUG=True, fast password hashing
- `config/settings/prod.py` -- PostgreSQL, security hardening, requires DJANGO_SECRET_KEY
- `apps/api/models.py` -- Category and Product models (Product has created_by FK to User)
- `apps/api/serializers.py` -- DRF serializers including RegisterSerializer/LoginSerializer
- `apps/api/viewsets.py` -- ModelViewSets with IsAuthenticatedOrReadOnly permissions
- `apps/api/views.py` -- Auth views (RegisterView, LoginView) returning tokens
- `apps/api/urls.py` -- Router-based URL routing + auth endpoints
- `apps/api/admin.py` -- Admin registrations
- `apps/api/management/commands/seed.py` -- Database seeding command
- `apps/api/migrations/` -- Django migrations (0001_initial)
- `apps/api/tests/` -- Tests (models, views, serializers, auth, integration)
- `conftest.py` -- Project-wide pytest fixtures (api_client, auth_client, token_client)

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Create account, returns token |
| POST | `/api/auth/login/` | No | Login, returns token |
| GET | `/api/categories/` | No | List categories (paginated) |
| POST | `/api/categories/` | Yes | Create category |
| GET | `/api/categories/{id}/` | No | Retrieve category |
| PUT/PATCH | `/api/categories/{id}/` | Yes | Update category |
| DELETE | `/api/categories/{id}/` | Yes | Delete category |
| GET | `/api/products/` | No | List products (paginated) |
| POST | `/api/products/` | Yes | Create product (sets created_by) |
| GET | `/api/products/{id}/` | No | Retrieve product |
| PUT/PATCH | `/api/products/{id}/` | Yes | Update product |
| DELETE | `/api/products/{id}/` | Yes | Delete product |
| GET | `/api/products/active/` | No | List active products |
| GET | `/api/products/low-stock/` | No | List low-stock products |

## Authentication

Token-based authentication via `rest_framework.authtoken`. Include the token in the `Authorization` header:

```
Authorization: Token <your-token>
```

Read endpoints (GET) are open. Write endpoints (POST/PUT/PATCH/DELETE) require authentication.

## Rules

- Always create migrations for model changes: `python manage.py makemigrations api`
- Use class-based views for CRUD, function views for simple endpoints
- Parameterized queries only -- never raw SQL with string interpolation
- All new models need proper `__str__` and `Meta.ordering`
- Run tests before committing: `pytest`
- Token auth required for write operations (IsAuthenticatedOrReadOnly)
- Product.created_by is set automatically via perform_create
- Settings are split: base.py (shared) / dev.py (SQLite) / prod.py (PostgreSQL)
- PAGE_SIZE is 20 (configurable in base.py REST_FRAMEWORK settings)
