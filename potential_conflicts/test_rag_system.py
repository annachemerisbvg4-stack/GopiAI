"""
Test script for the RAG system in GopiAI-CrewAI.

This script tests the RAG system by:
1. Initializing the RAG system
2. Adding sample documents
3. Performing test queries
4. Verifying the results
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from rag_system import get_rag_system

def test_document_indexing(rag_system):
    """Test document indexing functionality."""
    print("\n[TEST] Testing document indexing...")
    
    # Test documents with different content and metadata
    test_docs = [
        ("test_doc_1", "GopiAI is an advanced AI assistant.", 
         {"type": "introduction", "source": "test", "category": "ai"}),
        ("test_doc_2", "CrewAI enables multi-agent AI systems.", 
         {"type": "framework", "source": "test", "category": "ai"}),
        ("test_doc_3", "RAG combines retrieval with generation.", 
         {"type": "technology", "source": "test", "category": "ai"}),
        ("test_doc_4", "To start, initialize the RAG system.", 
         {"type": "tutorial", "source": "test", "category": "guide"})
    ]
    
    # Index test documents
    for doc_id, text, metadata in test_docs:
        success = rag_system.index_document(text, doc_id, metadata)
        if success:
            print(f"  [OK] Indexed document: {doc_id}")
        else:
            print(f"  [ERROR] Failed to index document: {doc_id}")
    
    # Verify documents were indexed
    for doc_id, text, _ in test_docs:
        try:
            # Try to retrieve the document
            doc = rag_system.embeddings.document(doc_id) if hasattr(rag_system.embeddings, 'document') else None
            if doc:
                print(f"  [OK] Document found in index: {doc_id}")
                print(f"       Content: {doc.get('text', 'No text')[:60]}...")
            else:
                print(f"  [WARNING] Document not found in index: {doc_id}")
        except Exception as e:
            print(f"  [ERROR] Error retrieving document {doc_id}: {e}")

def test_search_functionality(rag_system):
    """Test search functionality with various queries."""
    print("\n[TEST] Testing search functionality...")
    
    test_queries = [
        ("What is GopiAI?", ["GopiAI", "AI assistant"]),
        ("Tell me about CrewAI", ["CrewAI", "multi-agent"]),
        ("Explain RAG", ["RAG", "retrieval", "generation"]),
        ("How to start", ["initialize", "start", "RAG system"])
    ]
    
    for query, keywords in test_queries:
        print(f"\n[QUERY] '{query}'")
        
        # Perform the search
        results = rag_system.search(query, limit=2)
        
        if not results:
            print("  [WARNING] No results found for query")
            continue
            
        print(f"  Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. [Score: {result['score']:.3f}] ID: {result['id']}")
            print(f"     Text: {result['text'][:100]}...")
            if result['metadata']:
                print(f"     Metadata: {result['metadata']}")
            
            # Check if any keywords are in the result
            found_keywords = [kw for kw in keywords if kw.lower() in result['text'].lower()]
            if found_keywords:
                print(f"     Found keywords: {', '.join(found_keywords)}")

def test_rag_integration(rag_system):
    """Test the full RAG pipeline."""
    print("\n[TEST] Testing RAG integration...")
    
    test_queries = [
        "What is GopiAI?",
        "How does CrewAI work?",
        "Explain RAG system",
        "How to start using the system"
    ]
    
    for query in test_queries:
        print(f"\n[QUERY] '{query}'")
        
        # Get context using the RAG system
        context = rag_system.get_context(query)
        
        # Print the results
        if context and context != "No relevant context found.":
            print(f"[CONTEXT] {context[:200]}...")
        else:
            print("[WARNING] No relevant context found.")
            
            # Try a direct search as fallback
            print("  Trying direct search...")
            results = rag_system.search(query, limit=1)
            if results:
                print(f"  Found document: {results[0]['id']}")
                print(f"  Text: {results[0]['text'][:100]}...")

def test_rag_system():
    """Test the RAG system with sample data."""
    print("[INFO] Starting RAG system test...")
    
    try:
        # Get the RAG system instance
        rag_system = get_rag_system()
        print("[SUCCESS] RAG system initialized successfully")
        
        # Sample documents to add to the RAG system
        sample_docs = [
            {
                "text": "GopiAI is an advanced AI assistant that can help with various tasks.",
                "metadata": {"source": "introduction", "type": "general"}
            },
            {
                "text": "CrewAI is a framework for creating multi-agent AI systems.",
                "metadata": {"source": "crewai_docs", "type": "framework"}
            },
            {
                "text": "The RAG system combines retrieval-augmented generation with large language models.",
                "metadata": {"source": "rag_paper", "type": "technical"}
            },
            {
                "text": "To use the system, first initialize the RAG instance and then add documents.",
                "metadata": {"source": "usage_guide", "type": "tutorial"}
            }
        ]
        
        # Add sample documents to the RAG system
        print("\n[INFO] Adding sample documents...")
        for i, doc in enumerate(sample_docs):
            doc_id = f"doc_{i}"
            rag_system.index_document(
                text=doc["text"],
                doc_id=doc_id,
                metadata=doc["metadata"]
            )
            print(f"  - Added document {doc_id}: {doc['text'][:50]}...")
        
        print("[SUCCESS] Documents indexed successfully")
        
        # Run tests
        test_document_indexing(rag_system)
        test_search_functionality(rag_system)
        test_rag_integration(rag_system)
        
        print("\n[SUCCESS] All RAG system tests completed!")
            
    except Exception as e:
        print(f"[ERROR] Error testing RAG system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_system()
