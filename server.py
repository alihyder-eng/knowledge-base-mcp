from __future__ import annotations

from fastmcp import FastMCP

from config import load_settings
from doc_registry import get_document_meta, get_document_text, list_documents
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore

mcp = FastMCP(
    name="Personal Knowledge Base",
    instructions=(
        "Semantic search over the user's personal document corpus (ingested PDFs). "
        "Use search_notes to find relevant passages, get_document to pull full "
        "context for a citation, and list_sources to see what's indexed."
    ),
)

_settings = load_settings()
_store = QdrantStore(_settings)
_embedder = GeminiEmbedder(_settings)


@mcp.tool
def search_notes(query: str, top_k: int = 5) -> dict:
    """
    Search the personal knowledge base by meaning (semantic search), not
    exact keyword match.

    Args:
        query: Natural-language question or topic to search for.
        top_k: Number of ranked results to return (default 5, max 20).

    Returns:
        A dict with a "results" list, each item containing the matched text,
        a similarity score, the source document title/path, and a doc_id you
        can pass to get_document() for full context. If nothing clears the
        confidence threshold, "results" is empty and "message" explains why.
    """
    top_k = max(1, min(top_k, 20))
    query_vec = _embedder.embed_query(query)
    hits = _store.search(query_vec, top_k=top_k, user_id=_settings.mcp_default_user_id)

    confident = [h for h in hits if h.score >= _settings.similarity_threshold]
    if not confident:
        return {
            "results": [],
            "message": (
                "No confident match found for this query in the indexed corpus "
                f"(similarity threshold={_settings.similarity_threshold}). "
                "Try rephrasing, or check list_sources() to see what's indexed."
            ),
        }

    return {
        "results": [
            {
                "text": h.text,
                "score": round(h.score, 4),
                "doc_id": h.doc_id,
                "title": h.title,
                "source": h.source,
                "chunk_index": h.chunk_index,
            }
            for h in confident
        ]
    }


@mcp.tool
def get_document(doc_id: str) -> dict:
    """
    Fetch the full original text of an indexed document, given a doc_id
    returned by search_notes(). Use this when a snippet needs more
    surrounding context than the chunk alone provides.

    Args:
        doc_id: Document identifier, as returned in search_notes results.

    Returns:
        A dict with the document's metadata and full text, or an "error"
        key if the doc_id is not found.
    """
    meta = get_document_meta(doc_id, user_id=_settings.mcp_default_user_id)
    text = get_document_text(doc_id, user_id=_settings.mcp_default_user_id)
    if meta is None or text is None:
        return {"error": f"No document found with doc_id={doc_id!r}"}

    return {
        "doc_id": doc_id,
        "title": meta["title"],
        "source": meta["source_path"],
        "num_chunks": meta["num_chunks"],
        "ingested_at": meta["ingested_at"],
        "text": text,
    }


@mcp.tool
def list_sources() -> dict:
    """
    Enumerate every document currently indexed in the knowledge base.

    Returns:
        A dict with a "sources" list of {doc_id, title, source, num_chunks,
        ingested_at} for every ingested document, and a "count".
    """
    docs = list_documents(user_id=_settings.mcp_default_user_id)
    return {
        "count": len(docs),
        "sources": [
            {
                "doc_id": d["doc_id"],
                "title": d["title"],
                "source": d["source_path"],
                "num_chunks": d["num_chunks"],
                "ingested_at": d["ingested_at"],
            }
            for d in docs
        ],
    }


if __name__ == "__main__":
    mcp.run()