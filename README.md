
# Personal Knowledge-Base MCP

FastMCP server for semantic search over documents using Qdrant.

## Features
- Semantic search
- Document retrieval
- Source listing
- Claude Desktop support

## Setup

```bash
pip install -r requirements.txt
docker compose up -d
cp .env.example .env
````

Add your `GEMINI_API_KEY` to `.env`.

## Run

```bash
python ingest.py ./documents
python server.py
```

## Tools

* `search_notes()`
* `get_document()`
* `list_sources()`

**Status:** ✅ Complete


