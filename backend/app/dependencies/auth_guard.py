from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import settings
from schemas.user_schemas import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        userid: str = payload.get("userid")
        email: str = payload.get("email")
        role: str = payload.get("role")
        if userid is None or email is None:
            raise credentials_exception
        return UserOut(userid=userid, email=email, role=role)
    except JWTError:
        raise credentials_exception

def require_role(allowed_roles: list[str]):
    async def role_checker(user=Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Requires one of: {allowed_roles}",
            )
        return user
    return role_checker