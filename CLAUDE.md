# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django REST API — REST API built with Django 5.1 and Django REST Framework — ModelViewSets, serializers, router-based URL routing, and admin.

Built with Django 5.x, Python 3.13, and Django REST Framework.

## Commands

```bash
pip install -r requirements.txt          # Install dependencies
python manage.py runserver               # Start dev server (http://localhost:8000)
python manage.py test                    # Run tests
python manage.py makemigrations          # Create migrations
python manage.py migrate                 # Apply migrations
ruff check .                             # Lint
ruff format .                            # Format
```

## Architecture

- `manage.py` — Django management entry point
- `config/` or project root — Django settings, URLs, WSGI/ASGI
- `*/models.py` — Database models
- `*/views.py` — View functions / class-based views
- `*/serializers.py` — DRF serializers
- `*/urls.py` — URL routing
- `templates/` — Django HTML templates
- `static/` — Static assets

## Rules

- Always create migrations for model changes
- Use class-based views for CRUD, function views for simple endpoints
- Parameterized queries only — never raw SQL with string interpolation
- All new models need proper `__str__` and `Meta.ordering`
