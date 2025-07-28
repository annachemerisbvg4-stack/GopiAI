#!/usr/bin/env python3
"""
Simple test script to verify the GopiAI fixes work correctly
Tests the actual application behavior rather than isolated modules
"""

import os
import sys
import requests
import time
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
        if api_key.startswith('sk-or-v1-') and len(api_key) > 20:
            print("✅ API key has correct format")
            return True
        else:
            print("❌ API key format seems incorrect")
            return False
    else:
        print("❌ OPENROUTER_API_KEY not found")
        return False

def test_openrouter_api_direct():
    """Test OpenRouter API directly with the key"""
    print("\n=== Testing OpenRouter API Connection ===")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key available for testing")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test with models endpoint
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ OpenRouter API connection successful")
            data = response.json()
            models_count = len(data.get('data', []))
            print(f"   Found {models_count} models available")
            return True
        elif response.status_code == 401:
            print("❌ OpenRouter API authentication failed (401)")
            print("   This means the API key is invalid or malformed")
            return False
        else:
            print(f"❌ OpenRouter API returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error testing OpenRouter API: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing OpenRouter API: {e}")
        return False

def test_crewai_server():
    """Test if CrewAI server is running and responsive"""
    print("\n=== Testing CrewAI Server ===")
    
    try:
        response = requests.get("http://127.0.0.1:5051/health", timeout=5)
        if response.status_code == 200:
            print("✅ CrewAI server is running and responsive")
            return True
        else:
            print(f"❌ CrewAI server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ CrewAI server is not running or not accessible")
        print("   Please start the server with: python GopiAI-CrewAI/crewai_api_server.py")
        return False
    except Exception as e:
        print(f"❌ Error testing CrewAI server: {e}")
        return False

def test_crewai_api_with_openrouter():
    """Test CrewAI API with OpenRouter model"""
    print("\n=== Testing CrewAI API with OpenRouter ===")
    
    if not test_crewai_server():
        return False
    
    try:
        # Test data similar to what the UI sends
        test_data = {
            "message": "Hello, test message",
            "metadata": {
                "session_id": "test_session",
                "model_provider": "openrouter",
                "model_id": "agentica-org/deepcoder-14b-preview:free",
                "system_prompt": "You are a helpful assistant."
            }
        }
        
        response = requests.post(
            "http://127.0.0.1:5051/api/process",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'pending' and result.get('task_id'):
                print("✅ CrewAI API accepted OpenRouter request")
                print(f"   Task ID: {result['task_id']}")
                
                # Wait a moment and check task status
                time.sleep(2)
                task_response = requests.get(
                    f"http://127.0.0.1:5051/api/task/{result['task_id']}",
                    timeout=10
                )
                
                if task_response.status_code == 200:
                    task_result = task_response.json()
                    if task_result.get('status') == 'completed':
                        response_text = task_result.get('result', {}).get('response', '')
                        if response_text and response_text != 'Пустой ответ':
                            print("✅ OpenRouter model returned proper response")
                            print(f"   Response preview: {response_text[:100]}...")
                            return True
                        else:
                            print("❌ OpenRouter model returned empty response")
                            print("   This suggests the authentication fix didn't work")
                            return False
                    else:
                        print(f"⚠️ Task status: {task_result.get('status')}")
                        if task_result.get('error'):
                            print(f"   Error: {task_result['error']}")
                        return False
                else:
                    print("❌ Failed to check task status")
                    return False
            else:
                print("❌ Unexpected response format from CrewAI API")
                return False
        else:
            print(f"❌ CrewAI API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CrewAI API: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing GopiAI Fixes (Simple Version)\n")
    
    results = []
    
    # Test 1: API Key
    results.append(test_openrouter_api_key())
    
    # Test 2: Direct API Connection
    results.append(test_openrouter_api_direct())
    
    # Test 3: CrewAI Server
    server_running = test_crewai_server()
    results.append(server_running)
    
    # Test 4: Full Integration (only if server is running)
    if server_running:
        results.append(test_crewai_api_with_openrouter())
    else:
        print("\n⚠️ Skipping integration test - server not running")
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! The fixes are working correctly.")
        print("\nNext steps:")
        print("1. Start the UI application")
        print("2. Select an OpenRouter model")
        print("3. Send a test message")
        print("4. Verify you get proper responses instead of 'Пустой ответ'")
    else:
        print("⚠️ Some tests failed. Check the specific errors above.")
        
        if not results[0]:  # API key test failed
            print("\n🔧 Fix: Check your .env files for correct OPENROUTER_API_KEY")
        if not results[1]:  # API connection failed
            print("\n🔧 Fix: Verify your OpenRouter API key is valid")
        if not results[2]:  # Server test failed
            print("\n🔧 Fix: Start the CrewAI server first")

if __name__ == "__main__":
    main()