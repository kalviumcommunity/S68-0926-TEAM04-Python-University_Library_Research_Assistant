"""Tests for the isolated frontend/backend request boundary."""

import pytest

from frontend.utils.api_client import (
    BackendNotConfiguredError,
    ask_research_backend,
    build_query_payload,
)


def test_build_query_payload_matches_agreed_contract() -> None:
    assert build_query_payload("What is RAG?", {"subject": "NLP"}) == {
        "question": "What is RAG?",
        "filters": {"subject": "NLP"},
    }


def test_backend_call_is_explicitly_unavailable_until_person_two_implements_it() -> None:
    with pytest.raises(BackendNotConfiguredError):
        ask_research_backend("What is RAG?")
