from contextvars import ContextVar
from typing import Optional

# Thread-safe context variables mapping current request session parameters
_current_tenant_id: ContextVar[Optional[str]] = ContextVar(
    "current_tenant_id", default=None
)
_current_user_id: ContextVar[Optional[str]] = ContextVar(
    "current_user_id", default=None
)


def set_tenant_id(tenant_id: Optional[str]) -> None:
    """Sets the current active tenant ID in context variables."""
    _current_tenant_id.set(tenant_id)


def get_tenant_id() -> Optional[str]:
    """Retrieves the current active tenant ID from context variables."""
    return _current_tenant_id.get()


def set_user_id(user_id: Optional[str]) -> None:
    """Sets the current active user ID in context variables."""
    _current_user_id.set(user_id)


def get_user_id() -> Optional[str]:
    """Retrieves the current active user ID from context variables."""
    return _current_user_id.get()


def clear_context() -> None:
    """Clears all variables inside the current request context."""
    _current_tenant_id.set(None)
    _current_user_id.set(None)
