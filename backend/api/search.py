from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from auth.dependencies import get_current_user
from database.models import User

from config import load_settings
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore
from backend.gemini import GeminiGenerator


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


# =========================================================
# SERVICES
# =========================================================

settings = load_settings()

store = QdrantStore(settings)

embedder = GeminiEmbedder(settings)

generator = GeminiGenerator(settings)


# =========================================================
# SEARCH
# =========================================================

@router.get("/")
def search_documents(
    q: str = Query(
        ...,
        min_length=1,
        description="Question to ask about uploaded documents",
    ),

    top_k: int = Query(
        5,
        ge=1,
        le=20,
        description="Maximum number of supporting sources",
    ),

    current_user: User = Depends(
        get_current_user
    ),
):
    """
    RAG search endpoint.

    Flow:

    1. Embed the user's question.
    2. Retrieve relevant chunks from Qdrant.
    3. Remove low-confidence matches.
    4. Keep the strongest chunk from each document.
    5. Generate ONE grounded answer using Gemini.
    6. Return the answer together with all supporting sources.
    """

    # =====================================================
    # 1. CLEAN QUERY
    # =====================================================

    query = q.strip()

    if not query:
        return {
            "query": q,
            "answer": (
                "Please enter a question about "
                "your uploaded documents."
            ),
            "results": [],
        }

    # =====================================================
    # 2. CREATE QUERY EMBEDDING
    # =====================================================

    query_vector = embedder.embed_query(
        query
    )

    # =====================================================
    # 3. RETRIEVE MORE CANDIDATES
    # =====================================================
    #
    # We retrieve more than top_k first.
    # This gives us enough candidates after
    # applying the similarity threshold and
    # document-level filtering.
    #

    retrieval_k = min(
        max(top_k * 5, top_k),
        100,
    )

    hits = store.search(
        query_vector=query_vector,
        top_k=retrieval_k,
        user_id=current_user.id,
    )

    # =====================================================
    # 4. APPLY SIMILARITY THRESHOLD
    # =====================================================

    confident_hits = [
        hit
        for hit in hits
        if hit.score >= settings.similarity_threshold
    ]

    # =====================================================
    # 5. KEEP BEST CHUNK FROM EACH DOCUMENT
    # =====================================================
    #
    # Prevents one document from dominating
    # the source list with many chunks.
    #

    best_by_document = {}

    for hit in confident_hits:

        existing = best_by_document.get(
            hit.doc_id
        )

        if (
            existing is None
            or hit.score > existing.score
        ):
            best_by_document[hit.doc_id] = hit

    # =====================================================
    # 6. SORT BY RELEVANCE
    # =====================================================

    final_results = sorted(
        best_by_document.values(),
        key=lambda hit: hit.score,
        reverse=True,
    )[:top_k]

    # =====================================================
    # 7. FORMAT SOURCES
    # =====================================================

    sources = []

    for hit in final_results:

        sources.append(
            {
                "text": hit.text,

                "score": round(
                    float(hit.score),
                    4,
                ),

                "document_id": hit.doc_id,

                "document_name": hit.title,

                "source": hit.source,

                "page_number": hit.page_number,

                "chunk_index": hit.chunk_index,
            }
        )

    # =====================================================
    # 8. NO RELEVANT SOURCES
    # =====================================================

    if not final_results:

        return {
            "query": query,

            "answer": (
                "I couldn't find enough relevant "
                "information in your uploaded documents "
                "to answer this question."
            ),

            "results": [],
        }

    # =====================================================
    # 9. BUILD GROUNDED CONTEXT
    # =====================================================

    context_parts = []

    for index, hit in enumerate(
        final_results,
        start=1,
    ):

        page = (
            hit.page_number
            if hit.page_number is not None
            else "N/A"
        )

        context_parts.append(
            (
                f"SOURCE {index}\n"
                f"Document: {hit.title}\n"
                f"Page: {page}\n"
                f"Relevance: {hit.score:.4f}\n\n"
                f"Content:\n{hit.text}"
            )
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    # =====================================================
    # 10. GENERATE ONE GROUNDED ANSWER
    # =====================================================

    try:

        answer = generator.generate(
            query=query,
            context=context,
        )

        if not answer or not answer.strip():

            answer = (
                "I found relevant information in "
                "your documents, but I couldn't "
                "generate an answer from it."
            )

    except Exception as exc:

        print(
            f"Answer generation error: {exc}"
        )

        answer = (
            "I found relevant information in "
            "your documents, but I couldn't "
            "generate an answer right now."
        )

    # =====================================================
    # 11. RETURN ONE ANSWER + ALL SOURCES
    # =====================================================

    return {
        "query": query,

        "answer": answer.strip(),

        "results": sources,
    }