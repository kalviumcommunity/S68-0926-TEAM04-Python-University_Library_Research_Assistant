"""Shared frontend integration errors."""


class BackendRequestError(RuntimeError):
    """Raised when the backend cannot return a usable research response."""
