"""
Temporary one-shot setup endpoint.
Runs Django migrations and creates initial users.
Protected by DJANGO_SETUP_TOKEN env var.
DELETE this file after use.
"""
import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

import django
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from config.wsgi import application as _django_app


def _run_setup():
    results = []

    # Run migrations
    try:
        call_command("migrate", "--no-input", verbosity=0)
        results.append("migrations: OK")
    except Exception as e:
        results.append(f"migrations: ERROR {e}")
        return results

    admin_pw = os.environ.get("DJANGO_ADMIN_PASSWORD", "")
    demo_pw = os.environ.get("DJANGO_DEMO_PASSWORD", "")

    if not admin_pw or not demo_pw:
        results.append("ERROR: DJANGO_ADMIN_PASSWORD and DJANGO_DEMO_PASSWORD must be set")
        return results

    # Create superuser (admin)
    try:
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="bellaangemickael2006@gmail.com",
                password=admin_pw,
                first_name="Admin",
                last_name="User",
            )
            results.append("superuser admin: created")
        else:
            results.append("superuser admin: already exists")
    except Exception as e:
        results.append(f"superuser: ERROR {e}")

    # Create demo reporter account
    try:
        if not User.objects.filter(username="fabrice.kameni").exists():
            User.objects.create_user(
                username="fabrice.kameni",
                email="fabrice.kameni@marquette.edu",
                password=demo_pw,
                first_name="Fabrice",
                last_name="Kameni",
                is_staff=False,
                is_superuser=False,
            )
            results.append("demo user fabrice.kameni: created")
        else:
            results.append("demo user fabrice.kameni: already exists")
    except Exception as e:
        results.append(f"demo user: ERROR {e}")

    return results


def application(environ, start_response):
    """WSGI entry point for this setup script."""
    # Only allow POST to /setup/
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "")

    if path != "/setup/" or method != "POST":
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not found"]

    # Token check
    expected_token = os.environ.get("DJANGO_SETUP_TOKEN", "")
    if not expected_token:
        start_response("503 Service Unavailable", [("Content-Type", "text/plain")])
        return [b"Setup disabled"]

    # Read token from header
    provided = environ.get("HTTP_X_SETUP_TOKEN", "")
    if provided != expected_token:
        start_response("401 Unauthorized", [("Content-Type", "text/plain")])
        return [b"Invalid token"]

    # Run setup
    try:
        results = _run_setup()
        body = "\n".join(results).encode()
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [body]
    except Exception as e:
        body = f"ERROR: {e}".encode()
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [body]
