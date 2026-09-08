# S68-0926-TEAM04-Python-University_Library_Research_Assistant
# University Library Research Assistant

An AI-powered research assistant that helps university students find **concise, citation-backed answers** from research papers, theses, and course materials using **Retrieval-Augmented Generation (RAG)**.

## Problem

University libraries contain large collections of academic documents, but students often have to search through dozens of unrelated papers and materials to find one specific answer.

## Solution

The system retrieves relevant academic content, generates a grounded answer using an LLM, and displays the supporting sources and citations alongside the response.

### How It Works

```text
Student Question
      ↓
Streamlit UI
      ↓
Backend API
      ↓
RAG Retrieval
      ↓
Relevant Academic Sources
      ↓
LLM Grounded Generation
      ↓
Answer + Citations
```

## Key Features

* 🔎 Semantic search across academic documents
* 🤖 RAG-based grounded answers
* 📚 Research papers, theses, and course materials
* 📌 Citation-backed responses
* 🎯 Metadata-based filtering
* 🚫 No-evidence/refusal handling
* ⚡ Streaming responses
* 📄 Source and document viewing
* 📊 RAG evaluation and quality testing
* 🔐 Environment-based secret management

## Tech Stack

**Frontend**

* Streamlit

**Backend**

* Python
* REST API

**AI / RAG**

* Embeddings
* Vector Database
* LLM
* Semantic Retrieval

**Data & Testing**

* Academic document corpus
* Python testing framework
* RAG evaluation metrics

**Development**

* Git
* GitHub
* Feature branches
* Pull Requests

## Project Structure

```text
University-Library-RAG/
├── backend/       # API and AI integration
├── rag/           # Ingestion, retrieval, generation & evaluation
├── frontend/      # Streamlit application
├── data/          # Raw, processed and sample documents
├── tests/         # Backend, RAG, frontend & integration tests
├── docs/          # PRD, architecture, API & evaluation docs
├── scripts/       # Ingestion and evaluation scripts
├── .env.example
├── requirements.txt
└── README.md
```

## Team Responsibilities

| Role                   | Responsibility                                                                |
| ---------------------- | ----------------------------------------------------------------------------- |
| AI/RAG Engineer        | Ingestion, chunking, embeddings, retrieval, grounding, citations & evaluation |
| Backend/AI Integration | API, RAG integration, LLM orchestration, streaming, errors & infrastructure   |
| Streamlit/Product      | UI, chat, citations, sources, filters, UX & project administration            |

## Development Workflow

```text
Issue
  ↓
Feature Branch
  ↓
Implement + Test
  ↓
Pull Request
  ↓
Code Review
  ↓
Merge to main
```

`main` is protected. All development happens through feature branches and reviewed PRs.

## Documentation

Detailed project documentation is available in:

* `docs/PRD.md` — Product requirements
* `docs/ARCHITECTURE.md` — System architecture
* `docs/RAG_DESIGN.md` — RAG design
* `docs/API_CONTRACT.md` — Backend/API contract
* `docs/EVALUATION.md` — RAG evaluation strategy
* `docs/CONTRIBUTING.md` — Development workflow

## Project Goal

> **Ask → Retrieve → Explain → Cite**

The goal is to make academic research faster, clearer, and more reliable while ensuring that answers remain grounded in the university's available sources.
