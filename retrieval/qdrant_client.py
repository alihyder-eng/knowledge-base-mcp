"""Qdrant vector database client."""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME
from .models import SearchResult, Document, DocumentMetadata

logger = logging.getLogger(__name__)


class QdrantVectorClient:
    """Client for interacting with Qdrant vector database."""

    def __init__(
        self,
        host: str = QDRANT_HOST,
        port: int = QDRANT_PORT,
        collection_name: str = QDRANT_COLLECTION_NAME,
    ):
        """Initialize Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection to use
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        
        try:
            self.client = QdrantClient(host=host, port=port)
            logger.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise RuntimeError(f"Failed to connect to Qdrant: {e}")

    def health_check(self) -> bool:
        """Check if Qdrant is healthy and collection exists.
        
        Returns:
            True if healthy and collection exists, False otherwise
        """
        try:
            # Try to get collection info
            self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            logger.warning(f"Qdrant health check failed: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in Qdrant.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of search results with scores and metadata
            
        Raises:
            RuntimeError: If search fails
        """
        if not query_vector:
            raise ValueError("Query vector cannot be empty")
        
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "score": result.score,
                    "id": result.id,
                    "payload": result.payload,
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Search failed: {e}")

    def get_point(self, point_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific point from Qdrant by ID.
        
        Args:
            point_id: The point ID to retrieve
            
        Returns:
            Point data with payload, or None if not found
            
        Raises:
            RuntimeError: If retrieval fails
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
            )
            
            if points:
                return {
                    "id": points[0].id,
                    "payload": points[0].payload,
                }
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve point {point_id}: {e}")
            raise RuntimeError(f"Failed to retrieve point: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Collection statistics including point count and vector config
            
        Raises:
            RuntimeError: If retrieval fails
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": collection_info.points_count,
                "status": collection_info.status,
                "config": {
                    "params": {
                        "vectors": collection_info.config.params.vectors,
                    }
                },
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise RuntimeError(f"Failed to get collection stats: {e}")

    def list_all_documents(self) -> List[Dict[str, Any]]:
        """List all documents (points) in the collection.
        
        Returns:
            List of all points with metadata
            
        Raises:
            RuntimeError: If retrieval fails
        """
        try:
            # Scroll through all points in the collection
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust based on collection size
            )
            
            results = []
            for point in points:
                results.append({
                    "id": point.id,
                    "payload": point.payload,
                })
            
            return results
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise RuntimeError(f"Failed to list documents: {e}")
