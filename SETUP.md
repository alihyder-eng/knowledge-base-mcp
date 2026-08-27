# Setup Instructions

Quick start guide for the Knowledge-Base MCP Server.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Qdrant vector database (running locally or remotely)

## Installation

### 1. Clone or Download the Project

```bash
cd /path/to/knowledge-base-mcp
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your Qdrant configuration
# Default values should work for local Qdrant on localhost:6333
```

## Running Qdrant

### Option 1: Docker (Recommended)

```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

The Qdrant API will be available at `http://localhost:6333`

### Option 2: Download and Run

Visit [qdrant.io](https://qdrant.io/documentation/quick-start/) for local installation.

### Verify Qdrant is Running

```bash
curl http://localhost:6333/health
```

Should return: `{"status":"ok"}`

## Initialize Sample Data

Before testing, populate Qdrant with sample documents:

```bash
python scripts/init_qdrant.py
```

This creates a test collection with 5 sample documents.

## Test the Server

### Test 1: Direct Function Testing

```bash
python scripts/test_tools.py
```

This tests the retrieval functions without MCP protocol.

### Test 2: Run MCP Server

```bash
python -m server.main
```

Server will start and wait for MCP client connections. Press Ctrl+C to stop.

Expected output:
```
INFO:server.main:Initialized knowledge-base-mcp v1.0.0
INFO:server.main:Registered tool: search_notes
INFO:server.main:Registered tool: get_document
INFO:server.main:Registered tool: list_sources
INFO:server.main:All tools registered successfully
INFO:server.main:knowledge-base-mcp server is running
```

### Test 3: Run Pytest Suite

```bash
pip install pytest pytest-asyncio

pytest tests/test_tools.py -v
```

## Next: Integrate with Claude Desktop

See [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md) for step-by-step instructions.

## Project Structure

```
knowledge-base-mcp/
├── server/                 # MCP server implementation
│   ├── __init__.py
│   └── main.py            # FastMCP server with 3 tools
├── retrieval/             # Retrieval layer
│   ├── models.py          # Data models
│   ├── qdrant_client.py   # Qdrant vector DB client
│   ├── retrieval_adapter.py # Integration point for Taqadus
│   └── __init__.py
├── config/                # Configuration
│   ├── settings.py        # Environment and settings
│   └── __init__.py
├── scripts/               # Utility scripts
│   ├── init_qdrant.py    # Initialize Qdrant collection
│   └── test_tools.py     # Direct tool testing
├── tests/                 # Test suite
│   └── test_tools.py
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project metadata
├── .env.example          # Environment template
├── .claude-desktop-config.json  # Claude config template
└── README.md             # Full documentation
```

## MCP Tools Available

### 1. search_notes
Search your knowledge base for relevant information.

**Parameters:**
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results (1-50, default: 5)

**Example:**
```
"Search for information about Python in my knowledge base"
```

### 2. get_document
Retrieve the full content of a specific document.

**Parameters:**
- `document_id` (string, required): Document ID

**Example:**
```
"Get document with ID '1' from my knowledge base"
```

### 3. list_sources
See all available documents in your knowledge base.

**No parameters required**

**Example:**
```
"What documents are available in my knowledge base?"
```

## Configuration

### Environment Variables (.env)

```env
# Qdrant Connection
QDRANT_HOST=localhost      # Qdrant server host
QDRANT_PORT=6333          # Qdrant server port
QDRANT_COLLECTION_NAME=knowledge_base  # Collection name

# Server Settings
MCP_SERVER_NAME=knowledge-base-mcp
MCP_SERVER_VERSION=1.0.0
MCP_DEBUG=false            # Enable debug logging
```

### Integrating Taqadus's Retrieval Function

When Taqadus provides the retrieval implementation:

1. Place retrieval code in `retrieval/` directory
2. Update `retrieval/retrieval_adapter.py` to import and wrap functions
3. Ensure functions return expected data types (SearchResult, Document, DocumentMetadata)
4. MCP layer will automatically use the new implementation

See `retrieval/retrieval_adapter.py` for detailed integration instructions.

## Troubleshooting

### Qdrant Connection Failed

```
ERROR: Failed to connect to Qdrant
```

**Solution:**
1. Verify Qdrant is running: `curl http://localhost:6333/health`
2. Check QDRANT_HOST and QDRANT_PORT in .env
3. Ensure no firewall is blocking connections

### No Results from Search

**Solution:**
1. Verify collection has data: `python scripts/test_tools.py`
2. Initialize sample data: `python scripts/init_qdrant.py`
3. Try broader search queries

### Import Errors

**Solution:**
1. Activate virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify Python 3.11+: `python --version`

## Support

- **Documentation**: See [README.md](README.md)
- **Claude Integration**: See [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md)
- **Direct Testing**: Run `python scripts/test_tools.py`
- **MCP Protocol**: See [FastMCP documentation](https://github.com/jlowin/fastmcp)
