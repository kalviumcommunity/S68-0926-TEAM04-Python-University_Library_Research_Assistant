# S68-0926-TEAM04-Python-University_Library_Research_Assistant
# University Library Research Assistant

An academic library research assistant prototype that helps university students find **concise, citation-backed answers** from a small collection of research papers using traceable document ingestion and retrieval.

## Problem

University libraries contain large collections of academic documents, but students often have to search through dozens of unrelated papers and materials to find one specific answer.

## Solution

The current system retrieves relevant academic content with deterministic lexical matching and displays the supporting sources and citations alongside the response. LLM generation, embeddings, and vector search are planned follow-up work.

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
Answer Excerpt + Citations
```

## Key Features

* 🔎 Search across processed academic documents
* 🧭 Traceable page-level evidence
* 📚 Research papers, theses, and course materials
* 📌 Citation-backed responses
* 🎯 Metadata-based filtering
* 🚫 No-evidence/refusal handling
* 📄 Source and document viewing
* 🔐 Environment-based secret management

## Tech Stack

**Frontend**

* Streamlit

**Backend**

* Python
* REST API

**AI / RAG (current implementation)**

* PyMuPDF extraction
* Cleaning and metadata
* Configurable chunking
* Deterministic lexical retrieval

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
* `API_CONTRACT.md` — Backend/API contract
* `docs/EVALUATION.md` — Planned RAG evaluation strategy
* `docs/CONTRIBUTING.md` — Development workflow

## Project Goal

> **Ask → Retrieve → Explain → Cite**

The goal is to make academic research faster, clearer, and more reliable while ensuring that answers remain grounded in the university's available sources.

## Run locally

From the repository root, install dependencies and process the PDFs:

```powershell
python -m pip install -r requirements.txt
python -m scripts.process_documents
```

Start the backend in one terminal:

```powershell
python -m uvicorn Backend.main:app --host 127.0.0.1 --port 8000
```

Start Streamlit in a second terminal:

```powershell
python -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8510
```

Open `http://127.0.0.1:8510`. Run the tests with `python -m pytest -q`.

## Current limitations

Embeddings, ChromaDB, semantic vector retrieval, LLM generation, streaming, and
formal RAG evaluation are not implemented in this prototype. The backend uses
the processed JSONL chunks and deterministic lexical matching so that the
end-to-end ingestion, citation, and frontend flow can be demonstrated honestly.
