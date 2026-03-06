from datetime import datetime, timedelta
from typing import Optional

from core.config import settings
from jose import jwt, JWTError


def create_jwt(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
):
    to_encode = data.copy()
    
    # Default expiration based on token type
    if not expires_delta:
        if token_type == "access":
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == "refresh":
            expires_delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        else:
            expires_delta = timedelta(hours=24)  # default for custom
    
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    
    # Use provided or default keys
    secret_key = secret_key or settings.SECRET_KEY
    algorithm = algorithm or settings.ALGORITHM
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

# Decode JWT token
def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError: 
        return None
