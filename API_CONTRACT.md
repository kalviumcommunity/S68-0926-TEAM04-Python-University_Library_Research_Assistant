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
  "question": "What factors influence student engagement?",
  "filters": {}
}