import traceback as _tb

_init_error = None
_wsgi = None

try:
    from config.wsgi import application as _wsgi
except Exception:
    _init_error = _tb.format_exc()


def application(environ, start_response):
    if _init_error or _wsgi is None:
        err = _init_error or "Unknown init error (no wsgi app)"
        body = ("Django init error:\n" + err).encode()
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
    return _wsgi(environ, start_response)
