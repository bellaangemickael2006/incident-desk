# Explicitly import every third-party package at module level so Vercel's
# static import tracer bundles them. The tracer only follows direct imports
# in this file; it does NOT follow transitive imports through other modules.
import django           # noqa: F401
import dotenv          # noqa: F401
import dj_database_url  # noqa: F401
import psycopg         # noqa: F401
import whitenoise      # noqa: F401
import sqlparse        # noqa: F401

import traceback as _tb

_init_error = None
_wsgi_app = None

try:
    from config.wsgi import application as _wsgi_app
except Exception:
    _init_error = _tb.format_exc()


def application(environ, start_response):
    if _init_error or _wsgi_app is None:
        err = _init_error or "Unknown init error (wsgi app is None)"
        body = ("Django init error:\n" + err).encode()
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
    return _wsgi_app(environ, start_response)
