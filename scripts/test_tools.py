#!/usr/bin/env python
"""Quick test of MCP server tools (without MCP protocol).

This script allows you to test the retrieval functions directly before
connecting to Claude Desktop.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval import search_notes, get_document, list_sources

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_list_sources():
    """Test list_sources function."""
    print("\n" + "="*60)
    print("TEST: list_sources()")
    print("="*60)
    
    try:
        docs = list_sources()
        print(f"Found {len(docs)} documents:")
        for doc in docs:
            print(f"  - {doc.name} (ID: {doc.id}, Size: {doc.size} bytes)")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_search_notes():
    """Test search_notes function."""
    print("\n" + "="*60)
    print("TEST: search_notes()")
    print("="*60)
    
    queries = [
        "Python programming",
        "vector database",
        "machine learning",
    ]
    
    for query in queries:
        try:
            print(f"\nSearching for: {query}")
            results = search_notes(query=query, top_k=3)
            
            if results:
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n  Result {i}:")
                    print(f"    Document: {result.document_name}")
                    print(f"    Score: {result.similarity_score:.2%}")
                    print(f"    Text: {result.relevant_text[:100]}...")
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ERROR: {e}")


def test_get_document():
    """Test get_document function."""
    print("\n" + "="*60)
    print("TEST: get_document()")
    print("="*60)
    
    # Test with valid ID (from sample data)
    try:
        print("\nRetrieving document ID: 1")
        doc = get_document("1")
        print(f"  Name: {doc.name}")
        print(f"  Content: {doc.content[:200]}...")
        print(f"  Metadata: {doc.metadata}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test with invalid ID
    try:
        print("\nRetrieving document ID: 99999 (should fail)")
        doc = get_document("99999")
    except ValueError as e:
        print(f"  EXPECTED ERROR: {e}")
    except RuntimeError as e:
        print(f"  EXPECTED ERROR: {e}")


def test_error_handling():
    """Test error handling."""
    print("\n" + "="*60)
    print("TEST: Error Handling")
    print("="*60)
    
    # Empty query
    try:
        print("\nTesting empty query:")
        search_notes(query="")
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")
    
    # Invalid top_k
    try:
        print("\nTesting invalid top_k:")
        search_notes(query="test", top_k=0)
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")
    
    # Empty document ID
    try:
        print("\nTesting empty document_id:")
        get_document("")
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")


def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# Knowledge-Base MCP Server - Tool Tests")
    print("#"*60)
    
    # Test in order
    test_list_sources()
    test_search_notes()
    test_get_document()
    test_error_handling()
    
    print("\n" + "#"*60)
    print("# Tests Complete")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
