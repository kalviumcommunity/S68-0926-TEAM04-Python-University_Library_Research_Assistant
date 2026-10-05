"""Backend health and real evidence integration tests."""

from fastapi.testclient import TestClient

from Backend.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_real_evidence_and_citations() -> None:
    response = client.post(
        "/chat",
        json={"question": "retrieval augmented generation", "filters": {}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["citations"]
    assert body["citations"][0]["document_id"]
    assert body["citations"][0]["page"] is not None


def test_chat_returns_explicit_no_evidence_state() -> None:
    response = client.post(
        "/chat",
        json={"question": "zzzz-not-in-the-library", "filters": {}},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "No supporting evidence was found in the library documents.",
        "citations": [],
    }


def test_chat_rejects_unrelated_multi_term_question() -> None:
    response = client.post(
        "/chat",
        json={"question": "What is quantum teleportation?", "filters": {}},
    )

    assert response.status_code == 200
    assert response.json()["citations"] == []
