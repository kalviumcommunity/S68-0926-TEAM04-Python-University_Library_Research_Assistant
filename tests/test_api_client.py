"""Tests for the isolated frontend/backend request boundary."""

from frontend.utils.api_client import (
    build_query_payload,
)


def test_build_query_payload_matches_agreed_contract() -> None:
    assert build_query_payload("What is RAG?", {"subject": "NLP"}) == {
        "question": "What is RAG?",
        "filters": {"subject": "NLP"},
    }
