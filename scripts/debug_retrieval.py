"""Print semantic retrieval results for development diagnostics."""

import argparse

from Backend.services.rag_service import RAGService


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    results = RAGService().retrieve(args.query, top_k=args.top_k)
    print(f"Query: {args.query!r}")
    print("Top retrieved results:")
    for index, result in enumerate(results, start=1):
        print(f"\n{index}.")
        print(f"document_id: {result['document_id']}")
        print(f"title: {result['metadata'].get('title')}")
        print(f"page: {result.get('page')}")
        print(f"score: {result['score']:.4f}")
        excerpt = result["text"][:500].encode("ascii", "replace").decode("ascii")
        print(f"excerpt: {excerpt}")


if __name__ == "__main__":
    main()
