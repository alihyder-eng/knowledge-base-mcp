"""Configuration package."""
from .settings import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION_NAME,
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    MCP_DEBUG,
    DEFAULT_TOP_K,
    MAX_TOP_K,
)

__all__ = [
    "QDRANT_HOST",
    "QDRANT_PORT",
    "QDRANT_COLLECTION_NAME",
    "MCP_SERVER_NAME",
    "MCP_SERVER_VERSION",
    "MCP_DEBUG",
    "DEFAULT_TOP_K",
    "MAX_TOP_K",
]
