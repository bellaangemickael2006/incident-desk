import os
import traceback

# This module-level import must stay here so Vercel's Python builder
# traces and bundles Django. Do NOT move it into a function or block.
from config.wsgi import application as _django_app

from django.core.management import call_command as _call_command
from django.contrib.auth.models import User as _User


def _run_setup():
    results = []

    try:
        _call_command("migrate", "--no-input", verbosity=0)
        results.append("migrations: OK")
    except Exception as e:
        results.append(f"migrations: ERROR {e}")
        return results

    admin_pw = os.environ.get("DJANGO_ADMIN_PASSWORD", "")
    demo_pw = os.environ.get("DJANGO_DEMO_PASSWORD", "")

    if not admin_pw or not demo_pw:
        results.append("ERROR: DJANGO_ADMIN_PASSWORD and DJANGO_DEMO_PASSWORD must be set")
        return results

    try:
        if not _User.objects.filter(username="admin").exists():
            _User.objects.create_superuser(
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

    try:
        if not _User.objects.filter(username="fabrice.kameni").exists():
            _User.objects.create_user(
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
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "")

    if path == "/setup/" and method == "POST":
        expected_token = os.environ.get("DJANGO_SETUP_TOKEN", "")
        if not expected_token:
            start_response("503 Service Unavailable", [("Content-Type", "text/plain")])
            return [b"Setup disabled"]
        provided = environ.get("HTTP_X_SETUP_TOKEN", "")
        if provided != expected_token:
            start_response("401 Unauthorized", [("Content-Type", "text/plain")])
            return [b"Invalid token"]
        try:
            results = _run_setup()
            body = "\n".join(results).encode()
            start_response("200 OK", [("Content-Type", "text/plain")])
            return [body]
        except Exception:
            body = traceback.format_exc().encode()
            start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
            return [body]

    return _django_app(environ, start_response)
