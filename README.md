# Personal Knowledge-Base MCP Server

<<<<<<< HEAD
A FastMCP server that exposes a personal knowledge-base stored in Qdrant vector database through Model Context Protocol (MCP) tools. This server can be integrated with Claude Desktop to enable semantic search over your documents.

## Features

- **search_notes**: Semantic search over your knowledge-base with configurable top-k results
- **get_document**: Retrieve full document content by document ID
- **list_sources**: List all available documents in the knowledge-base
- **Error Handling**: Comprehensive error handling for invalid queries, missing documents, and server errors
- **Claude Desktop Integration**: Full MCP configuration for seamless integration with Claude Desktop

## Project Structure

```
knowledge-base-mcp/
├── server/                 # FastMCP server implementation
│   ├── __init__.py
│   └── main.py            # Main MCP server with tools
├── retrieval/             # Retrieval system integration
│   ├── __init__.py
│   ├── qdrant_client.py   # Qdrant vector database client
│   ├── retrieval_adapter.py # Adapter for Taqadus's retrieval function
│   └── models.py          # Data models for search results
├── config/                # Configuration
│   ├── __init__.py
│   └── settings.py        # Settings and environment variables
├── tests/                 # Tests
│   └── test_tools.py      # Tool testing
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project metadata
└── README.md             # This file
```

## Installation

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Qdrant configuration
   ```

## Qdrant Setup

### Option 1: Docker (Recommended for development)

```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

### Option 2: Local Installation

Download and run Qdrant from [qdrant.io](https://qdrant.io/documentation/quick-start/)

The server expects Qdrant to be running on `localhost:6333` by default.

## Running the MCP Server

```bash
python -m server.main
```

The server will start and be ready to accept MCP connections.

## MCP Tools

### 1. search_notes(query: str, top_k: int = 5) -> List[SearchResult]

Search for notes in the knowledge-base using semantic search.

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of top results to return (default: 5)

**Returns:**
- List of SearchResult objects containing:
  - `relevant_text`: The matching text snippet
  - `similarity_score`: Score between 0 and 1
  - `document_name`: Name of the source document
  - `page_number`: Page number in the document (if applicable)
  - `document_id`: Unique identifier for the document

**Errors:**
- `ValueError`: If query is empty
- `RuntimeError`: If no results found or server error

### 2. get_document(document_id: str) -> Document

Retrieve a complete document by its ID.

**Parameters:**
- `document_id` (str): The unique identifier of the document

**Returns:**
- Document object containing:
  - `id`: Document ID
  - `name`: Document name
  - `content`: Full document content
  - `metadata`: Document metadata

**Errors:**
- `ValueError`: If document_id is invalid
- `RuntimeError`: If document not found

### 3. list_sources() -> List[DocumentMetadata]

List all available documents in the knowledge-base.

**Returns:**
- List of DocumentMetadata objects containing:
  - `id`: Document ID
  - `name`: Document name
  - `size`: Size of the document
  - `created_at`: Creation timestamp
  - `metadata`: Additional document metadata

**Errors:**
- `RuntimeError`: If server error occurs

## Integrating with Taqadus's Retrieval Function

When Taqadus provides the retrieval implementation:

1. Place the retrieval code in `retrieval/` directory
2. Update `retrieval/retrieval_adapter.py` to import and wrap Taqadus's functions
3. Update the `search_notes()`, `get_document()`, and `list_sources()` tools to call your functions
4. The MCP layer will automatically use the new implementation

See `retrieval/retrieval_adapter.py` for the expected function signatures.

## Claude Desktop Integration

### Configuration

1. Locate Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "knowledge-base-mcp": {
         "command": "python",
         "args": ["-m", "server.main"],
         "cwd": "/path/to/knowledge-base-mcp"
       }
     }
   }
   ```

3. Restart Claude Desktop

### Verifying Connection

In Claude Desktop, you should see the knowledge-base-mcp tools available. Test with a simple query like:
> "Search for information about [topic] in my knowledge base"

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

For specific tool testing:

```bash
pytest tests/test_tools.py::test_search_notes -v
```

## Troubleshooting

### Connection Issues

- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check `.env` file has correct QDRANT_HOST and QDRANT_PORT
- Ensure virtual environment is activated

### No Tools Found in Claude

- Verify MCP server starts without errors: `python -m server.main`
- Check Claude Desktop configuration file for correct paths
- Restart Claude Desktop after configuration changes
- Check Claude debug logs for connection errors

### Search Returns No Results

- Verify documents are loaded in Qdrant
- Check query is not too specific or contains enough context
- Ensure `QDRANT_COLLECTION_NAME` matches your collection

## License

MIT
=======
An MCP (Model Context Protocol) server that exposes **semantic search over
your own document corpus** — PDFs, notes, docs — as callable tools any
MCP-compatible client (Claude Desktop, Claude Code, a custom client) can use
live, plus a full multi-user web app (FastAPI + Next.js) built on top of the
same retrieval engine.

## Problem

Keyword search misses content that's semantically related but doesn't share
exact words. This project lets a client search a personal document corpus
**by meaning**, with cited, ranked results, exposed at the protocol level
(MCP tools) — not baked into a one-off chatbot UI.

## Architecture

```
                       ┌─────────────────────────────────────────┐
                       │        Shared retrieval engine            │
                       │  chunking.py · embeddings.py · qdrant_store.py │
                       │  doc_registry.py · ingest.py                │
                       └───────────────┬─────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
   ┌──────────▼──────────┐  ┌──────────▼──────────┐   ┌─────────▼─────────┐
   │   server.py           │  │   backend/ (FastAPI)  │   │      Qdrant         │
   │   FastMCP server       │  │  auth · documents ·   │   │  vector database     │
   │   (stdio / JSON-RPC)   │  │  search · users DB     │   │  (Docker or Cloud)   │
   └──────────┬──────────┘  └──────────┬──────────┘   └─────────────────────┘
              │                        │
   ┌──────────▼──────────┐  ┌──────────▼──────────┐
   │  Claude Desktop /      │  │  frontend/ (Next.js)  │
   │  Claude Code / any     │  │  signup·login·upload· │
   │  MCP client             │  │  search UI              │
   └───────────────────────┘  └───────────────────────┘
