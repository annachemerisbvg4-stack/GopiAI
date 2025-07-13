"""Minimal test script for RAG system."""
import os
from rag_system import get_rag_system, RAGSystem
from rag_config import get_rag_config

def test_minimal_rag():
    """Test minimal RAG functionality."""
    # Get configuration
    config = get_rag_config()
    
    # Print config for verification
    print("\n[CONFIG]")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Get RAG system instance
    print("\n[INIT] Getting RAG system instance...")
    rag = get_rag_system()
    
    # Test document
    doc_id = "test_doc_1"
    text = "GopiAI is an advanced AI assistant that can help with various tasks."
    metadata = {"type": "test", "source": "minimal_test"}
    
    # Index document
    print(f"\n[INDEX] Adding document: {doc_id}")
    success = rag.index_document(text, doc_id, metadata)
    print(f"  Indexing {'succeeded' if success else 'failed'}")
    
    # Verify document exists
    print("\n[VERIFY] Checking document in index...")
    try:
        if hasattr(rag.embeddings, 'get'):
            doc = rag.embeddings.get(doc_id)
            print(f"  Document retrieved: {bool(doc)}")
            if doc:
                print(f"  Content: {doc}")
        
        # List all documents in index
        if hasattr(rag.embeddings, 'search'):
            print("\n[SEARCH] Listing all documents:")
            results = rag.embeddings.search("select id, text, metadata from txtai")
            print(f"  Found {len(results)} documents:")
            for i, doc in enumerate(results, 1):
                print(f"  {i}. ID: {doc.get('id')}")
                print(f"     Text: {doc.get('text', '')[:60]}...")
                print(f"     Metadata: {doc.get('metadata', {})}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Search for the document
    print("\n[SEARCH] Searching for 'AI assistant':")
    results = rag.search("AI assistant")
    print(f"  Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. ID: {result['id']}")
        print(f"     Score: {result['score']:.3f}")
        print(f"     Text: {result['text'][:60]}...")
        print(f"     Metadata: {result['metadata']}")

if __name__ == "__main__":
    test_minimal_rag()
