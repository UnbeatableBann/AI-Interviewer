import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.repositories import TenantIsolatedRepository
from src.contexts.intelligence.models import (
    Skill,
    CandidateProfile,
    CandidateSkill,
    Strength,
    Weakness,
    ProgressSnapshot,
    InterviewInsight,
)


class SkillRepository:
    """Async database operations for global Skill taxonomy dictionary."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, skill_id: uuid.UUID) -> Optional[Skill]:
        stmt = select(Skill).where(Skill.id == skill_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Skill]:
        stmt = select(Skill).where(Skill.name == name)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_all(self) -> List[Skill]:
        stmt = select(Skill).order_by(Skill.name.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, skill: Skill) -> Skill:
        self.db.add(skill)
        await self.db.flush()
        return skill


class CandidateProfileRepository(TenantIsolatedRepository[CandidateProfile]):
    """Tenant-isolated database operations for CandidateProfile entities."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, CandidateProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[CandidateProfile]:
        """Retrieves candidate profile linked to a specific user ID."""
        stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_profile_with_relations(
        self, candidate_id: uuid.UUID
    ) -> Optional[CandidateProfile]:
        """Loads candidate profile with all child matrices pre-fetched using selectinload."""
        stmt = (
            select(CandidateProfile)
            .where(CandidateProfile.id == candidate_id)
            .options(
                selectinload(CandidateProfile.skills).selectinload(
                    CandidateSkill.skill
                ),
                selectinload(CandidateProfile.strengths),
                selectinload(CandidateProfile.weaknesses),
                selectinload(CandidateProfile.progress_snapshots),
                selectinload(CandidateProfile.insights),
            )
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()


class CandidateSkillRepository(TenantIsolatedRepository[CandidateSkill]):
    """Tenant-isolated database operations for CandidateSkill associative scores."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, CandidateSkill)

    async def get_by_candidate_and_skill(
        self, candidate_id: uuid.UUID, skill_id: uuid.UUID
    ) -> Optional[CandidateSkill]:
        """Retrieves candidate level record for a specific skill."""
        stmt = (
            select(CandidateSkill)
            .where(CandidateSkill.candidate_id == candidate_id)
            .where(CandidateSkill.skill_id == skill_id)
            .options(selectinload(CandidateSkill.skill))
        )
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()


class StrengthRepository(TenantIsolatedRepository[Strength]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Strength)


class WeaknessRepository(TenantIsolatedRepository[Weakness]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Weakness)


class ProgressSnapshotRepository(TenantIsolatedRepository[ProgressSnapshot]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ProgressSnapshot)


class InterviewInsightRepository(TenantIsolatedRepository[InterviewInsight]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, InterviewInsight)
