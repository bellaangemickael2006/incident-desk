"""
Temporary one-shot setup endpoint.
Runs Django migrations and creates initial users.
Protected by DJANGO_SETUP_TOKEN env var.
DELETE this file after use.
"""
import os
import sys
import traceback

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

_django_ready = False
_init_error = None

try:
    import django
    django.setup()
    from django.core.management import call_command
    from django.contrib.auth.models import User
    _django_ready = True
except Exception:
    _init_error = traceback.format_exc()


def _run_setup():
    results = []

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
    if not _django_ready:
        body = f"Django init failed:\n{_init_error}".encode()
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [body]

    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "")

    if path != "/setup/" or method != "POST":
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not found"]

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
    except Exception as e:
        body = f"ERROR: {traceback.format_exc()}".encode()
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [body]
