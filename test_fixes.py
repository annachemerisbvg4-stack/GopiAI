#!/usr/bin/env python3
"""
Test script to verify the fixes for GopiAI issues:
1. OpenRouter API key loading
2. EmotionalClassifier initialization
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_api_key():
    """Test if OpenRouter API key is loaded correctly"""
    print("=== Testing OpenRouter API Key ===")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        print(f"✅ OPENROUTER_API_KEY found: {api_key[:10]}...")
        print(f"   Full length: {len(api_key)} characters")
        
        # Check if it has the correct format
        if api_key.startswith('sk-or-v1-'):
            print("✅ API key has correct format")
        else:
            print("❌ API key format seems incorrect")
    else:
        print("❌ OPENROUTER_API_KEY not found")
    
    return api_key is not None

def test_emotional_classifier():
    """Test EmotionalClassifier initialization with AI Router"""
    print("\n=== Testing EmotionalClassifier ===")
    
    try:
        # Add the path to gopiai_integration
        project_root = os.path.dirname(os.path.abspath(__file__))
        gopiai_integration_path = os.path.join(project_root, 'GopiAI-CrewAI', 'tools', 'gopiai_integration')
        sys.path.insert(0, gopiai_integration_path)
        
        # Import required modules directly from files
        from ai_router_llm import AIRouterLLM
        from emotional_classifier import EmotionalClassifier
        
        print("✅ Successfully imported AIRouterLLM and EmotionalClassifier")
        
        # Create AI Router
        ai_router = AIRouterLLM()
        print("✅ AIRouterLLM initialized successfully")
        
        # Create EmotionalClassifier with AI Router
        classifier = EmotionalClassifier(ai_router)
        print("✅ EmotionalClassifier initialized successfully with AI Router")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"   Current sys.path includes: {gopiai_integration_path}")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_openrouter_client():
    """Test OpenRouter client functionality"""
    print("\n=== Testing OpenRouter Client ===")
    
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        gopiai_integration_path = os.path.join(project_root, 'GopiAI-CrewAI', 'tools', 'gopiai_integration')
        sys.path.insert(0, gopiai_integration_path)
        
        from openrouter_client import OpenRouterClient
        
        client = OpenRouterClient()
        print("✅ OpenRouterClient initialized")
        
        # Test connection
        if client.test_connection():
            print("✅ OpenRouter connection test passed")
            return True
        else:
            print("❌ OpenRouter connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ OpenRouter client error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing GopiAI Fixes\n")
    
    results = []
    
    # Test 1: API Key
    results.append(test_openrouter_api_key())
    
    # Test 2: EmotionalClassifier
    results.append(test_emotional_classifier())
    
    # Test 3: OpenRouter Client
    results.append(test_openrouter_client())
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! The fixes should work correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()