from __future__ import annotations

import argparse
import json
from pathlib import Path

from config import load_settings
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore

DEFAULT_QUERIES_PATH = Path(__file__).parent / "data" / "eval_queries.json"


def precision_at_k(retrieved_doc_ids: list[str], relevant_doc_ids: set[str], k: int) -> float:
    top = retrieved_doc_ids[:k]
    if not top:
        return 0.0
    hits = sum(1 for d in top if d in relevant_doc_ids)
    return hits / len(top)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES_PATH)
    args = parser.parse_args()

    if not args.queries.exists():
        print(f"No eval query file found at {args.queries}. See docstring for the format.")
        return

    test_set = json.loads(args.queries.read_text())
    settings = load_settings()
    store = QdrantStore(settings)
    embedder = GeminiEmbedder(settings)

    scores = []
    print(f"{'query':<50} precision@{args.top_k}")
    print("-" * 70)
    for item in test_set:
        query = item["query"]
        relevant = set(item["relevant_doc_ids"])
        vec = embedder.embed_query(query)
        hits = store.search(vec, top_k=args.top_k)
        retrieved_ids = [h.doc_id for h in hits]
        p = precision_at_k(retrieved_ids, relevant, args.top_k)
        scores.append(p)
        print(f"{query[:48]:<50} {p:.2f}")

    mean_p = sum(scores) / len(scores) if scores else 0.0
    print("-" * 70)
    print(f"Mean precision@{args.top_k} over {len(scores)} queries: {mean_p:.3f}")


if __name__ == "__main__":
    main()
