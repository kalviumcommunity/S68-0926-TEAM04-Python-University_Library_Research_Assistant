"""Isolated boundary for the future FastAPI research endpoint."""

import os
from typing import Any

import httpx

from frontend.utils.errors import BackendRequestError


BackendNotConfiguredError = BackendRequestError


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
    """Send the agreed request to the FastAPI chat endpoint."""
    payload = build_query_payload(question, filters)
    base_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        response = httpx.post(
            f"{base_url}/chat",
            json=payload,
            timeout=15.0,
        )
        response.raise_for_status()
        body = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise BackendRequestError(
            "The research backend is unavailable or returned an invalid response."
        ) from error

    return validate_chat_response(body)


def validate_chat_response(body: object) -> dict[str, Any]:
    """Validate the shared chat response without assuming optional citation fields."""
    if not isinstance(body, dict) or not isinstance(body.get("answer"), str):
        raise BackendRequestError("The research backend returned an invalid response.")
    citations = body.get("citations")
    if not isinstance(citations, list):
        raise BackendRequestError("The research backend returned invalid citations.")
    for citation in citations:
        if not isinstance(citation, dict):
            raise BackendRequestError("The research backend returned an invalid citation.")
        if not isinstance(citation.get("document_id"), str):
            raise BackendRequestError("The research backend returned an invalid citation.")
    has_evidence = body.get("has_evidence", bool(citations))
    if not isinstance(has_evidence, bool):
        raise BackendRequestError("The research backend returned an invalid evidence flag.")
    return {**body, "has_evidence": has_evidence}
