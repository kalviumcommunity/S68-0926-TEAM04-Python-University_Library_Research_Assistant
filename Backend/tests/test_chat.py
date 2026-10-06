from fastapi.testclient import TestClient

from Backend.main import app
from Backend.schemas.chat import ChatResponse
from Backend.schemas.citation import Citation


client = TestClient(app)


def test_chat_valid_request():
    response = client.post(
        "/chat",
        json={
            "question": "retrieval augmented generation",
            "filters": {},
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"]
    assert response.json()["citations"]
    assert response.json()["has_evidence"] is True


def test_chat_empty_question():
    response = client.post(
        "/chat",
        json={
            "question": "",
            "filters": {},
        },
    )

    assert response.status_code == 422


def test_chat_whitespace_question():
    response = client.post(
        "/chat",
        json={
            "question": "     ",
            "filters": {},
        },
    )

    assert response.status_code == 422


def test_chat_missing_question():
    response = client.post(
        "/chat",
        json={
            "filters": {},
        },
    )

    assert response.status_code == 422


def test_chat_response_schema():
    response = ChatResponse(
        answer="Test answer",
        citations=[],
    )

    assert response.answer == "Test answer"
    assert response.citations == []


def test_citation_schema():
    citation = Citation(
        document_id="doc_001",
        title="Student Engagement Research",
        page=12,
        section="Discussion",
    )

    assert citation.document_id == "doc_001"
    assert citation.title == "Student Engagement Research"
    assert citation.page == 12
    assert citation.section == "Discussion"


def test_transformer_answer_uses_top_semantic_evidence():
    response = client.post(
        "/chat",
        json={"question": "What is the Transformer architecture?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"][0]["document_id"] == "1706.03762v7"
    assert "stacked self-attention" in payload["answer"]