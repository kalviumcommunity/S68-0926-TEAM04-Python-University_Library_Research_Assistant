from fastapi.testclient import TestClient
import pytest

from Backend.main import app
from Backend.schemas.chat import ChatResponse
from Backend.schemas.citation import Citation
from Backend.routes import chat as chat_route
from Backend.services.llm_service import GeneratedAnswer


client = TestClient(app)


def _mock_generated_answer(question, evidence):
    if "Transformer" in question:
        return GeneratedAnswer("The Transformer architecture uses stacked self-attention.", [1])
    if "BERT" in question and "masking" not in question:
        return GeneratedAnswer("BERT is a language representation model.", [1])
    if "masking" in question:
        return GeneratedAnswer("BERT uses MASK tokens during training.", [1])
    return GeneratedAnswer("retrieval augmented generation", [1])


def _mock_retrieval(question, filters):
    if "Transformer" in question:
        document_id = "1706.03762v7"
        text = "The Transformer architecture uses stacked self-attention layers and feed-forward networks to process sequences."
        title = "Attention Is All You Need"
    elif "BERT" in question:
        document_id = "1810.04805v2"
        text = "BERT is a language representation model designed to pre-train deep bidirectional representations from unlabeled text."
        title = "BERT"
    else:
        document_id = "rag-001"
        text = "Retrieval augmented generation combines retrieved evidence with language model generation."
        title = "Retrieval Augmented Generation"
    return [{
        "chunk_id": f"{document_id}-chunk-1",
        "document_id": document_id,
        "text": text,
        "page": 1,
        "section": "Abstract",
        "metadata": {"title": title},
        "score": 0.91,
    }]


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    monkeypatch.setattr(chat_route.llm_service, "generate", _mock_generated_answer)
    monkeypatch.setattr(chat_route.rag_service, "retrieve", _mock_retrieval)


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
    assert len(payload["answer"]) < len(payload["citations"][0]["excerpt"])
    assert not payload["answer"].startswith("Figure")


def test_definition_answer_prefers_definition_over_incidental_detail():
    response = client.post("/chat", json={"question": "What is BERT?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"]
    assert payload["citations"][0]["document_id"] == "1810.04805v2"
    assert "language representation model" in payload["answer"]
    assert "80%, 10%, 10%" not in payload["answer"]
    assert "Jacob Devlin" not in payload["answer"]
    assert len(payload["citations"]) == 1


def test_specific_question_can_select_detail_evidence():
    response = client.post(
        "/chat",
        json={"question": "What masking strategy does BERT use?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"][0]["document_id"] == "1810.04805v2"
    assert "MASK" in payload["answer"] or "mask" in payload["answer"]


def test_chat_generates_and_maps_only_valid_citations(monkeypatch):
    evidence = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "page": 4,
            "section": "Introduction",
            "metadata": {"title": "Research paper"},
            "score": 0.91,
            "text": "Evidence text",
        }
    ]

    monkeypatch.setattr(chat_route.rag_service, "retrieve", lambda question, filters: evidence)

    class FakeLLM:
        def generate(self, question, retrieved_evidence):
            assert question == "What is the topic?"
            assert retrieved_evidence == evidence
            return GeneratedAnswer("Grounded answer", [1, 99])

    monkeypatch.setattr(chat_route, "llm_service", FakeLLM())

    response = client.post("/chat", json={"question": "What is the topic?"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Grounded answer",
        "citations": [
            {
                "citation_id": 1,
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "title": "Research paper",
                "author": None,
                "excerpt": "Evidence text",
                "page": 4,
                "section": "Introduction",
                "source_url": None,
                "score": 0.91,
                "metadata": {"title": "Research paper"},
            }
        ],
        "has_evidence": True,
    }


def test_chat_does_not_call_llm_without_evidence(monkeypatch):
    monkeypatch.setattr(chat_route.rag_service, "retrieve", lambda question, filters: [])

    class FailingLLM:
        def generate(self, question, retrieved_evidence):
            raise AssertionError("LLM must not be called without evidence")

    monkeypatch.setattr(chat_route, "llm_service", FailingLLM())

    response = client.post("/chat", json={"question": "Unsupported question"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "No supporting evidence was found in the library documents.",
        "citations": [],
        "has_evidence": False,
    }
