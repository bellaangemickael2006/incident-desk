import traceback as _tb
_init_error = None
try:
    from config.wsgi import application
except Exception:
    _init_error = _tb.format_exc()
    def application(environ, start_response):
        body = ("Django init error:\n" + _init_error).encode()
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
