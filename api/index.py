import traceback as _tb

# This bare import is at module level so Vercel's static tracer bundles all
# Django/dotenv/psycopg transitive deps even though the real import below
# sits inside a try-except for error surfacing.
import config.environment as _ce  # noqa: F401

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
