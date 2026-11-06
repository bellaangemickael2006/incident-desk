class ResponsePolicyMiddleware:
    """Security headers for every response."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/management-k9b4x2/"):
            # Django admin uses inline scripts and styles — allow 'unsafe-inline'
            # but keep other controls tight.
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
                "form-action 'self'"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self' data:; object-src 'none'; base-uri 'none'; "
                "frame-ancestors 'none'; form-action 'self'"
            )
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        # Never let a shared cache retain private/authentication pages.
        if request.user.is_authenticated or request.path.startswith("/accounts/"):
            response.headers["Cache-Control"] = "no-store, private"
        return response
