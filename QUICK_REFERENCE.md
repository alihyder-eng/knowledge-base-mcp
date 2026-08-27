# Quick Reference - MCP Tools

## Overview
Three MCP tools for accessing your knowledge base through Claude Desktop.

---

## Tool 1: search_notes

**Purpose**: Search for relevant information in your knowledge base

**Required Parameters**:
- `query` (string): What you're looking for
  - Example: "machine learning", "Python best practices"

**Optional Parameters**:
- `top_k` (integer): How many results to return
  - Range: 1-50 (default: 5)
  - Higher numbers = more results but slower response

**What It Returns**:
- List of matching documents
- Relevance score (0.0 - 1.0)
- Document name
- Page number (if applicable)
- Document ID
- Text snippet containing the match

**Example Claude Prompt**:
```
Search my knowledge base for information about "artificial intelligence".
Show me the top 3 results.
```

---

## Tool 2: get_document

**Purpose**: Get the complete content of a specific document

**Required Parameters**:
- `document_id` (string): The ID of the document
  - Get IDs from search_notes results or list_sources
  - Example: "1", "doc-123"

**What It Returns**:
- Document name
- Complete document content
- Document metadata
- Creation timestamp

**Example Claude Prompt**:
```
Get the full content of document ID 1 from my knowledge base.
```

---

## Tool 3: list_sources

**Purpose**: See what documents are available in your knowledge base

**Parameters**: None required

**What It Returns**:
- List of all documents
- Document ID
- Document name
- File size
- Creation date
- Metadata

**Example Claude Prompt**:
```
What documents do I have in my knowledge base?
```

---

## Example Workflow

### Step 1: Find relevant information
```
"Search my knowledge base for Python programming tips"
```
Claude calls: `search_notes(query="Python programming tips", top_k=5)`

Result: Finds 3 relevant documents with scores like 0.92, 0.87, 0.81

### Step 2: Get full document
```
"Show me the full content of document ID 1"
```
Claude calls: `get_document(document_id="1")`

Result: Complete document content displayed

### Step 3: List all sources
```
"What else is available in my knowledge base?"
```
Claude calls: `list_sources()`

Result: All documents listed with metadata

---

## Error Handling

If you get an error:

| Error | Cause | Solution |
|-------|-------|----------|
| "Query cannot be empty" | Empty search query | Try with actual search terms |
| "No results found" | No matches for query | Try broader terms or different keywords |
| "Document not found" | Invalid document ID | Check ID from search results or list_sources |
| "Failed to connect to Qdrant" | Database unavailable | Ensure Qdrant is running |
| "Invalid input" | Parameter format wrong | Check parameter types and values |

---

## Tips & Tricks

### Get Better Search Results
- Use specific keywords: "machine learning" vs "stuff"
- Try multiple variations if first search doesn't help
- Use the top_k parameter to get more options

### Find Documents Quickly
- First use `list_sources()` to see what's available
- Then use `search_notes()` to find specific info
- Finally use `get_document()` to read the full text

### Preserve Citations
- The similarity score indicates how relevant the result is
- Document names and IDs are preserved in responses
- Use get_document() to cite complete sources

### Multi-step Queries
Claude can chain tools together:
```
"Search for 'climate change', then get the first result 
and summarize the key points for me"
```

---

## Key Characteristics

### Search Accuracy
- Higher similarity scores (0.80+) = very relevant
- Medium scores (0.60-0.80) = somewhat relevant  
- Lower scores (<0.60) = barely relevant

### Result Limits
- Minimum top_k: 1 (get just the best match)
- Maximum top_k: 50 (get many results)
- Default: 5 (good balance)

### Data Preserved
- ✅ Similarity scores maintained
- ✅ Document names preserved
- ✅ Page numbers included
- ✅ Document IDs consistent
- ✅ Metadata included

---

## Environment Variables

These affect how the tools work (set in .env):

```env
QDRANT_HOST=localhost        # Where Qdrant is running
QDRANT_PORT=6333             # Port number
QDRANT_COLLECTION_NAME=knowledge_base  # Collection to search
```

---

## Troubleshooting Quick Guide

**Tools don't appear in Claude?**
- Restart Claude Desktop after config changes
- Check .env file is configured correctly
- Verify MCP server is running: `python -m server.main`

**Search returns no results?**
- Initialize sample data: `python scripts/init_qdrant.py`
- Check documents are in Qdrant: `python scripts/test_tools.py`
- Try broader search terms

**Get "Document not found"?**
- First run `list_sources()` to see available documents
- Copy exact ID from list and use in `get_document()`
- IDs must match exactly

**MCP server won't start?**
- Check Python version: `python --version` (need 3.11+)
- Verify Qdrant is running: `curl http://localhost:6333/health`
- Install dependencies: `pip install -r requirements.txt`

---

## Next Steps

1. ✅ **Set up project** - Read SETUP.md
2. ✅ **Configure Claude Desktop** - Follow CLAUDE_INTEGRATION.md
3. ✅ **Test the tools** - Run `python scripts/test_tools.py`
4. ✅ **Use in Claude** - Start asking questions!

---

## Support Resources

- **Installation issues**: See SETUP.md
- **Claude Desktop setup**: See CLAUDE_INTEGRATION.md
- **Direct testing**: Run `python scripts/test_tools.py`
- **Full documentation**: See README.md
- **Task progress**: See TASK_TRACKING.md

---

**Version**: 1.0.0  
**Last Updated**: 2026-08-18  
**Status**: Ready for Production ✅
