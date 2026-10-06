# University Library Research Assistant API Contract

## 1. Chat API

### Endpoint

POST `/chat`

### Purpose

Receives an academic question from the user and sends the question
and optional filters to the backend RAG service interface.

The actual RAG implementation is owned by Person 1.

---

## 2. Request

### Request Body

```json
{
  "question": "What is retrieval augmented generation?",
  "filters": {}
}
```

`filters` may include supported document metadata such as `document_id`,
`document_type`, `year`, `subject`, and `author`.

## 3. Response

```json
{
  "answer": "Retrieved evidence excerpt...",
  "citations": [
    {
      "citation_id": 1,
      "chunk_id": "rag_survey.pdf-p19-c1",
      "document_id": "rag_survey.pdf",
      "title": "Retrieval-Augmented Generation for AI-Generated Content: A Survey",
      "author": "Author",
      "page": 19,
      "section": null,
      "excerpt": "Retrieved evidence excerpt...",
      "source_url": "https://example.edu/source",
      "score": 0.71,
      "metadata": {}
    }
  ],
  "has_evidence": true
}
```

When retrieval finds no evidence, `citations` is empty and `has_evidence` is
`false`; the answer is exactly:

```text
No supporting evidence was found in the library documents.