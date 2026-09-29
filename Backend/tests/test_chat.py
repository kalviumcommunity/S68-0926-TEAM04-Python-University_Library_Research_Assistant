from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.chat import ChatResponse
from backend.schemas.citation import Citation


client = TestClient(app)


def test_chat_valid_request():
    response = client.post(
        "/chat",
        json={
            "question": "What factors influence student engagement?",
            "filters": {},
        },
    )

    assert response.status_code == 503


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