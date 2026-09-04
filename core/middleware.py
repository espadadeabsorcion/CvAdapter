"""
core/middleware.py

SecurityHeadersMiddleware — añade los headers de seguridad HTTP requeridos
a TODAS las respuestas del sistema, independientemente del código de estado.

Req. 11.1: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection.
"""


class SecurityHeadersMiddleware:
    """Middleware que inyecta headers de seguridad en cada respuesta HTTP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        return response
