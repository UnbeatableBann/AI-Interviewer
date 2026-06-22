from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.db import get_db
from src.contexts.auth.schemas import (
    EmailVerifyConfirm,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from src.contexts.auth.services import AuthService, TokenRotationService
from src.shared.schemas.responses import APIResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


# Dependency injection providers for authentication services
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_rotation_service(
    db: AsyncSession = Depends(get_db),
) -> TokenRotationService:
    return TokenRotationService(db)


@router.post("/register", response_model=APIResponse[UserResponse], status_code=201)
async def register(
    payload: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[UserResponse]:
    """Registers a new candidate or recruiter account, enforcing role scopes validation."""
    user = await service.register_user(payload)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    payload: UserLogin,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[TokenResponse]:
    """Authenticates credentials, initiating session mapping under brute-force protections."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = await service.login_user(
        payload, ip_address=client_ip, user_agent=user_agent
    )

    return APIResponse(
        success=True,
        data=tokens,
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(
    payload: TokenRefreshRequest,
    request: Request,
    service: TokenRotationService = Depends(get_rotation_service),
) -> APIResponse[TokenResponse]:
    """Exchanges an active refresh token for a new set, enforcing reuse breach checks."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = await service.rotate_tokens(
        payload.refresh_token, ip_address=client_ip, user_agent=user_agent
    )

    return APIResponse(
        success=True,
        data=tokens,
    )


@router.post("/verify-email", response_model=APIResponse[bool])
async def verify_email(
    payload: EmailVerifyConfirm,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[bool]:
    """Confirms account email verification codes."""
    res = await service.verify_email(payload.token)
    return APIResponse(
        success=res,
        data=res,
    )


@router.post("/password-reset/request", response_model=APIResponse[bool])
async def request_password_reset(
    payload: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[bool]:
    """Requests a password reset link token for the designated email profile."""
    await service.request_password_reset(payload.email)
    return APIResponse(
        success=True,
        data=True,
    )


@router.post("/password-reset/confirm", response_model=APIResponse[bool])
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[bool]:
    """Submits the updated password alongside the reset code validation token."""
    res = await service.confirm_password_reset(payload.token, payload.new_password)
    return APIResponse(
        success=res,
        data=res,
    )
