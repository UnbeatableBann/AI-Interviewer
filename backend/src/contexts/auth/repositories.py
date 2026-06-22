import uuid
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.auth.models import User, RefreshToken, Session


class UserRepository:
    """Async database operations for the User entity."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        stmt = select(User).where(User.verification_token == token)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_by_reset_token(self, token: str) -> Optional[User]:
        stmt = select(User).where(User.password_reset_token == token)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User) -> User:
        # State transitions are written locally on model and flushed to session
        self.db.add(user)
        await self.db.flush()
        return user


class RefreshTokenRepository:
    """Async database operations for managing RefreshTokens."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, token_entity: RefreshToken) -> RefreshToken:
        self.db.add(token_entity)
        await self.db.flush()
        return token_entity

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)

    async def revoke_chain(self, parent_token: str) -> None:
        """Revokes all tokens down a rotation hierarchy to mitigate replay attacks."""
        stmt = (
            update(RefreshToken)
            .where(
                (RefreshToken.parent_token == parent_token)
                | (RefreshToken.token == parent_token)
            )
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)


class SessionRepository:
    """Async database operations for Session lifecycle audits."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_token_id(self, token_id: str) -> Optional[Session]:
        stmt = select(Session).where(Session.token_id == token_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, session: Session) -> Session:
        self.db.add(session)
        await self.db.flush()
        return session

    async def revoke_by_token_id(self, token_id: str) -> None:
        stmt = (
            update(Session).where(Session.token_id == token_id).values(is_revoked=True)
        )
        await self.db.execute(stmt)

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = update(Session).where(Session.user_id == user_id).values(is_revoked=True)
        await self.db.execute(stmt)
