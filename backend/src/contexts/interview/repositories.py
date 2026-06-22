import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.repositories import TenantIsolatedRepository
from src.contexts.interview.models import (
    InterviewSession,
    InterviewQuestion,
    InterviewResponse,
)


class InterviewSessionRepository(TenantIsolatedRepository[InterviewSession]):
    """Tenant-isolated repository for InterviewSession."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, InterviewSession)

    async def get_session_with_relations(
        self, session_id: uuid.UUID
    ) -> Optional[InterviewSession]:
        """Loads interview session pre-fetching questions and responses."""
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(
                selectinload(InterviewSession.questions),
                selectinload(InterviewSession.responses),
            )
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()


class InterviewQuestionRepository(TenantIsolatedRepository[InterviewQuestion]):
    """Tenant-isolated repository for InterviewQuestion."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, InterviewQuestion)

    async def get_by_session(self, session_id: uuid.UUID) -> List[InterviewQuestion]:
        """Retrieves all questions generated within a specific session ordered by sequence."""
        stmt = (
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.order.asc())
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class InterviewResponseRepository(TenantIsolatedRepository[InterviewResponse]):
    """Tenant-isolated repository for InterviewResponse."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, InterviewResponse)
