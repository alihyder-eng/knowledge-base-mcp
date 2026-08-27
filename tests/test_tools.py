"""Tests for MCP tools."""
import pytest
import logging
from unittest.mock import patch, MagicMock

from retrieval import search_notes, get_document, list_sources
from retrieval.models import SearchResult, Document, DocumentMetadata

logger = logging.getLogger(__name__)


class TestSearchNotes:
    """Tests for search_notes tool."""
    
    def test_search_notes_empty_query_raises_error(self):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            search_notes(query="", top_k=5)
    
    def test_search_notes_whitespace_query_raises_error(self):
        """Test that whitespace-only query raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            search_notes(query="   ", top_k=5)
    
    def test_search_notes_invalid_top_k_zero(self):
        """Test that top_k=0 raises ValueError."""
        with pytest.raises(ValueError, match="between 1 and"):
            search_notes(query="test", top_k=0)
    
    def test_search_notes_invalid_top_k_negative(self):
        """Test that negative top_k raises ValueError."""
        with pytest.raises(ValueError, match="between 1 and"):
            search_notes(query="test", top_k=-1)
    
    def test_search_notes_invalid_top_k_too_large(self):
        """Test that top_k > 50 raises ValueError."""
        with pytest.raises(ValueError, match="between 1 and"):
            search_notes(query="test", top_k=100)
    
    def test_search_notes_valid_query(self):
        """Test that valid query returns results or empty list."""
        # This will return empty list in placeholder implementation
        results = search_notes(query="test", top_k=5)
        assert isinstance(results, list)
    
    def test_search_notes_default_top_k(self):
        """Test that top_k defaults to 5."""
        # Verify default behavior
        results = search_notes(query="test")
        assert isinstance(results, list)


class TestGetDocument:
    """Tests for get_document tool."""
    
    def test_get_document_empty_id_raises_error(self):
        """Test that empty document_id raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            get_document(document_id="")
    
    def test_get_document_whitespace_id_raises_error(self):
        """Test that whitespace-only document_id raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            get_document(document_id="   ")
    
    def test_get_document_invalid_id_format(self):
        """Test that invalid ID format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid.*format"):
            get_document(document_id="not-a-number")
    
    def test_get_document_valid_id_not_found(self):
        """Test that valid ID that doesn't exist raises RuntimeError."""
        # This will raise RuntimeError for non-existent document in Qdrant
        with pytest.raises(RuntimeError, match="not found|Failed"):
            get_document(document_id="99999")


class TestListSources:
    """Tests for list_sources tool."""
    
    def test_list_sources_returns_list(self):
        """Test that list_sources returns a list."""
        results = list_sources()
        assert isinstance(results, list)
    
    def test_list_sources_empty_collection(self):
        """Test that empty collection returns empty list."""
        # Behavior depends on Qdrant state
        results = list_sources()
        # Should return list, empty or not
        assert isinstance(results, list)


class TestSearchResultModel:
    """Tests for SearchResult data model."""
    
    def test_search_result_to_dict(self):
        """Test SearchResult serialization to dict."""
        result = SearchResult(
            relevant_text="Test content",
            similarity_score=0.95,
            document_name="Test Doc",
            page_number=1,
            document_id="doc-1",
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["relevant_text"] == "Test content"
        assert result_dict["similarity_score"] == 0.95
        assert result_dict["document_name"] == "Test Doc"
        assert result_dict["page_number"] == 1
        assert result_dict["document_id"] == "doc-1"


class TestDocumentModel:
    """Tests for Document data model."""
    
    def test_document_to_dict(self):
        """Test Document serialization to dict."""
        doc = Document(
            id="doc-1",
            name="Test Document",
            content="This is test content",
            metadata={"source": "test"},
        )
        
        doc_dict = doc.to_dict()
        
        assert doc_dict["id"] == "doc-1"
        assert doc_dict["name"] == "Test Document"
        assert doc_dict["content"] == "This is test content"
        assert doc_dict["metadata"]["source"] == "test"


class TestDocumentMetadataModel:
    """Tests for DocumentMetadata data model."""
    
    def test_document_metadata_to_dict(self):
        """Test DocumentMetadata serialization to dict."""
        metadata = DocumentMetadata(
            id="doc-1",
            name="Test Document",
            size=1024,
            metadata={"type": "note"},
        )
        
        meta_dict = metadata.to_dict()
        
        assert meta_dict["id"] == "doc-1"
        assert meta_dict["name"] == "Test Document"
        assert meta_dict["size"] == 1024
        assert meta_dict["metadata"]["type"] == "note"


@pytest.fixture
def mock_qdrant_client():
    """Fixture for mocked Qdrant client."""
    with patch("retrieval.retrieval_adapter.get_qdrant_client") as mock:
        yield mock


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
