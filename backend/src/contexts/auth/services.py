import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import AuthenticationError, BusinessRuleValidationError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from src.contexts.auth.models import User, RefreshToken, Session
from src.contexts.auth.repositories import (
    UserRepository,
    RefreshTokenRepository,
    SessionRepository,
)
from src.contexts.auth.schemas import UserRegister, UserLogin, TokenResponse
from src.contexts.audit.services import AuditLogService


class BruteForceProtectionService:
    """Tracks failed authentication cycles and locks compromised logins temporarily."""

    @staticmethod
    def check_lockout(user: User) -> None:
        """Asserts that user is not locked out by ongoing verification cooling windows."""
        if user.lockout_until:
            # Force timezone awareness for comparison
            now = datetime.now(timezone.utc)
            lockout_time = (
                user.lockout_until.replace(tzinfo=timezone.utc)
                if user.lockout_until.tzinfo is None
                else user.lockout_until
            )

            if now < lockout_time:
                minutes_remaining = int((lockout_time - now).total_seconds() / 60) + 1
                raise AuthenticationError(
                    f"Account is temporarily locked due to excessive failed attempts. Try again in {minutes_remaining} minutes.",
                    code="ACCOUNT_LOCKED",
                )

    @staticmethod
    def handle_failed_login(user: User) -> None:
        """Increments login failure counts, triggering 15-minute lockouts upon 5 failures."""
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            user.login_attempts = 0  # Reset counter for next cycle

    @staticmethod
    def handle_successful_login(user: User) -> None:
        """Resets failed verification metrics upon valid token release."""
        user.login_attempts = 0
        user.lockout_until = None


