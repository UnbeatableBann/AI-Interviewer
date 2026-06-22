import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.enums import UserRole
from src.contexts.tenant.models import Tenant
from src.contexts.auth.models import User


@pytest.mark.asyncio
async def test_candidate_self_registration_flow(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that candidates can register and must verify their email before login."""
    # Seed active tenant slug
    tenant = Tenant(id="test_tenant", name="Test Tenant", status="ACTIVE")
    db_session.add(tenant)
    await db_session.commit()

    # 1. Register candidate
    reg_payload = {
        "email": "candidate@example.com",
        "password": "securepassword123",
        "role": "CANDIDATE",
        "tenant_id": "test_tenant",
    }

    headers = {"X-Tenant-ID": "test_tenant"}
    response = await client.post(
        "/api/v1/auth/register", json=reg_payload, headers=headers
    )
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "candidate@example.com"
    assert body["data"]["role"] == "CANDIDATE"
    assert body["data"]["is_verified"] is False

    # Get verification token from DB
    stmt = select(User).where(User.email == "candidate@example.com")
    res = await db_session.execute(stmt)
    user = res.scalars().first()
    assert user is not None
    assert user.verification_token is not None

    # 2. Login fails before email is verified
    login_payload = {
        "email": "candidate@example.com",
        "password": "securepassword123",
    }
    login_response = await client.post(
        "/api/v1/auth/login", json=login_payload, headers=headers
    )
    assert login_response.status_code == 401
    assert "verify your email" in login_response.json()["error"]["message"]

    # 3. Verify Email
    verify_payload = {"token": user.verification_token}
    verify_response = await client.post(
        "/api/v1/auth/verify-email", json=verify_payload, headers=headers
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["data"] is True

    # 4. Login succeeds after verification
    login_response = await client.post(
        "/api/v1/auth/login", json=login_payload, headers=headers
    )
    assert login_response.status_code == 200
    tokens = login_response.json()["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_admin_registration_block(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that users cannot self-register directly as Admin."""
    tenant = Tenant(id="test_tenant", name="Test Tenant", status="ACTIVE")
    db_session.add(tenant)
    await db_session.commit()

    admin_payload = {
        "email": "admin@example.com",
        "password": "securepassword123",
        "role": "ADMIN",
        "tenant_id": "test_tenant",
    }

    headers = {"X-Tenant-ID": "test_tenant"}
    response = await client.post(
        "/api/v1/auth/register", json=admin_payload, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_token_rotation_and_replay_detection(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies refresh token rotation (DAS/Replay protection) works correctly."""
    # Seed active tenant slug
    tenant = Tenant(id="test_tenant", name="Test Tenant", status="ACTIVE")
    db_session.add(tenant)

    # 1. Setup verified user
    from src.core.security import get_password_hash

    hashed = get_password_hash("password123")
    user = User(
        tenant_id="test_tenant",
        email="recruiter@example.com",
        hashed_password=hashed,
        role=UserRole.RECRUITER,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"X-Tenant-ID": "test_tenant"}
    login_payload = {
        "email": "recruiter@example.com",
        "password": "password123",
    }

    # 2. Login to get refresh token
    login_res = await client.post(
        "/api/v1/auth/login", json=login_payload, headers=headers
    )
    assert login_res.status_code == 200
    original_refresh = login_res.json()["data"]["refresh_token"]

    # 3. Rotate tokens
    rotate_res1 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
        headers=headers,
    )
    assert rotate_res1.status_code == 200
    new_refresh = rotate_res1.json()["data"]["refresh_token"]
    assert new_refresh != original_refresh

    # 4. Replay Attack Detection: Attempt to use the original refresh token again
    replay_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
        headers=headers,
    )
    assert replay_res.status_code == 401
    assert "TOKEN_REPLAY" in replay_res.json()["error"]["code"]


@pytest.mark.asyncio
async def test_brute_force_lockout(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that 5 failed login attempts triggers account lockout."""
    # Seed active tenant slug
    tenant = Tenant(id="test_tenant", name="Test Tenant", status="ACTIVE")
    db_session.add(tenant)

    # Setup verified user
    from src.core.security import get_password_hash

    hashed = get_password_hash("password123")
    user = User(
        tenant_id="test_tenant",
        email="locked@example.com",
        hashed_password=hashed,
        role=UserRole.CANDIDATE,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"X-Tenant-ID": "test_tenant"}
    bad_login_payload = {
        "email": "locked@example.com",
        "password": "wrongpassword",
    }

    # Execute 5 failed logins
    for i in range(5):
        response = await client.post(
            "/api/v1/auth/login", json=bad_login_payload, headers=headers
        )
        assert response.status_code == 401

    # The 6th login should be locked out even if it uses correct credentials
    good_login_payload = {
        "email": "locked@example.com",
        "password": "password123",
    }
    lockout_res = await client.post(
        "/api/v1/auth/login", json=good_login_payload, headers=headers
    )
    assert lockout_res.status_code == 401
    assert "ACCOUNT_LOCKED" in lockout_res.json()["error"]["code"]
