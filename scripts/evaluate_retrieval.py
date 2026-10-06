"""Evaluate indexed retrieval against the checked-in question set."""

import json
from pathlib import Path

from Backend.services.rag_service import RAGService


QUESTIONS_PATH = Path("data/evaluation/questions.jsonl")


def evaluate() -> dict[str, float]:
    service = RAGService()
    cases = [
        json.loads(line)
        for line in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    hits = correct_documents = no_evidence = traceable = 0
    supported_total = sum(case["supported"] for case in cases)
    unsupported_total = len(cases) - supported_total
    for case in cases:
        results = service.retrieve(case["question"])
        expected = set(case["expected_document_ids"])
        found = {chunk["document_id"] for chunk in results}
        if case["supported"] and results:
            hits += 1
            correct_documents += int(bool(found & expected))
            traceable += int(
                all(chunk["document_id"] and chunk["chunk_id"] for chunk in results)
            )
        if not case["supported"] and not results:
            no_evidence += 1
    metrics = {
        "retrieval_hit_rate": hits / supported_total if supported_total else 0.0,
        "correct_document_rate": (
            correct_documents / supported_total if supported_total else 0.0
        ),
        "no_evidence_accuracy": (
            no_evidence / unsupported_total if unsupported_total else 0.0
        ),
        "citation_traceability": (
            traceable / supported_total if supported_total else 0.0
        ),
    }
    for name, value in metrics.items():
        print(f"{name}: {value:.2%}")
    return metrics


if __name__ == "__main__":
    evaluate()
