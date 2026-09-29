"""Isolated boundary for the future FastAPI research endpoint."""

from typing import Any


class BackendNotConfiguredError(RuntimeError):
    """Raised until Person 2 provides the agreed backend endpoint."""


def build_query_payload(
    question: str,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the agreed request shape without making a network call."""
    return {"question": question, "filters": filters or {}}


def ask_research_backend(
    question: str,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reserve the API call boundary for the backend implementation."""
    build_query_payload(question, filters)
    raise BackendNotConfiguredError(
        "The FastAPI research endpoint is not available yet."
    )
