
# Knowledge-Base MCP

FastMCP server for semantic search over a personal knowledge base using Qdrant and Claude Desktop.

## Features

- Semantic search
- Document retrieval
- Source listing
- Qdrant integration
- Claude Desktop support
- Testing with Pytest

## Tools

- `search_notes()` — Search the knowledge base
- `get_document()` — Retrieve a document
- `list_sources()` — List available documents

## Run

```bash
pip install -r requirements.txt
python -m server.main
````

## Test

```bash
pytest tests/test_tools.py -v
```


