import uuid
from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant
from src.core.exceptions import TenantIsolationError
from src.shared.utils.context import get_tenant_id

T = TypeVar("T")


class TenantRepository:
    """Async database operations for managing Tenant metadata."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Loads a tenant namespace mapping from PostgreSQL database."""
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, tenant: Tenant) -> Tenant:
        """Saves a new tenant registry record."""
        self.db.add(tenant)
        await self.db.flush()
        return tenant

    async def update(self, tenant: Tenant) -> Tenant:
        """Flushes updated tenant settings metadata."""
        self.db.add(tenant)
        await self.db.flush()
        return tenant


class TenantIsolatedRepository(Generic[T]):
    """Base repository subclass isolating database access to active context tenant slugs."""

    def __init__(self, db: AsyncSession, model_class: Type[T]) -> None:
        self.db = db
        self.model_class = model_class

    def _get_active_tenant_id(self) -> str:
        """Retrieves the request-bound tenant ID, throwing error if context is empty."""
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise TenantIsolationError(
                "Access Denied: No active tenant namespace is bound to this request context."
            )
        return tenant_id

    def _apply_tenant_filter(self, stmt: select) -> select:
        """Dynamically appends tenant_id boundary conditions to database statements."""
        # Ensure that target model class contains tenant_id attribute before filtering
        if not hasattr(self.model_class, "tenant_id"):
            raise TenantIsolationError(
                f"Configuration Error: Model '{self.model_class.__name__}' is missing tenant_id column."
            )
        return stmt.where(self.model_class.tenant_id == self._get_active_tenant_id())

    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[T]:
        """Loads a tenant-scoped record by ID, enforcing tenant boundaries."""
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_all(self, limit: int = 50, offset: int = 0) -> List[T]:
        """Returns lists of tenant-scoped records, bounded to the active tenant context."""
        stmt = select(self.model_class).limit(limit).offset(offset)
        stmt = self._apply_tenant_filter(stmt)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, entity: T) -> T:
        """Inserts a new record, automatically applying the active tenant slug."""
        active_tenant = self._get_active_tenant_id()

        # Guard clause: Ensure write entity tenant matches the active context
        entity_tenant = getattr(entity, "tenant_id", None)
        if entity_tenant and entity_tenant != active_tenant:
            raise TenantIsolationError(
                f"Security Breach Blocked: Cannot insert record for tenant '{entity_tenant}' inside context '{active_tenant}'."
            )

        # Automatically assign tenant id if empty to prevent developer oversight
        if not entity_tenant:
            setattr(entity, "tenant_id", active_tenant)

        self.db.add(entity)
        await self.db.flush()
        return entity
