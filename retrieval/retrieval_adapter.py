"""Adapter for Taqadus's retrieval function.

This module provides the interface between MCP tools and the actual retrieval system.
When Taqadus provides the retrieval implementation, update this file to integrate it.
"""

from typing import List, Optional, Dict, Any
import logging

from .models import SearchResult, Document, DocumentMetadata
from .qdrant_client import QdrantVectorClient

logger = logging.getLogger(__name__)

# Initialize Qdrant client as fallback
_qdrant_client: Optional[QdrantVectorClient] = None


def get_qdrant_client() -> QdrantVectorClient:
    """Get or initialize the Qdrant client.
    
    Returns:
        QdrantVectorClient instance
    """
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantVectorClient()
    return _qdrant_client


# ============================================================================
# INTEGRATION POINTS FOR TAQADUS'S RETRIEVAL FUNCTION
# ============================================================================
# When Taqadus provides the retrieval implementation:
#
# 1. Import the retrieval functions:
#    from taqadus.retrieval import search_documents, get_document_by_id, list_documents
#
# 2. Update the functions below to call Taqadus's implementation
# 3. Ensure the functions return the expected data types
# 4. The MCP layer will automatically use the new implementation
# ============================================================================


def search_notes(
    query: str,
    top_k: int = 5,
) -> List[SearchResult]:
    """Search for notes using semantic search.
    
    This is a placeholder that will be replaced with Taqadus's retrieval function.
    
    Args:
        query: Search query string
        top_k: Number of top results to return
        
    Returns:
        List of SearchResult objects
        
    Raises:
        ValueError: If query is empty or top_k is invalid
        RuntimeError: If search fails or no results found
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    
    if top_k <= 0 or top_k > 50:
        raise ValueError("top_k must be between 1 and 50")

    try:
        client = get_qdrant_client()

        query_terms = {
            term
            for term in query.lower().split()
            if term.strip()
        }

        if not query_terms:
            return []

        documents = client.list_all_documents()
        scored_results: List[SearchResult] = []

        for doc in documents:
            payload = doc.get("payload", {})
            content = str(payload.get("content", ""))
            name = str(payload.get("name", "Unknown"))
            haystack = f"{name} {content}".lower()

            matched_terms = {term for term in query_terms if term in haystack}
            if not matched_terms:
                continue

            score = len(matched_terms) / len(query_terms)
            snippet = content[:200] if content else name

            scored_results.append(
                SearchResult(
                    relevant_text=snippet,
                    similarity_score=score,
                    document_name=name,
                    page_number=payload.get("page_number"),
                    document_id=str(doc.get("id")),
                    metadata=payload.get("metadata", {}),
                )
            )

        scored_results.sort(
            key=lambda result: (result.similarity_score, len(result.relevant_text)),
            reverse=True,
        )

        return scored_results[:top_k]
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise RuntimeError(f"Search operation failed: {str(e)}")


def get_document(document_id: str) -> Document:
    """Retrieve a complete document by ID.
    
    This is a placeholder that will be replaced with Taqadus's retrieval function.
    
    Args:
        document_id: Unique identifier for the document
        
    Returns:
        Document object with full content
        
    Raises:
        ValueError: If document_id is invalid
        RuntimeError: If document not found or retrieval fails
    """
    if not document_id or not document_id.strip():
        raise ValueError("Document ID cannot be empty")
    
    # TODO: Replace this with Taqadus's retrieval function
    try:
        client = get_qdrant_client()
        
        # Convert document_id to integer for Qdrant (adjust if needed)
        try:
            point_id = int(document_id)
        except ValueError:
            raise ValueError(f"Invalid document ID format: {document_id}")
        
        # Retrieve from Qdrant
        point = client.get_point(point_id)
        
        if not point:
            raise RuntimeError(f"Document not found: {document_id}")
        
        # Format as Document object
        payload = point.get("payload", {})
        doc = Document(
            id=str(point["id"]),
            name=payload.get("name", "Unknown"),
            content=payload.get("content", ""),
            metadata=payload.get("metadata", {}),
        )
        
        return doc
        
    except (ValueError, RuntimeError):
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise RuntimeError(f"Failed to retrieve document: {str(e)}")


def list_sources() -> List[DocumentMetadata]:
    """List all available documents in the knowledge-base.
    
    This is a placeholder that will be replaced with Taqadus's retrieval function.
    
    Returns:
        List of DocumentMetadata objects
        
    Raises:
        RuntimeError: If listing fails
    """
    # TODO: Replace this with Taqadus's retrieval function
    try:
        client = get_qdrant_client()
        
        # Get all documents from Qdrant
        documents = client.list_all_documents()
        
        results = []
        for doc in documents:
            payload = doc.get("payload", {})
            metadata = DocumentMetadata(
                id=str(doc["id"]),
                name=payload.get("name", "Unknown"),
                size=len(payload.get("content", "")),
                metadata=payload.get("metadata", {}),
            )
            results.append(metadata)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise RuntimeError(f"Failed to list documents: {str(e)}")
