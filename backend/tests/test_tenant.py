import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant
from src.core.security import create_access_token


@pytest.mark.asyncio
async def test_tenant_provision_and_lifecycle(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies tenant creation, details retrieval, and suspension workflow by platform admins."""
    # 1. Setup platform administrator authentication
    admin_token = create_access_token(
        subject="admin_id",
        tenant_id="system",
        scopes=["system:admin"],
    )
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Tenant-ID": "system",
    }

    # Register system tenant in DB first to satisfy middleware registration checks
    system_tenant = Tenant(id="system", name="System Tenant", status="ACTIVE")
    db_session.add(system_tenant)
    await db_session.commit()

    # 2. Provision new tenant slug 'acme-corp'
    payload = {
        "id": "acme-corp",
        "name": "Acme Corporation",
        "tier": "ENTERPRISE",
    }

    response = await client.post("/api/v1/tenants", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == "acme-corp"

    # Verify acme-corp exists in PostgreSQL
    stmt = select(Tenant).where(Tenant.id == "acme-corp")
    res = await db_session.execute(stmt)
    tenant = res.scalars().first()
    assert tenant is not None
    assert tenant.status == "ACTIVE"

    # 3. Retrieve tenant metadata
    get_response = await client.get("/api/v1/tenants/acme-corp", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "Acme Corporation"

    # 4. Suspend tenant
    susp_response = await client.post(
        "/api/v1/tenants/acme-corp/suspend", headers=headers
    )
    assert susp_response.status_code == 200
    assert susp_response.json()["data"]["status"] == "SUSPENDED"

    # Refresh DB session and verify status
    await db_session.refresh(tenant)
    assert tenant.status == "SUSPENDED"


@pytest.mark.asyncio
async def test_tenant_middleware_enforcement(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that the tenant middleware blocks unauthorized, suspended, or missing tenant headers."""
    # Setup standard tenants in DB
    t_active = Tenant(id="active-tenant", name="Active Tenant", status="ACTIVE")
    t_susp = Tenant(id="suspended-tenant", name="Suspended Tenant", status="SUSPENDED")
    db_session.add_all([t_active, t_susp])
    await db_session.commit()

    # Protected endpoint requires X-Tenant-ID
    # 1. Missing header request
    response_missing = await client.get("/api/v1/tenants/active-tenant")
    assert response_missing.status_code == 400
    assert (
        "X-Tenant-ID header is required" in response_missing.json()["error"]["message"]
    )

    # 2. Unregistered tenant header request
    headers_unreg = {"X-Tenant-ID": "fake-tenant"}
    response_unreg = await client.get(
        "/api/v1/tenants/fake-tenant", headers=headers_unreg
    )
    assert response_unreg.status_code == 404
    assert "is not registered" in response_unreg.json()["error"]["message"]

    # 3. Suspended tenant header request
    headers_susp = {"X-Tenant-ID": "suspended-tenant"}
    response_susp = await client.get(
        "/api/v1/tenants/suspended-tenant", headers=headers_susp
    )
    assert response_susp.status_code == 403
    assert "has been suspended" in response_susp.json()["error"]["message"]
