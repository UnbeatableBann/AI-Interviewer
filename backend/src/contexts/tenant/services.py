from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import EntityNotFoundError, BusinessRuleValidationError
from src.contexts.tenant.models import Tenant
from src.contexts.tenant.repositories import TenantRepository
from src.contexts.tenant.schemas import TenantCreate
from src.contexts.audit.services import AuditLogService


class TenantService:
    """Manages Tenant onboarding, billing tiers, and runtime lifecycle states."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = TenantRepository(db)
        self.audit_service = AuditLogService(db)

    async def create_tenant(self, schema: TenantCreate) -> Tenant:
        """Provisions a new tenant namespace namespace, validating slug uniqueness."""
        existing = await self.repo.get_by_id(schema.id)
        if existing:
            raise BusinessRuleValidationError(
                f"Tenant ID slug '{schema.id}' is already registered.",
                code="TENANT_SLUG_DUPLICATE",
            )

        new_tenant = Tenant(
            id=schema.id,
            name=schema.name,
            tier=schema.tier.upper(),
            status="ACTIVE",
        )
        tenant = await self.repo.create(new_tenant)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=tenant.id,
            action="TENANT_PROVISION",
            resource_type="tenant",
            resource_id=tenant.id,
            details={"name": schema.name, "tier": tenant.tier},
        )
        return tenant

    async def get_tenant(self, tenant_id: str) -> Tenant:
        """Retrieves tenant details, throwing EntityNotFoundError if missing."""
        tenant = await self.repo.get_by_id(tenant_id)
        if not tenant:
            raise EntityNotFoundError(
                f"Tenant '{tenant_id}' does not exist.",
                code="TENANT_NOT_FOUND",
            )
        return tenant

    async def suspend_tenant(self, tenant_id: str) -> Tenant:
        """Suspends tenant access, rendering all child restricted endpoints inaccessible."""
        tenant = await self.get_tenant(tenant_id)
        tenant.status = "SUSPENDED"
        await self.repo.update(tenant)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=tenant.id,
            action="TENANT_SUSPEND",
            resource_type="tenant",
            resource_id=tenant.id,
        )
        return tenant

    async def activate_tenant(self, tenant_id: str) -> Tenant:
        """Restores suspended tenant access."""
        tenant = await self.get_tenant(tenant_id)
        tenant.status = "ACTIVE"
        await self.repo.update(tenant)
        await self.db.commit()

        await self.audit_service.log_action(
            tenant_id=tenant.id,
            action="TENANT_ACTIVATE",
            resource_type="tenant",
            resource_id=tenant.id,
        )
        return tenant
