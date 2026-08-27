"""
Scaffold data/eval_queries.json from whatever is currently ingested.

This does NOT invent queries for you - retrieval quality must be judged
against real, hand-written queries the student knows the right answer to.
It just saves you the copy-pasting: for every ingested document it prints
its doc_id/title so you can write 2-4 realistic queries per document and
fill in "relevant_doc_ids" yourself.

Usage:
    python scripts/build_eval_template.py [--user-id 1]

Then edit the generated data/eval_queries.json by hand before running
`python eval.py`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import load_settings  # noqa: E402
from doc_registry import list_documents  # noqa: E402

OUTPUT_PATH = PROJECT_ROOT / "data" / "eval_queries.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        help="Only include documents owned by this user id (defaults to "
        "MCP_DEFAULT_USER_ID / all documents if omitted).",
    )
    args = parser.parse_args()

    settings = load_settings()
    user_id = args.user_id if args.user_id is not None else settings.mcp_default_user_id
    docs = list_documents(user_id=user_id)

    if not docs:
        print(
            f"No ingested documents found for user_id={user_id}. "
            "Run `python ingest.py <path>` first."
        )
        return

    print(f"Found {len(docs)} ingested document(s):\n")
    template = []
    for d in docs:
        print(f"  doc_id={d['doc_id']}  title={d['title']!r}  chunks={d['num_chunks']}")
        template.append(
            {
                "query": f"TODO: write a real question this doc answers ({d['title']})",
                "relevant_doc_ids": [d["doc_id"]],
            }
        )

    if OUTPUT_PATH.exists():
        print(f"\n{OUTPUT_PATH} already exists - not overwriting it.")
        print("Delete it first (or edit it directly) if you want a fresh template.")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(template, indent=2), encoding="utf-8")
    print(f"\nWrote template with {len(template)} entries to {OUTPUT_PATH}")
    print("Now edit each \"query\" by hand with a real question, then run: python eval.py")


if __name__ == "__main__":
    main()
