import asyncio
from typing import Any
import pytest
from unittest.mock import patch
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    retry_with_backoff,
)


# 1. Custom Mock Redis to mock rate limiting and idempotency actions
class MockRedisClient:
    def __init__(self) -> None:
        self.store = {}

    async def get(self, key: str) -> Any:
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)

    def pipeline(self, transaction: bool = True) -> Any:
        class MockPipeline:
            def __init__(self, outer: "MockRedisClient") -> None:
                self.outer = outer
                self.increments = []

            def incr(self, key: str) -> None:
                self.increments.append(key)

            def expire(self, key: str, ttl: int) -> None:
                pass

            async def __aenter__(self) -> "MockPipeline":
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                pass

            async def execute(self) -> list:
                results = []
                for k in self.increments:
                    val = int(self.outer.store.get(k, 0)) + 1
                    self.outer.store[k] = str(val)
                    results.append(val)
                return results

        return MockPipeline(self)

    async def aclose(self) -> None:
        pass


@pytest.mark.asyncio
async def test_resilience_circuit_breaker() -> None:
    """Verifies circuit breaker state transitions (CLOSED -> OPEN -> HALF-OPEN -> CLOSED) and fail-fast."""
    breaker = CircuitBreaker(
        "test_breaker",
        failure_threshold=2,
        recovery_timeout=0.1,
        half_open_max_successes=2,
    )

    assert breaker.state.value == "CLOSED"

    # Step 1: Trigger failures to trip the breaker
    async def failing_call():
        raise ValueError("Downstream failure")

    with pytest.raises(ValueError):
        await breaker.call(failing_call)
    assert breaker.state.value == "CLOSED"

    with pytest.raises(ValueError):
        await breaker.call(failing_call)
    # Tripped after 2 failures
    assert breaker.state.value == "OPEN"

    # Subsequent calls fail fast
    with pytest.raises(CircuitBreakerOpenException):
        await breaker.call(failing_call)

    # Step 2: Cooldown recovery timeout
    await asyncio.sleep(0.15)

    # Calling now transitions to HALF-OPEN
    success_called = 0

    async def success_call():
        nonlocal success_called
        success_called += 1
        return "success"

    # First call in HALF-OPEN
    res1 = await breaker.call(success_call)
    assert res1 == "success"
    assert breaker.state.value == "HALF-OPEN"

    # Second call in HALF-OPEN (crosses half_open_max_successes = 2)
    res2 = await breaker.call(success_call)
    assert res2 == "success"
    assert breaker.state.value == "CLOSED"
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_resilience_retries_and_timeout() -> None:
    """Verifies backoff retries and execution timeouts function correctly."""
    call_attempts = 0

    async def transient_error_call():
        nonlocal call_attempts
        call_attempts += 1
        if call_attempts < 3:
            raise ConnectionError("Transient network glitch")
        return "completed"

    res = await retry_with_backoff(
        transient_error_call,
        retries=3,
        initial_delay=0.01,
        backoff_factor=1.5,
        exceptions=(ConnectionError,),
    )
    assert res == "completed"
    assert call_attempts == 3

    # Test timeout execution
    async def slow_call():
        await asyncio.sleep(0.5)
        return "done"

    with pytest.raises(asyncio.TimeoutError):
        await retry_with_backoff(
            slow_call,
            retries=1,
            timeout_sec=0.05,
        )


@pytest.mark.asyncio
async def test_security_headers_middleware(client: AsyncClient) -> None:
    """Verifies that browser hardening security headers are appended to responses."""
    # Hit the root endpoint
    response = await client.get("/")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "frame-ancestors 'none'" in headers.get("Content-Security-Policy", "")
    assert "max-age=" in headers.get("Strict-Transport-Security", "")


