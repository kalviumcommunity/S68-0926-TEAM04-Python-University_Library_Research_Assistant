"""Tests for the isolated frontend/backend request boundary."""

from frontend.utils.api_client import (
    build_query_payload,
    validate_chat_response,
)
from frontend.utils.errors import BackendRequestError


def test_build_query_payload_matches_agreed_contract() -> None:
    assert build_query_payload("What is RAG?", {"subject": "NLP"}) == {
        "question": "What is RAG?",
        "filters": {"subject": "NLP"},
    }


def test_validate_chat_response_accepts_optional_citation_fields() -> None:
    response = validate_chat_response(
        {"answer": "Evidence", "citations": [{"document_id": "doc"}]}
    )

    assert response["has_evidence"] is True


def test_validate_chat_response_rejects_invalid_citation() -> None:
    try:
        validate_chat_response({"answer": "Evidence", "citations": [{}]})
    except BackendRequestError:
        return
    raise AssertionError("Expected malformed citation to be rejected")
