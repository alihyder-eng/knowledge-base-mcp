"""FastMCP server for personal knowledge-base.

This module implements the Model Context Protocol (MCP) server that exposes
three tools for interacting with the knowledge-base:
- search_notes: semantic search over documents
- get_document: retrieve a document by ID
- list_sources: list all available documents
"""

import logging
import sys
from typing import Any

from fastmcp import FastMCP

from config import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MCP_DEBUG,
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
)
from retrieval import get_document, list_sources, search_notes
from retrieval.models import SearchResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(MCP_SERVER_NAME, version=MCP_SERVER_VERSION)
logger.info("Initialized %s v%s", MCP_SERVER_NAME, MCP_SERVER_VERSION)


@mcp.tool(name="search_notes")
def search_notes_tool(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict[str, Any]]:
    """Search the knowledge base for relevant notes."""
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    if top_k <= 0 or top_k > MAX_TOP_K:
        raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}")

    logger.info("Searching for: %s (top_k=%s)", query.strip(), top_k)
    results = search_notes(query=query.strip(), top_k=top_k)

    formatted_results: list[dict[str, Any]] = []
    for result in results:
        if isinstance(result, SearchResult):
            formatted_results.append(result.to_dict())
        elif isinstance(result, dict):
            formatted_results.append(result)

    return formatted_results


@mcp.tool(name="get_document")
def get_document_tool(document_id: str) -> dict[str, Any]:
    """Return the full content of a document by ID."""
    doc_id = str(document_id or "").strip()
    if not doc_id:
        raise ValueError("Document ID cannot be empty")

    logger.info("Retrieving document: %s", doc_id)
    document = get_document(document_id=doc_id)
    return document.to_dict()


@mcp.tool(name="list_sources")
def list_sources_tool() -> list[dict[str, Any]]:
    """List all available documents in the knowledge base."""
    logger.info("Listing all sources")
    documents = list_sources()
    return [doc.to_dict() for doc in documents]


if __name__ == "__main__":
    try:
        logger.info("Starting %s server...", MCP_SERVER_NAME)
        logger.info("Debug mode: %s", MCP_DEBUG)
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        sys.exit(0)
    except Exception as exc:  # pragma: no cover
        logger.error("Server error: %s", exc, exc_info=True)
        sys.exit(1)