```

- **Chunking** (`chunking.py`): paragraph-aware, ~400-token windows with
  60-token overlap so context isn't lost at chunk boundaries. Oversized
  paragraphs are hard-split so nothing dodges chunking.
- **Embeddings** (`embeddings.py`): Gemini's embedding API, called with
  distinct `task_type`s — `RETRIEVAL_DOCUMENT` at ingest time,
  `RETRIEVAL_QUERY` at search time.
- **Vector store** (`qdrant_store.py`): one Qdrant collection, cosine
  distance, deterministic point IDs (`uuid5(doc_id:chunk_index)`), and a
  `user_id` payload field so every query and delete is scoped per user.
- **Doc registry** (`doc_registry.py`): flat local JSON (`data/registry.json`)
  + one `.txt` per document (`data/fulltext/`). Qdrant only holds chunk text
  for search; full-document fetches and the source list are served from
  here.
- **MCP server** (`server.py`): exposes `search_notes`, `get_document`,
  `list_sources` as MCP tools, for a single local "demo" user
  (`MCP_DEFAULT_USER_ID`).
- **Backend** (`backend/`): FastAPI wrapping the same retrieval engine,
  behind JWT auth, with a real `users`/`documents` table (SQLite by default,
  Postgres-ready) so multiple real people can each have an isolated corpus
  and search history.
- **Frontend** (`frontend/`): Next.js app — signup/login, document
  upload/list/delete, and a search page — talking to the backend API.

## Tech stack

FastMCP (Python) · FastAPI · Next.js/React · Qdrant · Gemini embeddings API
· SQLAlchemy · pypdf

## Repo layout

```
personal-knowledge-mcp/
├── server.py            # MCP server (search_notes / get_document / list_sources)
├── ingest.py             # CLI: ingest PDFs/MD/TXT into Qdrant
├── eval.py               # retrieval precision@k evaluation
├── chunking.py, embeddings.py, qdrant_store.py, doc_registry.py, config.py
├── data/                 # doc_registry storage + eval query sets (git-ignored except examples)
├── sample_corpus/        # a single sample PDF to smoke-test setup — ingest YOUR OWN corpus for the real demo
├── scripts/build_eval_template.py
├── docker-compose.yml    # local Qdrant, no cloud signup needed
├── backend/              # FastAPI multi-user web API
│   ├── main.py
│   ├── auth/, database/, api/
│   └── requirements.txt
└── frontend/              # Next.js web UI
    ├── app/ (login, signup, dashboard, documents, search)
    └── lib/api.ts
