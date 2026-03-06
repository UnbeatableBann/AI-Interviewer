from core.config import settings
from dependencies.auth_guard import get_current_user
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user_schemas import (
    EmailRequest,
    OTPVerifyRequest,
    ResetPasswordRequest,
    SetNewPasswordRequest,
    UserOut,
    UserSignUp,
)
from services.auth_service import (
    get_user_by_email,
    new_password_service,
    register_user,
    reset_password_service,
)
from utils.email_verify import generate_otp, send_email
from utils.exception import EmailSendException
from utils.jwt import create_jwt, decode_jwt
from utils.redis_client import delete_otp, get_otp, set_otp
from utils.security import verify_password

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    summary="Register a new user",
    description="""
Create a new user account.

- Checks if the email is already registered.
- Saves the user to the database.
- Returns the created user details.

Raises:
- 409 Conflict: if the email is already registered.
- 500 Internal Server Error: if saving the user fails.
"""
)
async def register(user: UserSignUp):
    if await get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    db_user = await register_user(user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot save the details",
        )
    return db_user


@router.post(
    "/login",
    summary="User login",
    description="""
Authenticate a user and generate JWT access and refresh tokens.

- Validates user credentials.
- Returns access and refresh tokens with bearer type.

Raises:
- 401 Unauthorized: if credentials are invalid.
"""
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await get_user_by_email(form_data.username)

    if not db_user or not await verify_password(form_data.password, db_user.hashedpassword):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_jwt(
        data={"email": db_user.email, "userid": db_user.userid, "role": db_user.role},
        token_type="access"
    )
    refresh_token = create_jwt(
        data={"email": db_user.email, "userid": db_user.userid, "role": db_user.role},
        token_type="refresh"
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    summary="Get current user info",
    description="Fetch details of the currently authenticated user."
)
async def me(user: UserOut = Depends(get_current_user)):
    return user


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="""
Generate a new access token and refresh token using a valid refresh token.

- Validates the refresh token.
- Returns new access and refresh tokens.

Raises:
- 401 Unauthorized: if the refresh token is invalid or expired.
"""
)
async def refresh_token(refresh_token: str):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    userid = payload.get("userid")
    email = payload.get("email")
    role = payload.get("role")

    access_token = create_jwt(
        data={"email": email, "userid": userid, "role": role},
        token_type="access"
    )
    new_refresh_token = create_jwt(
        data={"email": email, "userid": userid, "role": role},
        token_type="refresh"
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "userid": userid,
    }


@router.post(
    "/send-otp",
    summary="Send OTP to user email",
    description="""
Generate and send a One-Time Password (OTP) to the user's email for verification.

- OTP is stored in Redis with expiry.
- Email sending is done asynchronously in the background.

Raises:
- 500 Internal Server Error: if OTP cannot be stored or email sending fails.
"""
)
async def send_otp(data: EmailRequest, background_tasks: BackgroundTasks):
    otp = generate_otp()
    result = await set_otp(data.email, otp, settings.OTP_EXPIRY)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to store OTP. Try again.")

    try:
        background_tasks.add_task(
            send_email,
            data.email,
            "Your OTP Code for Verification",
            otp,
            rollback_on_fail=True
        )
        return {"message": "OTP sent successfully"}
    except EmailSendException:
        raise HTTPException(
            status_code=500, detail="Failed to send OTP email. Please try again."
        )


@router.post(
    "/verify-otp",
    summary="Verify OTP",
    description="""
Verify the OTP sent to the user's email.

- Returns success if OTP matches.
- Deletes OTP after successful verification.

Returns:
- Error if OTP is invalid or expired.
"""
)
async def verify_otp(data: OTPVerifyRequest):
    stored_otp = await get_otp(data.email)
    if not stored_otp:
        return {"error": "OTP expired or invalid"}
    if stored_otp != data.otp:
        return {"error": "Incorrect OTP"}
    await delete_otp(data.email)
    return {"message": "OTP verified successfully"}


@router.post(
    "/reset-password",
    summary="Reset password",
    description="""
Reset the password for the authenticated user.

- Verifies the old password.
- Checks that the new password is not the same as old.
- Updates password in the database.

Raises:
- 401 Unauthorized: if old password is incorrect.
- 400 Bad Request: if new password is same as old password.
- 404 Not Found: if user does not exist.
- 500 Internal Server Error: if reset fails.
"""
)
async def reset_password(data: ResetPasswordRequest, user=Depends(get_current_user)):
    db_user = await get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not await verify_password(data.old_password, db_user.hashedpassword):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as old password"
        )

    result = await reset_password_service(
        db_user.userid, data.email, data.old_password, data.new_password
    )

    if "error" in result:
        if result["error"] == "User not found":
            raise HTTPException(status_code=404, detail=result["error"])
        if result["error"] == "No fields provided for update":
            raise HTTPException(status_code=400, detail=result["error"])
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post(
    "/forgot-password",
    summary="Forgot password / send OTP",
    description="""
Initiate password reset by sending an OTP to the user's email.

- Generates OTP and stores in Redis.
- Sends email asynchronously.

Raises:
- 404 Not Found: if user does not exist.
- 500 Internal Server Error: if OTP cannot be stored or email sending fails.
"""
)
async def forgot_password(data: EmailRequest, background_tasks: BackgroundTasks):
    db_user = await get_user_by_email(data.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    result = await set_otp(data.email, otp, settings.OTP_EXPIRY)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to store OTP. Try again.")

    try:
        background_tasks.add_task(
            send_email,
            data.email,
            "Password Reset OTP",
            otp,
            rollback_on_fail=True
        )
        return {"message": "Password reset OTP sent successfully"}
    except EmailSendException:
        raise HTTPException(
            status_code=500, detail="Failed to send OTP email. Please try again."
        )


@router.post(
    "/set-new-password",
    summary="Set a new password",
    description="""
Set a new password for the user after OTP verification.

- Validates the user exists.
- Updates the password in the database.

Raises:
- 404 Not Found: if user does not exist.
- 500 Internal Server Error: if updating password fails.
"""
)
async def set_new_password(data: SetNewPasswordRequest):
    db_user = await get_user_by_email(data.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await new_password_service(data.email, data.newpassword)
    if isinstance(result, dict) and 'error' in result:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to set new password: {result['error']}"
        )

    return {"success": "Password has been changed."}
