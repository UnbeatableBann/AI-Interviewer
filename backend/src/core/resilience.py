import asyncio
import time
from enum import Enum
import functools
import json
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, Type, TypeVar
from src.core.observability.logging import get_logger

logger = get_logger("src.core.resilience")

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF-OPEN"


class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is open and failing fast."""

    pass


class CircuitBreaker:
    """Thread-safe stateful circuit breaker for async downstream dependencies."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_successes: int = 2,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_successes = half_open_max_successes

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()

    def _transition_to(self, new_state: CircuitState) -> None:
        logger.info(
            "Circuit breaker state transition",
            name=self.name,
            old_state=self.state.value,
            new_state=new_state.value,
        )
        self.state = new_state
        self.last_state_change = time.time()
        self.failure_count = 0
        self.success_count = 0

    def record_success(self) -> None:
        """Called when a downstream operation completes successfully."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_successes:
                self._transition_to(CircuitState.CLOSED)
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Called when a downstream operation encounters an error."""
        if self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)
        elif self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)

    def check_state(self) -> None:
        """Evaluates whether operations can proceed, transitioning OPEN -> HALF_OPEN if elapsed."""
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_state_change
            if elapsed >= self.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN. Failing fast. Cooldown remaining: {self.recovery_timeout - elapsed:.1f}s"
                )

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Wraps async execution inside the circuit breaker state checks."""
        self.check_state()
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise


# Registry for caching circuit breakers across the platform
_breaker_registry: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, **kwargs: Any) -> CircuitBreaker:
    """Returns a circuit breaker singleton for a specific named dependency."""
    if name not in _breaker_registry:
        _breaker_registry[name] = CircuitBreaker(name, **kwargs)
    return _breaker_registry[name]


async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    timeout_sec: Optional[float] = 10.0,
    **kwargs: Any,
) -> Any:
    """Runs async function with an optional execution timeout and exponential retry backoff."""
    current_delay = initial_delay
    for attempt in range(1, retries + 1):
        try:
            if timeout_sec is not None:
                # Wrap with asyncio.wait_for to enforce timeouts
                return await asyncio.wait_for(
                    func(*args, **kwargs), timeout=timeout_sec
                )
            else:
                return await func(*args, **kwargs)
        except (asyncio.TimeoutError, *exceptions) as exc:
            logger.warning(
                "Resilience attempt failed",
                func=func.__name__,
                attempt=attempt,
                retries=retries,
                error=str(exc),
                next_delay_sec=current_delay if attempt < retries else 0,
            )
            if attempt == retries:
                raise exc
            await asyncio.sleep(current_delay)
            current_delay *= backoff_factor


def redis_cache(ttl_seconds: int = 300, key_prefix: str = "cache"):
    """Decorator to cache asynchronous function results in Redis."""

    def decorator(
        func: Callable[..., Awaitable[Any]],
    ) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from src.infrastructure.redis.client import get_redis_client

            # Generate cache key based on function name and serializable arguments
            serializable_args = []
            for arg in args:
                # Exclude database sessions, service classes, and complex entities
                from sqlalchemy.ext.asyncio import AsyncSession

                if isinstance(arg, AsyncSession):
                    continue
                if hasattr(arg, "db") or hasattr(arg, "session_repo"):
                    continue
                serializable_args.append(arg)

            serializable_kwargs = {}
            for k, v in kwargs.items():
                from sqlalchemy.ext.asyncio import AsyncSession

                if isinstance(v, AsyncSession):
                    continue
                serializable_kwargs[k] = v

            arg_str = f"{serializable_args}:{sorted(serializable_kwargs.items())}"
            cache_key = (
                f"{key_prefix}:{func.__module__}.{func.__name__}:{hash(arg_str)}"
            )

            client = get_redis_client()
            try:
                try:
                    cached_val = await client.get(cache_key)
                    if cached_val:
                        logger.debug("Cache hit", key=cache_key)
                        return json.loads(cached_val)
                except Exception as e:
                    logger.warning("Failed to read from cache", error=str(e))

                result = await func(*args, **kwargs)

                try:
                    # Serialize result to JSON and set in Redis
                    await client.setex(cache_key, ttl_seconds, json.dumps(result))
                except Exception as e:
                    logger.warning("Failed to write to cache", error=str(e))

                return result
            finally:
                await client.aclose()

        return wrapper

    return decorator
