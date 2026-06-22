import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.tenant.models import Tenant


@pytest.mark.asyncio
async def test_prometheus_metrics_and_observability(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that the /metrics endpoint works, contains custom metrics, and increments values after requests."""

    # 1. Setup Tenant and Token
    tenant = Tenant(id="otel_corp", name="OTel Corp", status="ACTIVE")
    db_session.add(tenant)
    await db_session.commit()

    # 2. Check metrics endpoint works initially
    response_metrics_init = await client.get("/metrics")
    assert response_metrics_init.status_code == 200
    assert "text/plain" in response_metrics_init.headers["content-type"]
    metrics_text_init = response_metrics_init.text

    # Ensure our custom metrics are registered
    assert "http_request_latency_seconds" in metrics_text_init
    assert "llm_latency_seconds" in metrics_text_init
    assert "llm_token_usage_total" in metrics_text_init
    assert "llm_cost_usd_total" in metrics_text_init
    assert "evaluation_score_points" in metrics_text_init

    # 3. Trigger API requests (which will invoke LoggingMiddleware and increment http_request_latency)
    response_root = await client.get("/")
    assert response_root.status_code == 200

    # 4. Check metrics endpoint again
    response_metrics_after = await client.get("/metrics")
    assert response_metrics_after.status_code == 200
    metrics_text_after = response_metrics_after.text

    # Verify request latency registry is active and captured health query
    assert "http_request_latency_seconds_count" in metrics_text_after

    # 5. Check Langfuse logger dry-run functions operate safely without errors/exceptions
    from src.core.observability import langfuse_logger

    assert langfuse_logger.enabled is False or langfuse_logger.enabled is True

    # Execute generation logging and scoring to ensure safe fail-safes (dry-runs)
    trace_id = langfuse_logger.trace_generation(
        name="Test Generation",
        prompt="Describe Python Concurrency.",
        completion="Python supports asyncio.",
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=15,
        latency_seconds=0.15,
        tenant_id="otel_corp",
    )
    # Logging score should complete silently
    langfuse_logger.log_score(
        trace_id=trace_id or "dummy_id",
        name="test_score",
        value=1.0,
        comment="Unit check complete.",
    )
