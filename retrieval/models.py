"""Data models for search results and documents."""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    """Represents a single search result."""
    relevant_text: str
    similarity_score: float
    document_name: str
    page_number: Optional[int] = None
    document_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "relevant_text": self.relevant_text,
            "similarity_score": self.similarity_score,
            "document_name": self.document_name,
            "page_number": self.page_number,
            "document_id": self.document_id,
            "metadata": self.metadata or {},
        }


@dataclass
class Document:
    """Represents a complete document."""
    id: str
    name: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class DocumentMetadata:
    """Metadata for a document in the knowledge-base."""
    id: str
    name: str
    size: int
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata or {},
        }
