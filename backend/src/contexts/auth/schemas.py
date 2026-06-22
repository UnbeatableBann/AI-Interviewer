from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from src.core.enums import UserRole


class UserRegister(BaseModel):
    """Payload to register a new user account."""

    email: EmailStr = Field(..., description="Unique user email address.")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Secure user password."
    )
    role: UserRole = Field(
        ..., description="Role to assume (Candidate or Recruiter only)."
    )
    tenant_id: str = Field(
        ..., min_length=2, max_length=50, description="Organization Tenant Namespace."
    )

    @field_validator("role")
    @classmethod
    def validate_role_self_registration(cls, v: UserRole) -> UserRole:
        """Restricts self-registration to Candidate and Recruiter roles only."""
        if v == UserRole.ADMIN:
            raise ValueError("Direct registration of Admin accounts is forbidden.")
        return v


class UserLogin(BaseModel):
    """Payload containing user login credentials."""

    email: EmailStr = Field(..., description="Registered email address.")
    password: str = Field(..., description="User password.")


class UserResponse(BaseModel):
    """API serialization layout for returning User details."""

    id: uuid.UUID
    tenant_id: str
    email: EmailStr
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """API payload mapping successful token generation."""

    access_token: str = Field(..., description="JWT short-lived access token.")
    refresh_token: str = Field(..., description="JWT long-lived refresh token.")
    token_type: str = Field("Bearer", description="HTTP authorization type scheme.")


class TokenRefreshRequest(BaseModel):
    """Payload containing target token to rotate."""

    refresh_token: str = Field(..., description="Active refresh token to swap.")


class PasswordResetRequest(BaseModel):
    """Payload to initiate a password reset workflow."""

    email: EmailStr = Field(..., description="Account email to reset password for.")


class PasswordResetConfirm(BaseModel):
    """Payload to confirm password updates."""

    token: str = Field(..., description="Password reset validation token.")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New secure password."
    )


class EmailVerifyConfirm(BaseModel):
    """Payload containing email verification token."""

    token: str = Field(..., description="Account email verification token.")
