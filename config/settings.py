"""Configuration and environment settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Qdrant Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "knowledge_base")

# MCP Server Configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "knowledge-base-mcp")
MCP_SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")
MCP_DEBUG = os.getenv("MCP_DEBUG", "false").lower() == "true"

# Defaults
DEFAULT_TOP_K = 5
MAX_TOP_K = 50
