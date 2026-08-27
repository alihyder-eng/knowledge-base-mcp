import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill it in."
        )
    return val


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_embed_model: str
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str
    chunk_size_tokens: int
    chunk_overlap_tokens: int
    similarity_threshold: float
    # user_id used by the standalone MCP server / CLI ingest, where there's
    # no logged-in web user. The multi-user web app never uses this - it
    # always uses the authenticated user's real id.
    mcp_default_user_id: int
    # Gemini embedding output dimensionality. gemini-embedding-001 supports
    # variable output dims (e.g. 768/1536/3072); 768 keeps Qdrant storage small.
    embed_dim: int = 768


def load_settings() -> Settings:
    return Settings(
        gemini_api_key=_require("GEMINI_API_KEY"),
        gemini_embed_model=os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001"),
        qdrant_url=_require("QDRANT_URL"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "personal_kb"),
        chunk_size_tokens=int(os.getenv("CHUNK_SIZE_TOKENS", "400")),
        chunk_overlap_tokens=int(os.getenv("CHUNK_OVERLAP_TOKENS", "60")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.55")),
        mcp_default_user_id=int(os.getenv("MCP_DEFAULT_USER_ID", "1")),
    )