class AuthService:
    """Manages credentials verify loops, verification requests, and account updates."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
        self.session_repo = SessionRepository(db)
        self.audit_service = AuditLogService(db)
        self.brute_force = BruteForceProtectionService()

    async def register_user(self, schema: UserRegister) -> User:
        """Registers a user profile mapping to standard roles (Candidate / Recruiter)."""
        existing = await self.user_repo.get_by_email(schema.email)
        if existing:
            raise BusinessRuleValidationError(
                "An account with this email address already exists.",
                code="EMAIL_ALREADY_EXISTS",
            )

        hashed = get_password_hash(schema.password)
        verification_token = str(uuid.uuid4())

        new_user = User(
            tenant_id=schema.tenant_id,
            email=schema.email,
            hashed_password=hashed,
            role=schema.role,
            is_active=True,
            is_verified=False,
            verification_token=verification_token,
        )

        user = await self.user_repo.create(new_user)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=schema.tenant_id,
            user_id=user.id,
            action="USER_REGISTER",
            resource_type="user",
            resource_id=str(user.id),
            details={"email": schema.email, "role": schema.role.value},
        )

        return user

    async def login_user(
        self,
        credentials: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticates user credentials, validating brute-force bounds and active states."""
        user = await self.user_repo.get_by_email(credentials.email)
        if not user:
            raise AuthenticationError("Invalid login credentials provided.")

        self.brute_force.check_lockout(user)

        if not verify_password(credentials.password, user.hashed_password):
            self.brute_force.handle_failed_login(user)
            await self.user_repo.update(user)

            await self.audit_service.log_action(
                tenant_id=user.tenant_id,
                user_id=user.id,
                action="LOGIN_FAILURE",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise AuthenticationError("Invalid login credentials provided.")

        if not user.is_active:
            raise AuthenticationError("This user account has been deactivated.")

        if not user.is_verified:
            raise AuthenticationError(
                "Please verify your email address before logging in.",
                code="EMAIL_UNVERIFIED",
            )

        self.brute_force.handle_successful_login(user)
        await self.user_repo.update(user)

        # Generate access and refresh tokens
        scopes = [f"role:{user.role.value.lower()}"]
        if user.role.value == "ADMIN":
            scopes.extend(["system:admin", "tenant:admin"])
        elif user.role.value == "RECRUITER":
            scopes.extend(["recruiter:write", "recruiter:read"])
        elif user.role.value == "CANDIDATE":
            # Candidates get specific scope constraints during adaptive execution
            scopes.extend(["candidate:session"])

        access = create_access_token(user.id, user.tenant_id, scopes)
        refresh = create_refresh_token(user.id, user.tenant_id)

        # Parse refresh payload to register expiration dates
        payload = decode_token(refresh)
        exp_timestamp = payload.get("exp")
        expires_at = (
            datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_timestamp
            else datetime.now(timezone.utc) + timedelta(days=7)
        )

        # Record RefreshToken entity mapping in PostgreSQL database
        import hashlib

        token_hash = hashlib.sha256(refresh.encode("utf-8")).hexdigest()
        refresh_entity = RefreshToken(
            tenant_id=user.tenant_id,
            user_id=user.id,
            token=token_hash,
            expires_at=expires_at,
        )

        await self.token_repo.create(refresh_entity)

        # Record login Session entity (JWT id tracking)
        jti = str(uuid.uuid4())
        session_entity = Session(
            tenant_id=user.tenant_id,
            user_id=user.id,
            token_id=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        await self.session_repo.create(session_entity)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"session_id": str(session_entity.id)},
        )

        return TokenResponse(access_token=access, refresh_token=refresh)

    async def verify_email(self, token: str) -> bool:
        """Confirms candidate or recruiter verification tokens mapping statuses."""
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            raise BusinessRuleValidationError(
                "Invalid or expired verification token.",
                code="INVALID_VERIFICATION_TOKEN",
            )

        user.is_verified = True
        user.verification_token = None
        await self.user_repo.update(user)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="EMAIL_VERIFIED",
            resource_type="user",
            resource_id=str(user.id),
        )
        return True

    async def request_password_reset(self, email: str) -> None:
        """Sets password reset tokens mapping expiries on matched email profiles."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Silence user existence check for security to prevent brute username enumerations
            return

        reset_token = str(uuid.uuid4())
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.user_repo.update(user)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="PASSWORD_RESET_REQUESTED",
            resource_type="user",
            resource_id=str(user.id),
        )

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Applies updated password details checking token validity windows."""
        user = await self.user_repo.get_by_reset_token(token)
        if not user:
            raise BusinessRuleValidationError(
                "Invalid password reset token.", code="INVALID_RESET_TOKEN"
            )

        if user.password_reset_expires:
            # Force timezone awareness for comparison
            now = datetime.now(timezone.utc)
            expiry_time = (
                user.password_reset_expires.replace(tzinfo=timezone.utc)
                if user.password_reset_expires.tzinfo is None
                else user.password_reset_expires
            )

            if now > expiry_time:
                raise BusinessRuleValidationError(
                    "Password reset token has expired.", code="EXPIRED_RESET_TOKEN"
                )

        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None

        # Reset lockout counters to unlock user upon successful pass updates
        user.login_attempts = 0
        user.lockout_until = None

        await self.user_repo.update(user)

        # Force revoke active refresh tokens and sessions to end existing compromised sessions
        await self.token_repo.revoke_all_for_user(user.id)
        await self.session_repo.revoke_all_for_user(user.id)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="PASSWORD_RESET_CONFIRMED",
            resource_type="user",
            resource_id=str(user.id),
        )
        return True


