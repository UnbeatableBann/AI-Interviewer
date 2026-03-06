from fastapi import FastAPI
from middleware import setup_cors
from routes import auth_routes, candidate_routes, hr_routes, admin_routes
from scalar_fastapi import get_scalar_api_reference

from utils.exception import EmailSendException, email_send_exception_handler
from utils.redis_client import check_redis_connection

app = FastAPI(
    title="AI Mock Interviewer",
    description="""
AI Mock Interviewer API provides endpoints for:

- **Authentication**: Register, login, refresh tokens, and manage passwords.
- **Candidate operations**: Save personal info, submit answers, generate questions, get evaluation results.
- **HR operations**: Manage interviews, fetch student information.
- **Admin operations**: Manage users and HR accounts.

Features include:

- OTP-based email verification.
- JWT-based authentication with access and refresh tokens.
- LLM-powered interview question generation.
- Redis integration for OTP and caching.
- Custom exception handling and logging.
"""
)

# Configure CORS middleware
setup_cors(app)

# Register custom exception handler for email sending errors
app.add_exception_handler(EmailSendException, email_send_exception_handler)

# Include API routers with prefixes and tags for documentation
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(candidate_routes.router, prefix="/candidate", tags=["candidate"])
app.include_router(hr_routes.router, prefix="/hr", tags=["hr"])
app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])


@app.get("/", summary="Health check endpoint", description="Check API health and Redis connectivity.")
async def health_check():
    """
    Simple health check endpoint.

    Returns:
    - {"status": "ok"} if Redis is connected.
    - {"status": "Redis not working."} if Redis is unavailable.
    """
    ping = await check_redis_connection()
    if not ping:
        return {"status": "Redis not working."}
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    """
    Return the Scalar API reference.

    This endpoint is hidden from OpenAPI/Swagger docs (`include_in_schema=False`).
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar"
    )