@pytest.mark.asyncio
async def test_rate_limiting_middleware() -> None:
    """Verifies RateLimiterMiddleware rejects requests exceeding requests-per-minute thresholds."""
    from src.api.middleware.hardening import RateLimiterMiddleware

    test_app = FastAPI()
    test_app.add_middleware(RateLimiterMiddleware, ip_limit=2, tenant_limit=5)

    @test_app.get("/test")
    def route_endpoint():
        return {"status": "ok"}

    mock_redis = MockRedisClient()

    with patch(
        "src.api.middleware.hardening.get_redis_client", return_value=mock_redis
    ):
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            # Request 1 (OK)
            r1 = await ac.get("/test")
            assert r1.status_code == 200

            # Request 2 (OK)
            r2 = await ac.get("/test")
            assert r2.status_code == 200

            # Request 3 (Rate Limited - exceeding ip_limit=2)
            r3 = await ac.get("/test")
            assert r3.status_code == 429
            assert r3.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_idempotency_middleware() -> None:
    """Verifies IdempotencyMiddleware prevents parallel locks and serves cached responses for duplicate headers."""
    from src.api.middleware.hardening import IdempotencyMiddleware
    from httpx import ASGITransport

    test_app = FastAPI()
    test_app.add_middleware(IdempotencyMiddleware)

    payload_calls = 0

    @test_app.post("/submit")
    async def submit_item():
        nonlocal payload_calls
        payload_calls += 1
        await asyncio.sleep(0.05)
        return {"payload_calls": payload_calls, "status": "processed"}

    mock_redis = MockRedisClient()

    with patch(
        "src.api.middleware.hardening.get_redis_client", return_value=mock_redis
    ):
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            headers = {"Idempotency-Key": "unique-uuid-key", "X-Tenant-ID": "tenant_1"}

            # Call 1: Initiates processing
            r1_task = asyncio.create_task(ac.post("/submit", headers=headers))
            await asyncio.sleep(0.01)  # Wait slightly for Call 1 to acquire the lock

            # Call 2 (Conflict): Hits during processing
            r2 = await ac.post("/submit", headers=headers)
            assert r2.status_code == 409
            assert r2.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"

            # Await Call 1 completion
            r1 = await r1_task
            assert r1.status_code == 200
            assert r1.json()["payload_calls"] == 1

            # Call 3 (Cached HIT): Hits after processing, returns cached payload
            r3 = await ac.post("/submit", headers=headers)
            assert r3.status_code == 200
            assert r3.headers.get("X-Cache-Lookup") == "HIT (Idempotent)"
            assert r3.json()["payload_calls"] == 1
            assert payload_calls == 1  # Handler was executed exactly once


@pytest.mark.asyncio
async def test_redis_caching_decorator() -> None:
    """Verifies that the redis_cache decorator avoids repeated calculations for cached arguments."""
    from src.core.resilience import redis_cache

    compute_count = 0

    @redis_cache(ttl_seconds=10, key_prefix="test_cache")
    async def compute_heavy_square(x: int) -> dict:
        nonlocal compute_count
        compute_count += 1
        return {"result": x * x, "count": compute_count}

    mock_redis = MockRedisClient()

    with patch(
        "src.infrastructure.redis.client.get_redis_client", return_value=mock_redis
    ):
        # First execution (Cache Miss)
        res1 = await compute_heavy_square(10)
        assert res1 == {"result": 100, "count": 1}
        assert compute_count == 1

        # Second execution (Cache Hit)
        res2 = await compute_heavy_square(10)
        assert res2 == {"result": 100, "count": 1}  # Returns cached dict
        assert compute_count == 1  # Function body not executed again

        # Different argument execution (Cache Miss)
        res3 = await compute_heavy_square(5)
        assert res3 == {"result": 25, "count": 2}
        assert compute_count == 2

        # Test function exception propagation and connection closing
        from unittest.mock import AsyncMock

        @redis_cache(ttl_seconds=10, key_prefix="test_cache_fail")
        async def compute_and_fail(x: int) -> dict:
            raise RuntimeError("Computation failed!")

        # Create a spy on MockRedisClient.aclose
        aclose_mock = AsyncMock()
        mock_redis.aclose = aclose_mock

        with pytest.raises(RuntimeError) as exc_info:
            await compute_and_fail(10)
        assert "Computation failed!" in str(exc_info.value)
        # Verify aclose was called exactly once to prevent leaks
        aclose_mock.assert_called_once()
