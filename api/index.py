import traceback as _tb

# All third-party imports INSIDE a try-except so that:
# 1. Vercel's static import tracer can see them and bundle the packages.
# 2. Any runtime failure (broken binary, missing lib) is caught here and
#    reported as a 200 plain-text diagnostic response instead of Vercel's
#    native 500, which provides no error detail.
_error: str | None = None
_wsgi_app = None

try:
    import django           # noqa: F401
    import dotenv           # noqa: F401
    import dj_database_url  # noqa: F401
    import psycopg          # noqa: F401
    import whitenoise       # noqa: F401
    import sqlparse         # noqa: F401
    from config.wsgi import application as _wsgi_app
except Exception:
    _error = _tb.format_exc()


def application(environ, start_response):
    if _error or _wsgi_app is None:
        body = ("Django init error:\n" + (_error or "wsgi app is None")).encode()
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
    return _wsgi_app(environ, start_response)
