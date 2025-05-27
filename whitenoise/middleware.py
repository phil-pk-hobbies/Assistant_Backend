"""Minimal no-op WhiteNoise middleware used for tests."""


class WhiteNoiseMiddleware:
    """No-op middleware placeholder.

    The real ``whitenoise`` package serves static files efficiently. This
    simplified version merely passes the request through so that tests do not
    fail when the external dependency is unavailable.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
