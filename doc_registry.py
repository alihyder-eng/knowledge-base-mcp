from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TypedDict


REGISTRY_DIR = Path(__file__).parent / "data"
REGISTRY_FILE = REGISTRY_DIR / "registry.json"
FULLTEXT_DIR = REGISTRY_DIR / "fulltext"


class DocMeta(TypedDict):
    doc_id: str
    user_id: int
    title: str
    source_path: str
    num_chunks: int
    ingested_at: str


def _load() -> dict[str, DocMeta]:
    if not REGISTRY_FILE.exists():
        return {}

    try:
        data = json.loads(
            REGISTRY_FILE.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, dict):
            return {}

        return data

    except (json.JSONDecodeError, OSError):
        return {}


def _save(
    registry: dict[str, DocMeta]
) -> None:

    REGISTRY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REGISTRY_FILE.write_text(
        json.dumps(
            registry,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def make_doc_id(
    source_path: str,
    user_id: int,
) -> str:
    """
    Generate a unique document ID for every upload.

    The old implementation generated the same ID when the
    same user uploaded the same filename again. That caused
    PostgreSQL duplicate-key errors.

    A UUID guarantees that every uploaded document receives
    a new ID.
    """

    unique_value = (
        f"{user_id}:"
        f"{source_path}:"
        f"{uuid.uuid4()}"
    )

    return hashlib.sha1(
        unique_value.encode("utf-8")
    ).hexdigest()[:16]


def register_document(
    source_path: str,
    title: str,
    full_text: str,
    num_chunks: int,
    user_id: int,
) -> str:

    doc_id = make_doc_id(
        source_path,
        user_id,
    )

    FULLTEXT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fulltext_path = (
        FULLTEXT_DIR / f"{doc_id}.txt"
    )

    fulltext_path.write_text(
        full_text,
        encoding="utf-8",
    )

    registry = _load()

    registry[doc_id] = {
        "doc_id": doc_id,
        "user_id": user_id,
        "title": title,
        "source_path": source_path,
        "num_chunks": num_chunks,
        "ingested_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    _save(registry)

    return doc_id


def list_documents(
    user_id: int | None = None,
) -> list[DocMeta]:

    documents = list(
        _load().values()
    )

    if user_id is None:
        return documents

    return [
        document
        for document in documents
        if document["user_id"] == user_id
    ]


def get_document_meta(
    doc_id: str,
    user_id: int | None = None,
) -> Optional[DocMeta]:

    document = _load().get(doc_id)

    if document is None:
        return None

    if (
        user_id is not None
        and document["user_id"] != user_id
    ):
        return None

    return document


def get_document_text(
    doc_id: str,
    user_id: int | None = None,
) -> Optional[str]:

    meta = get_document_meta(
        doc_id,
        user_id,
    )

    if meta is None:
        return None

    path = (
        FULLTEXT_DIR / f"{doc_id}.txt"
    )

    if not path.exists():
        return None

    return path.read_text(
        encoding="utf-8"
    )