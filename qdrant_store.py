from __future__ import annotations

import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from config import Settings


@dataclass
class SearchHit:
    text: str
    score: float
    doc_id: str
    source: str
    title: str
    chunk_index: int
    page_number: int | None


class QdrantStore:

    def __init__(self, settings: Settings):
        self.settings = settings

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )

    def ensure_collection(self) -> None:
        existing = [
            c.name
            for c in self.client.get_collections().collections
        ]

        if self.settings.qdrant_collection in existing:
            return

        self.client.create_collection(
            collection_name=self.settings.qdrant_collection,
            vectors_config=qm.VectorParams(
                size=self.settings.embed_dim,
                distance=qm.Distance.COSINE,
            ),
        )

    @staticmethod
    def _point_id(
        doc_id: str,
        chunk_index: int,
    ) -> str:
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{doc_id}:{chunk_index}",
            )
        )

    def upsert_chunks(
        self,
        doc_id: str,
        title: str,
        source: str,
        chunk_texts: list[str],
        embeddings: list[list[float]],
        user_id: int,
        page_numbers: list[int | None] | None = None,
    ) -> int:

        if page_numbers is None:
            page_numbers = [None] * len(chunk_texts)

        if len(chunk_texts) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        if len(chunk_texts) != len(page_numbers):
            raise ValueError(
                "Number of chunks and page numbers must match."
            )

        points = []

        for i, (text, vec) in enumerate(
            zip(chunk_texts, embeddings)
        ):

            points.append(
                qm.PointStruct(
                    id=self._point_id(
                        doc_id,
                        i,
                    ),
                    vector=vec,
                    payload={
                        "doc_id": doc_id,
                        "user_id": user_id,
                        "title": title,
                        "source": source,
                        "chunk_index": i,
                        "page_number": page_numbers[i],
                        "text": text,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.settings.qdrant_collection,
            points=points,
        )

        return len(points)

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        user_id: int,
    ) -> list[SearchHit]:

        user_filter = qm.Filter(
            must=[
                qm.FieldCondition(
                    key="user_id",
                    match=qm.MatchValue(
                        value=user_id
                    ),
                )
            ]
        )

        results = self.client.query_points(
            collection_name=self.settings.qdrant_collection,
            query=query_vector,
            query_filter=user_filter,
            limit=top_k,
            with_payload=True,
        ).points

        hits = []

        for r in results:

            payload = r.payload or {}

            hits.append(
                SearchHit(
                    text=payload.get("text", ""),
                    score=r.score,
                    doc_id=payload.get("doc_id", ""),
                    source=payload.get("source", ""),
                    title=payload.get("title", ""),
                    chunk_index=payload.get(
                        "chunk_index",
                        0,
                    ),
                    page_number=payload.get(
                        "page_number"
                    ),
                )
            )

        return hits

    def delete_document(
        self,
        doc_id: str,
        user_id: int,
    ):

        document_filter = qm.Filter(
            must=[
                qm.FieldCondition(
                    key="doc_id",
                    match=qm.MatchValue(
                        value=doc_id
                    ),
                ),
                qm.FieldCondition(
                    key="user_id",
                    match=qm.MatchValue(
                        value=user_id
                    ),
                ),
            ]
        )

        self.client.delete(
            collection_name=self.settings.qdrant_collection,
            points_selector=qm.FilterSelector(
                filter=document_filter
            ),
        )