class TokenRotationService:
    """Validates refresh cycles and re-signs credentials ensuring replay protections."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.token_repo = RefreshTokenRepository(db)
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.audit_service = AuditLogService(db)

    async def rotate_tokens(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Rotates a valid refresh token. Triggers replay breaches if token reuse occurs."""
        try:
            payload = decode_token(refresh_token)
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError(f"Invalid refresh token: {str(exc)}")

        user_id_str = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        token_type = payload.get("type")

        if not user_id_str or not tenant_id or token_type != "refresh":
            raise AuthenticationError("Invalid refresh token payload claims.")

        user_id = uuid.UUID(user_id_str)
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError(
                "User associated with token is inactive or not found."
            )

        # Replay Attack Detection: Verify the token hasn't been used yet.
        # We must look up the token. Since we hashed it in DB, we verify via verification context
        # Retrieve all active/revoked tokens for the user to verify matches
        # Note: A real-world production-grade design matches hash tokens efficiently
        # Since token hashes are saved, we check match loops:
        # Note: For performance, we search via token parent/hash references
        # Let's decode token signature or retrieve token lists
        # Let's look up using the hash of the token
        # (We hash it using pwd_context to protect DB, or standard sha256. We used bcrypt via get_password_hash.
        # Wait, bcrypt verification is slow but secure. Alternatively, a sha256 hash is indexing-friendly.
        # But since password hashing was used, we can verify matches.
        # To perform indexing-friendly lookups, using sha256 is usually preferred for tokens, but we can verify here.)
        # Let's see: how to lookup if it's hashed with bcrypt?
        # A simpler production way is: sha256 hash stored as token string, which is exact match indexable!
        # Let's modify: we'll search by standard string lookup in DB. To secure it, we'll store a sha256 hash of the token.
        # Let's implement a clean check.
        import hashlib

        token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()

        token_entity = await self.token_repo.get_by_token(token_hash)
        if not token_entity:
            # Fallback check (if bcrypt was used previously, or token is unrecognized)
            raise AuthenticationError("Refresh token is unrecognized or invalid.")

        # If token is already revoked, someone is trying to reuse an old refresh token!
        # This indicates a potential replay breach. Under security design rules, we revoke ALL user tokens.
        if token_entity.is_revoked:
            await self.token_repo.revoke_all_for_user(user_id)
            await self.session_repo.revoke_all_for_user(user_id)

            await self.audit_service.log_action(
                tenant_id=tenant_id,
                user_id=user_id,
                action="REFRESH_TOKEN_REPLAY_BREACH",
                resource_type="token",
                resource_id=str(token_entity.id),
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    "alert": "Breach detected: Refresh token reused. Active sessions terminated."
                },
            )
            raise AuthenticationError(
                "Compromised session. Full login validation required.",
                code="TOKEN_REPLAY",
            )

        # Check token expiration
        now = datetime.now(timezone.utc)
        expires_time = (
            token_entity.expires_at.replace(tzinfo=timezone.utc)
            if token_entity.expires_at.tzinfo is None
            else token_entity.expires_at
        )

        if now > expires_time:
            token_entity.is_revoked = True
            await self.token_repo.create(token_entity)
            raise AuthenticationError("Refresh token has expired.")

        # Mark token as revoked (used)
        token_entity.is_revoked = True
        await self.token_repo.create(token_entity)

        # Generate new Access and Refresh tokens
        scopes = [f"role:{user.role.value.lower()}"]
        if user.role.value == "ADMIN":
            scopes.extend(["system:admin", "tenant:admin"])
        elif user.role.value == "RECRUITER":
            scopes.extend(["recruiter:write", "recruiter:read"])
        elif user.role.value == "CANDIDATE":
            scopes.extend(["candidate:session"])

        new_access = create_access_token(user.id, tenant_id, scopes)
        new_refresh = create_refresh_token(user.id, tenant_id)

        # Save new token details
        new_payload = decode_token(new_refresh)
        new_exp_timestamp = new_payload.get("exp")
        new_expires_at = (
            datetime.fromtimestamp(new_exp_timestamp, tz=timezone.utc)
            if new_exp_timestamp
            else datetime.now(timezone.utc) + timedelta(days=7)
        )

        new_token_hash = hashlib.sha256(new_refresh.encode("utf-8")).hexdigest()
        new_token_entity = RefreshToken(
            tenant_id=tenant_id,
            user_id=user_id,
            token=new_token_hash,
            parent_token=token_hash,
            expires_at=new_expires_at,
        )
        await self.token_repo.create(new_token_entity)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="TOKEN_ROTATION",
            resource_type="token",
            resource_id=str(new_token_entity.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
