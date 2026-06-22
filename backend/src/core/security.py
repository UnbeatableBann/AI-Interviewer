from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import bcrypt
import jwt
from src.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a plain text password matches its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generates a secure hash from a plain text password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(subject: str | Any, tenant_id: str, scopes: list[str]) -> str:
    """Generates an access token with a specified tenant and scopes payload."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": tenant_id,
        "scopes": scopes,
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: str | Any, tenant_id: str) -> str:
    """Generates a long-lived refresh token for credential rotation."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": tenant_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decodes and validates a JWT token signature."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError("Token signature has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token payload")
