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

    if not isinstance(body, dict) or not isinstance(body.get("answer"), str):
        raise BackendRequestError("The research backend returned an invalid response.")
    if not isinstance(body.get("citations"), list):
        raise BackendRequestError("The research backend returned invalid citations.")
    return body
