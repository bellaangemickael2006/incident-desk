import traceback as _tb

# Guard every third-party import so a missing/broken package still allows
# `application` to be defined and serve a diagnostic 200 response.
_import_errors: list[str] = []
_init_error: str | None = None
_wsgi_app = None


def _try_import(name: str) -> None:
    try:
        __import__(name)
    except Exception:
        _import_errors.append(f"[{name}]\n{_tb.format_exc()}")


_try_import("django")
_try_import("dotenv")
_try_import("dj_database_url")
_try_import("psycopg")
_try_import("whitenoise")
_try_import("sqlparse")

if not _import_errors:
    try:
        from config.wsgi import application as _wsgi_app  # noqa: E402
    except Exception:
        _init_error = _tb.format_exc()


def application(environ, start_response):
    if _import_errors or _init_error or _wsgi_app is None:
        parts = []
        if _import_errors:
            parts.append("=== IMPORT ERRORS ===\n" + "\n---\n".join(_import_errors))
        if _init_error:
            parts.append("=== DJANGO INIT ERROR ===\n" + _init_error)
        if not parts:
            parts.append("=== UNKNOWN: wsgi app is None ===")
        body = "\n\n".join(parts).encode()
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
    return _wsgi_app(environ, start_response)
