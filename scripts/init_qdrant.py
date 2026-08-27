#!/usr/bin/env python
"""Initialize Qdrant collection with sample data.

This script creates a test collection and populates it with sample documents
for testing the MCP server before integrating with real data.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def initialize_collection():
    """Create and initialize a test collection in Qdrant."""
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        logger.info(f"Connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
        
        # Check if collection exists
        try:
            client.get_collection(QDRANT_COLLECTION_NAME)
            logger.warning(f"Collection '{QDRANT_COLLECTION_NAME}' already exists")
            return
        except:
            pass
        
        # Create collection
        logger.info(f"Creating collection '{QDRANT_COLLECTION_NAME}'...")
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,  # Typical size for embedding models
                distance=Distance.COSINE,
            ),
        )
        logger.info("Collection created successfully")
        
        # Add sample documents
        logger.info("Adding sample documents...")
        sample_documents = [
            {
                "id": 1,
                "text": "Python is a high-level programming language known for its simplicity and readability.",
                "name": "Python Basics",
                "page": 1,
            },
            {
                "id": 2,
                "text": "FastMCP is a framework for building Model Context Protocol servers in Python.",
                "name": "FastMCP Guide",
                "page": 1,
            },
            {
                "id": 3,
                "text": "Qdrant is a vector database for similarity search with extended filtering support.",
                "name": "Qdrant Documentation",
                "page": 1,
            },
            {
                "id": 4,
                "text": "Claude Desktop is a native application that provides access to Claude AI models.",
                "name": "Claude Desktop Setup",
                "page": 1,
            },
            {
                "id": 5,
                "text": "Machine Learning uses algorithms to enable computers to learn from data.",
                "name": "ML Fundamentals",
                "page": 1,
            },
        ]
        
        # Create dummy embeddings (in practice, use actual embeddings)
        import numpy as np
        
        points = []
        for doc in sample_documents:
            # Create a simple deterministic "embedding"
            # In production, use actual embedding model
            np.random.seed(doc["id"])
            embedding = np.random.randn(384).tolist()
            
            point = PointStruct(
                id=doc["id"],
                vector=embedding,
                payload={
                    "name": doc["name"],
                    "content": doc["text"],
                    "page_number": doc["page"],
                    "metadata": {
                        "source": "sample",
                        "type": "documentation",
                    },
                },
            )
            points.append(point)
        
        # Upload points
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points,
        )
        logger.info(f"Added {len(points)} sample documents")
        
        # Get collection stats
        stats = client.get_collection(QDRANT_COLLECTION_NAME)
        logger.info(f"Collection stats: {stats.points_count} points")
        
    except Exception as e:
        logger.error(f"Failed to initialize collection: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    initialize_collection()
    logger.info("Collection initialization complete!")
