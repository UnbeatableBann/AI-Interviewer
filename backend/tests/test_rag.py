import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant
from src.core.security import create_access_token


@pytest.mark.asyncio
async def test_rag_platform_lifecycle(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies RAG ingestion, hybrid retrieval, citation structure, and tenant isolation bounds."""

    # 1. Setup Tenants
    tenant_a = Tenant(id="tenant_alpha", name="Alpha Corporation", status="ACTIVE")
    tenant_b = Tenant(id="tenant_beta", name="Beta Corporation", status="ACTIVE")
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.commit()

    # 2. Setup Tokens and Headers
    token_a = create_access_token(
        subject="recruiter_alpha",
        tenant_id="tenant_alpha",
        scopes=["recruiter:write", "recruiter:read"],
    )
    headers_a = {
        "Authorization": f"Bearer {token_a}",
        "X-Tenant-ID": "tenant_alpha",
    }

    token_b = create_access_token(
        subject="recruiter_beta",
        tenant_id="tenant_beta",
        scopes=["recruiter:write", "recruiter:read"],
    )
    headers_b = {
        "Authorization": f"Bearer {token_b}",
        "X-Tenant-ID": "tenant_beta",
    }

    # 3. Ingest document for Tenant Alpha
    payload_alpha = {
        "title": "Alpha Python Playbook",
        "source_type": "INTERVIEW_PLAYBOOK",
        "content": (
            "This is the official interview playbook for Python engineering at Alpha. "
            "We always look for deep knowledge of memory management. "
            "Candidates must explain the differences between stack vs heap allocations. "
            "We also check for asyncio concurrency patterns."
        ),
        "metadata_json": {"department": "Engineering", "level": "L5"},
    }

    response_ingest_a = await client.post(
        "/api/v1/rag/documents",
        json=payload_alpha,
        headers=headers_a,
    )
    assert response_ingest_a.status_code == 201
    doc_a_data = response_ingest_a.json()["data"]
    assert doc_a_data["title"] == "Alpha Python Playbook"
    assert doc_a_data["tenant_id"] == "tenant_alpha"
    doc_a_id = doc_a_data["id"]

    # 4. Ingest document for Tenant Beta
    payload_beta = {
        "title": "Beta Go Playbook",
        "source_type": "INTERVIEW_PLAYBOOK",
        "content": (
            "This is the official interview playbook for Go engineering at Beta. "
            "We evaluate candidates on goroutine dynamics and channels. "
            "Candidates should design thread-safe connection pools. "
            "We focus heavily on lockless designs and mutex syncs."
        ),
        "metadata_json": {"department": "Platform Core", "level": "Senior"},
    }

    response_ingest_b = await client.post(
        "/api/v1/rag/documents",
        json=payload_beta,
        headers=headers_b,
    )
    assert response_ingest_b.status_code == 201
    doc_b_data = response_ingest_b.json()["data"]
    assert doc_b_data["title"] == "Beta Go Playbook"
    assert doc_b_data["tenant_id"] == "tenant_beta"
    doc_b_id = doc_b_data["id"]

    # 5. Verify tenant isolation in querying
    # Query Python (relates to Alpha) from Beta context -> Should return nothing!
    query_payload_beta = {
        "query": "Python memory management stack heap asyncio",
        "source_types": ["INTERVIEW_PLAYBOOK"],
        "limit": 5,
    }
    response_query_b_python = await client.post(
        "/api/v1/rag/query",
        json=query_payload_beta,
        headers=headers_b,
    )
    assert response_query_b_python.status_code == 200
    results_b_python = response_query_b_python.json()["data"]["results"]
    assert len(results_b_python) == 0  # No Alpha documents returned to Beta!

    # Query Python from Alpha context -> Should return the Alpha python chunks!
    query_payload_alpha = {
        "query": "Python memory management stack heap asyncio",
        "source_types": ["INTERVIEW_PLAYBOOK"],
        "limit": 5,
    }
    response_query_a_python = await client.post(
        "/api/v1/rag/query",
        json=query_payload_alpha,
        headers=headers_a,
    )
    assert response_query_a_python.status_code == 200
    results_a_python = response_query_a_python.json()["data"]["results"]
    assert len(results_a_python) > 0
    assert any(
        "Alpha Python Playbook" in r["citation"]["title"] for r in results_a_python
    )
    # Check citation structure and fields
    first_hit = results_a_python[0]
    assert first_hit["citation"]["document_id"] == doc_a_id
    assert first_hit["citation"]["source_type"] == "INTERVIEW_PLAYBOOK"
    assert "playbook" in first_hit["content"].lower()

    # Query Go (relates to Beta) from Beta context -> Should return Beta go chunks!
    query_payload_beta_go = {
        "query": "Go goroutine dynamics lockless mutex",
        "source_types": ["INTERVIEW_PLAYBOOK"],
        "limit": 5,
    }
    response_query_b_go = await client.post(
        "/api/v1/rag/query",
        json=query_payload_beta_go,
        headers=headers_b,
    )
    assert response_query_b_go.status_code == 200
    results_b_go = response_query_b_go.json()["data"]["results"]
    assert len(results_b_go) > 0
    assert results_b_go[0]["citation"]["document_id"] == doc_b_id

    # 6. Delete document for Tenant Alpha
    response_delete_a = await client.delete(
        f"/api/v1/rag/documents/{doc_a_id}",
        headers=headers_a,
    )
    assert response_delete_a.status_code == 200
    assert "successfully deleted" in response_delete_a.json()["data"]["message"]

    # Verify query on Alpha context now returns nothing
    response_query_a_after_delete = await client.post(
        "/api/v1/rag/query",
        json=query_payload_alpha,
        headers=headers_a,
    )
    assert response_query_a_after_delete.status_code == 200
    results_a_after_delete = response_query_a_after_delete.json()["data"]["results"]
    assert len(results_a_after_delete) == 0
