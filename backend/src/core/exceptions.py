class IIPException(Exception):
    """Base exception class for all Interviewer Intelligence Platform exceptions."""

    def __init__(
        self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class EntityNotFoundError(IIPException):
    """Exception raised when a requested resource/entity is not found in database."""

    def __init__(
        self, message: str = "Resource not found", code: str = "NOT_FOUND"
    ) -> None:
        super().__init__(message, code=code, status_code=404)


class AuthenticationError(IIPException):
    """Exception raised when identity verification fails."""

    def __init__(
        self,
        message: str = "Could not authenticate credentials",
        code: str = "UNAUTHENTICATED",
    ) -> None:
        super().__init__(message, code=code, status_code=401)


class AuthorizationError(IIPException):
    """Exception raised when user does not possess required scopes or permissions."""

    def __init__(
        self,
        message: str = "Not authorized to perform this operation",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(message, code=code, status_code=403)


class TenantIsolationError(IIPException):
    """Exception raised when a cross-tenant data isolation boundary violation is caught."""

    def __init__(
        self,
        message: str = "Tenant access boundary violation",
        code: str = "TENANT_VIOLATION",
    ) -> None:
        super().__init__(message, code=code, status_code=403)


class BusinessRuleValidationError(IIPException):
    """Exception raised when state change logic violates domain rules."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code=code, status_code=400)
