from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.audit.models import AuditLog


class AuditLogRepository:
    """Async database operations for managing audit trail logs."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, audit_log: AuditLog) -> AuditLog:
        self.db.add(audit_log)
        await self.db.flush()
        return audit_log

    async def get_by_tenant(
        self, tenant_id: str, limit: int = 50, offset: int = 0
    ) -> List[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_by_tenant(self, tenant_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar() or 0
