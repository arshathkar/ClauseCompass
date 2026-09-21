from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # API should not be cached
        if request.url.path.startswith("/v1/"):
            response.headers["Cache-Control"] = "no-store, max-age=0"
            
        return response


def setup_security(app: FastAPI) -> None:
    app.add_middleware(SecurityHeadersMiddleware)
