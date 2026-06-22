from typing import Annotated, List
from fastapi import Depends, Header
from fastapi.security import APIKeyHeader
import jwt
from pydantic import BaseModel, Field
from src.core.constants import BEARER_PREFIX, TENANT_HEADER
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    TenantIsolationError,
)
from src.core.security import decode_token
from src.shared.utils.context import set_user_id

# Header dependency mapping HTTP Authorization Bearer token
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)


class CurrentUser(BaseModel):
    """Domain model payload showing details of the current authenticated request user."""

    id: str = Field(..., description="Unique user UUID.")
    tenant_id: str = Field(..., description="Tenant namespace user belongs to.")
    scopes: List[str] = Field(default_factory=list, description="Assigned RBAC scopes.")


async def get_current_user(
    authorization: Annotated[str | None, Depends(oauth2_scheme)] = None,
    x_tenant_id: Annotated[str | None, Header(alias=TENANT_HEADER)] = None,
) -> CurrentUser:
    """Decodes and validates the authorization token, checking tenant isolation boundary."""
    if not authorization:
        raise AuthenticationError("Authorization header is missing or empty.")

    if not authorization.startswith(BEARER_PREFIX):
        raise AuthenticationError(
            f"Authorization header must use {BEARER_PREFIX}scheme."
        )

    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError(str(exc))

    user_id = payload.get("sub")
    token_tenant_id = payload.get("tenant_id")
    scopes = payload.get("scopes", [])

    if not user_id or not token_tenant_id:
        raise AuthenticationError(
            "Token payload is missing required identification fields."
        )

    # Core Row-Level Multi-Tenant Isolation Check:
    # Ensure token tenant claims match active HTTP header Tenant context variable
    if x_tenant_id and token_tenant_id != x_tenant_id:
        raise TenantIsolationError(
            f"Access Denied: Tenant context '{x_tenant_id}' does not match user registry '{token_tenant_id}'."
        )

    # Bind current user ID inside contextvars for structured audit tracking
    set_user_id(user_id)

    return CurrentUser(id=user_id, tenant_id=token_tenant_id, scopes=scopes)


class ScopeChecker:
    """Factory dependency to enforce specific RBAC scopes on route endpoints."""

    def __init__(self, required_scopes: List[str]) -> None:
        self.required_scopes = required_scopes

    def __call__(
        self, current_user: Annotated[CurrentUser, Depends(get_current_user)]
    ) -> CurrentUser:
        # Check if user has all required scopes
        for scope in self.required_scopes:
            if scope not in current_user.scopes:
                raise AuthorizationError(
                    f"Insufficient permissions. Required scope context: '{scope}'."
                )
        return current_user
