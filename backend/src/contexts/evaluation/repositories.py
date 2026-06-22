import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.repositories import TenantIsolatedRepository
from src.contexts.evaluation.models import EvaluationReport, SkillGapReport


class EvaluationReportRepository(TenantIsolatedRepository[EvaluationReport]):
    """Tenant-isolated database repository for EvaluationReport."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, EvaluationReport)

    async def get_by_session_id(
        self, session_id: uuid.UUID
    ) -> Optional[EvaluationReport]:
        """Loads evaluation report for a specific interview session."""
        stmt = select(EvaluationReport).where(EvaluationReport.session_id == session_id)
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()


class SkillGapReportRepository(TenantIsolatedRepository[SkillGapReport]):
    """Tenant-isolated database repository for SkillGapReport."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, SkillGapReport)

    async def get_by_candidate_id(
        self, candidate_id: uuid.UUID
    ) -> List[SkillGapReport]:
        """Loads all skill gaps associated with candidate, pre-fetching Skill details."""
        stmt = (
            select(SkillGapReport)
            .where(SkillGapReport.candidate_id == candidate_id)
            .options(selectinload(SkillGapReport.skill))
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
