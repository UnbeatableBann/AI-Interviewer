from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_CONNECTION],   # change to specific domains in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Force HTTPS in production
    if getattr(settings, "ENABLE_HTTPS_REDIRECT", False):
        app.add_middleware(HTTPSRedirectMiddleware)

    # Restrict allowed hosts
    if getattr(settings, "ALLOWED_HOSTS", None):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,  # e.g., ["example.com", "api.example.com"]
        )
