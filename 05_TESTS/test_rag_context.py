#!/usr/bin/env python3
"""
Test script for the get_rag_context function.

This script tests the RAG context retrieval helper function that was
implemented in GopiAI-App/gopiai/app/utils/common.py
"""

import sys
import os

# Add the GopiAI-App module to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'GopiAI-App'))

try:
    from gopiai.app.utils.common import get_rag_context
    print("✅ Successfully imported get_rag_context function")
    
    # Test with a simple query
    print("\n🔍 Testing RAG context retrieval...")
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
        
    # Test with different parameters
    print("\n🔍 Testing with different max_results...")
    context2 = get_rag_context("Python programming", max_results=1)
    print(f"📊 Context with max_results=1: {len(context2) if context2 else 0} characters")
    
    print("\n✅ RAG context function test completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this from the correct directory")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
