from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.db import get_db
from src.api.dependencies.auth import ScopeChecker, CurrentUser, get_current_user
from src.contexts.tenant.schemas import TenantCreate, TenantResponse
from src.contexts.tenant.services import TenantService
from src.shared.schemas.responses import APIResponse

router = APIRouter(prefix="/tenants", tags=["tenants"])

# Scope checker dependencies
admin_scope = ScopeChecker(required_scopes=["system:admin"])


async def get_tenant_service(db: AsyncSession = Depends(get_db)) -> TenantService:
    return TenantService(db)


@router.post("", response_model=APIResponse[TenantResponse], status_code=201)
async def provision_tenant(
    payload: TenantCreate,
    current_user: CurrentUser = Depends(admin_scope),
    service: TenantService = Depends(get_tenant_service),
) -> APIResponse[TenantResponse]:
    """Provisions a new tenant database namespace mapping (Platform Admin scope)."""
    tenant = await service.create_tenant(payload)
    return APIResponse(
        success=True,
        data=TenantResponse.model_validate(tenant),
    )


@router.get("/{id}", response_model=APIResponse[TenantResponse])
async def get_tenant(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: TenantService = Depends(get_tenant_service),
) -> APIResponse[TenantResponse]:
    """Retrieves metadata properties for a specific tenant namespace."""
    # Ensure current user can only read their own tenant metadata unless system admin
    if "system:admin" not in current_user.scopes and current_user.tenant_id != id:
        from src.core.exceptions import TenantIsolationError

        raise TenantIsolationError("Access Denied: Cannot read other tenant profiles.")

    tenant = await service.get_tenant(id)
    return APIResponse(
        success=True,
        data=TenantResponse.model_validate(tenant),
    )


@router.post("/{id}/suspend", response_model=APIResponse[TenantResponse])
async def suspend_tenant(
    id: str,
    current_user: CurrentUser = Depends(admin_scope),
    service: TenantService = Depends(get_tenant_service),
) -> APIResponse[TenantResponse]:
    """Suspends the target tenant account (Platform Admin scope)."""
    tenant = await service.suspend_tenant(id)
    return APIResponse(
        success=True,
        data=TenantResponse.model_validate(tenant),
    )


@router.post("/{id}/activate", response_model=APIResponse[TenantResponse])
async def activate_tenant(
    id: str,
    current_user: CurrentUser = Depends(admin_scope),
    service: TenantService = Depends(get_tenant_service),
) -> APIResponse[TenantResponse]:
    """Re-activates a suspended tenant account (Platform Admin scope)."""
    tenant = await service.activate_tenant(id)
    return APIResponse(
        success=True,
        data=TenantResponse.model_validate(tenant),
    )
