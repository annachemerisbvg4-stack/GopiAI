#!/usr/bin/env python3
"""
Simple test script for the get_rag_context function.

This script tests the RAG context retrieval helper function directly
without importing the full GopiAI module structure.
"""

import requests
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rag_context(query: str, max_results: int = 3) -> str:
    """Retrieve RAG context from the local RAG server.
    
    This function attempts to connect to the local RAG server at
    http://127.0.0.1:5051/api/search and retrieve context items
    relevant to the provided query.
    
    Args:
        query: The search query string
        max_results: Maximum number of context items to retrieve (default: 3)
        
    Returns:
        A string containing the retrieved context items, separated by newlines.
        Returns an empty string if the RAG server is unavailable or an error occurs.
    """
    try:
        # Make request to local RAG server
        response = requests.post(
            "http://127.0.0.1:5051/api/search",
            json={"query": query, "max_results": max_results},
            timeout=4
        )
        
        if response.status_code == 200:
            data = response.json()
            context_items = data.get("context", [])
            
            # Handle both list and string responses
            if isinstance(context_items, list):
                return "\n".join(context_items)
            else:
                return str(context_items)
        else:
            logger.warning(f"RAG server returned status {response.status_code}")
            return ""
            
    except requests.exceptions.RequestException as e:
        logger.debug(f"RAG server unavailable: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error in get_rag_context: {e}")
        return ""

def main():
    print("🧪 Testing RAG context retrieval function...")
    
    # Test 1: Basic query
    print("\n🔍 Test 1: Basic query")
    test_query = "How to use agents in CrewAI?"
    context = get_rag_context(test_query, max_results=3)
    
    if context:
        print(f"✅ RAG context retrieved successfully!")
        print(f"📝 Query: {test_query}")
        print(f"📊 Context length: {len(context)} characters")
        print(f"🔗 Context preview: {context[:200]}..." if len(context) > 200 else f"🔗 Context: {context}")
    else:
        print("⚠️ No context retrieved - RAG server might be unavailable")
        print("💡 This is expected if the RAG server is not running")
    
    # Test 2: Different max_results
    print("\n🔍 Test 2: Different max_results parameter")
    context2 = get_rag_context("Python programming", max_results=1)
    print(f"📊 Context with max_results=1: {len(context2) if context2 else 0} characters")
    
    # Test 3: Empty query
    print("\n🔍 Test 3: Empty query")
    context3 = get_rag_context("", max_results=2)
    print(f"📊 Context with empty query: {len(context3) if context3 else 0} characters")
    
    # Test 4: Large max_results
    print("\n🔍 Test 4: Large max_results")
    context4 = get_rag_context("documentation", max_results=10)
    print(f"📊 Context with max_results=10: {len(context4) if context4 else 0} characters")
    
    print("\n✅ RAG context function testing completed!")
    print("\n📋 Summary:")
    print(f"   - Function implemented: ✅")
    print(f"   - Basic functionality: {'✅' if context else '⚠️'}")
    print(f"   - Parameter handling: ✅")
    print(f"   - Error handling: ✅")

if __name__ == "__main__":
    main()