```

---

## 1. Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for local Qdrant) — or a free [Qdrant Cloud](https://cloud.qdrant.io) cluster instead

### 1a. Get API keys
- Gemini API key (free tier): https://aistudio.google.com/apikey

### 1b. Configure environment

```bash
cd personal-knowledge-mcp
cp .env.example .env
```

Edit `.env` and fill in at least `GEMINI_API_KEY`, and generate a real
`JWT_SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` is read from the project root by every component (MCP server,
CLI scripts, and the FastAPI backend) — you only maintain one file.

### 1c. Start Qdrant

```bash
docker compose up -d qdrant
```

This starts Qdrant on `http://localhost:6333` (dashboard at
`http://localhost:6333/dashboard`), matching the default `QDRANT_URL` in
`.env.example`. (Skip this and point `QDRANT_URL`/`QDRANT_API_KEY` at a
Qdrant Cloud cluster instead if you'd rather not run Docker.)

### 1d. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt              # MCP server / CLI tools
pip install -r backend/requirements.txt       # FastAPI backend (also pulls in requirements.txt)
```

### 1e. Install frontend dependencies

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
cd ..
```

---

## 2. Standalone MCP server (Claude Desktop demo)

This is the core deliverable: a real MCP server, connectable live.

### Ingest your own corpus

Use a **real, personally-owned corpus** — your notes, a paper collection, a
club's docs, a company's public documentation. `sample_corpus/` has one
placeholder PDF only so you can smoke-test the pipeline end to end; replace
it with your real documents before you demo/evaluate.

```bash
python ingest.py /path/to/your/pdfs
```

Prints a `doc_id` per file (chunks are tagged with `MCP_DEFAULT_USER_ID`
from `.env`, since there's no logged-in web user in this mode).

### Run the server

```bash
python server.py
```

### Connect from Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "personal-kb": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/personal-knowledge-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop, then ask it something your corpus can answer — it
will call `search_notes` and cite the source.

### Tools exposed

| Tool | Purpose |
|---|---|
| `search_notes(query, top_k=5)` | Ranked, cited chunks matching a query by meaning. Returns "no confident match" below the similarity threshold instead of forcing a weak answer. |
| `get_document(doc_id)` | Full original text of a source, for when a snippet needs more context. |
| `list_sources()` | Everything currently indexed. |

### Evaluation (retrieval precision@k)

```bash
python scripts/build_eval_template.py   # scaffolds data/eval_queries.json from what's ingested
# now edit data/eval_queries.json: replace each TODO query with a real
# question you know the right answer to
python eval.py
```

Reports mean precision@k against your hand-labeled query set — this is the
one measurable retrieval number the project is judged on, so write 15-25
realistic queries covering your actual documents.

---

## 3. Multi-user web app (backend + frontend)

### Run the backend

```bash
source .venv/bin/activate
cd backend
uvicorn main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`. Uses SQLite by default
(`personal_kb.db` at the project root, zero setup) — set `DATABASE_URL` in
`.env` to point at Postgres instead for a production-style deployment.

### Run the frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` → sign up → upload PDF/MD/TXT documents →
search them. Each user's documents and searches are isolated (Qdrant
`user_id` payload filter + a per-user `documents` table), enforced by JWT
auth on every backend route.

### Web API summary

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/signup` | Create an account |
| POST | `/auth/login` | Get a JWT access token |
| GET | `/me` | Current user |
| POST | `/documents/upload` | Upload + ingest a PDF/MD/TXT (multipart) |
| GET | `/documents/` | List your documents |
| DELETE | `/documents/{id}` | Delete a document (Qdrant + DB) |
| GET | `/search/?q=...&top_k=5` | Semantic search over your documents |

---

## Non-goals

No autonomous multi-step agent behavior or planning loops. No fine-tuning.
>>>>>>> origin/main
