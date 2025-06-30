#!/usr/bin/env python3
"""
Manual Test Script for RAG and CrewAI Integration

Test matrix:  
| RAG | CrewAI | Expected |  
| --- | --- | --- |  
| off | on  | Fast response (≤15 s), no freeze |  
| on  | on  | Response with RAG context, no freeze |  
| off | off | Graceful fallback, UI warns, no freeze |  

Run this script manually after setting up services as needed.
"""

import sys
import os
import time
import requests
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "GopiAI-UI"))
sys.path.insert(0, str(project_root / "GopiAI-CrewAI"))

# Test configuration
CREWAI_SERVER_URL = "http://127.0.0.1:5050"
RAG_SERVER_URL = "http://127.0.0.1:5051"

def check_service_status():
    """Check current status of services"""
    print("🔍 Checking Service Status")
    print("=" * 50)
    
    # Check CrewAI
    try:
        response = requests.get(f"{CREWAI_SERVER_URL}/api/health", timeout=3)
        crewai_status = response.status_code == 200
        print(f"CrewAI (port 5050): {'✅ Running' if crewai_status else '❌ Not running'}")
    except requests.RequestException:
        crewai_status = False
        print(f"CrewAI (port 5050): ❌ Not running")
    
    # Check RAG
    try:
        response = requests.get(f"{RAG_SERVER_URL}/api/health", timeout=3)
        rag_status = response.status_code == 200
        print(f"RAG (port 5051): {'✅ Running' if rag_status else '❌ Not running'}")
    except requests.RequestException:
        rag_status = False
        print(f"RAG (port 5051): ❌ Not running")
    
    return {"crewai": crewai_status, "rag": rag_status}

def test_prompt(prompt, prompt_name="Test", timeout=20):
    """Test a single prompt and measure response time"""
    print(f"\n🧪 Testing: {prompt_name}")
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Try to use CrewAI client first
        try:
            from gopiai.ui.components.crewai_client import CrewAIClient
            client = CrewAIClient()
            response = client.process_request(prompt, timeout=timeout)
        except ImportError:
            # Fallback to direct API call
            response = requests.post(
                f"{CREWAI_SERVER_URL}/api/process",
                json={"message": prompt},
                timeout=timeout
            )
            if response.status_code == 200:
                response = response.json()
            else:
                response = {"error": f"HTTP {response.status_code}: {response.text}"}
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Analyze response
        print(f"⏱️ Response time: {response_time:.1f}s")
        
        if response_time > timeout:
            print("❌ FREEZE DETECTED: Response took too long!")
            return False
        elif response_time <= 15:
            print("✅ Fast response (≤15s)")
        else:
            print("⚠️ Slow response (>15s)")
        
        # Check response content
        if isinstance(response, dict):
            if "error" in response or "error_message" in response:
                error_msg = response.get("error_message", response.get("error", "Unknown error"))
                print(f"❌ Error response: {error_msg}")
                if "unavailable" in error_msg.lower() or "not found" in error_msg.lower():
                    print("✅ Graceful fallback detected")
                return False
            elif "response" in response:
                print(f"✅ Valid response received: {response['response'][:200]}...")
                if response.get("processed_with_crewai", False):
                    print("✅ Processed with CrewAI")
                return True
        elif isinstance(response, str):
            print(f"✅ String response received: {response[:200]}...")
            return True
        else:
            print(f"❌ Unexpected response type: {type(response)}")
            return False
            
    except requests.Timeout:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"❌ TIMEOUT after {response_time:.1f}s")
        return False
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"❌ Exception after {response_time:.1f}s: {e}")
        return False

def run_test_scenario(scenario_name):
    """Run a specific test scenario"""
    print(f"\n{'='*70}")
    print(f"🎯 TESTING SCENARIO: {scenario_name}")
    print(f"{'='*70}")
    
    # Check current service status
    status = check_service_status()
    current_config = f"RAG: {'ON' if status['rag'] else 'OFF'}, CrewAI: {'ON' if status['crewai'] else 'OFF'}"
    print(f"\nCurrent Configuration: {current_config}")
    
    # Test prompts
    short_prompts = [
        ("What is Python?", "Short Prompt 1"),
        ("Hello, how are you?", "Short Prompt 2")
    ]
    
    long_prompts = [
        ("""Please provide a comprehensive analysis of machine learning algorithms, 
        including their applications, strengths, and weaknesses. Compare supervised 
        learning, unsupervised learning, and reinforcement learning approaches. 
        Discuss recent advances in deep learning and their impact on various industries.""", 
        "Long Prompt 1")
    ]
    
    results = []
    
    # Test short prompts
    for prompt, name in short_prompts:
        result = test_prompt(prompt, name)
        results.append((name, result))
    
    # Test long prompts
    for prompt, name in long_prompts:
        result = test_prompt(prompt, name)
        results.append((name, result))
    
    # Summary
    print(f"\n📊 SCENARIO RESULTS: {scenario_name}")
    print("-" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {name}")
    
    print(f"\nPassed: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    return passed == total

def main():
    """Main manual test function"""
    print("🧪 Manual RAG and CrewAI Test Script")
    print("=" * 70)
    print("\nThis script will test the current configuration of RAG and CrewAI services.")
    print("Make sure to start/stop services manually as needed for each test scenario.")
    print("\nTest Matrix:")
    print("| RAG | CrewAI | Expected |")
    print("| --- | --- | --- |")
    print("| off | on  | Fast response (≤15 s), no freeze |")
    print("| on  | on  | Response with RAG context, no freeze |")
    print("| off | off | Graceful fallback, UI warns, no freeze |")
    
    while True:
        print(f"\n{'='*70}")
        print("MANUAL TEST MENU")
        print("=" * 70)
        print("1. Check Service Status")
        print("2. Test Current Configuration")
        print("3. Instructions for Service Control")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            check_service_status()
            
        elif choice == "2":
            status = check_service_status()
            scenario = f"RAG_{'ON' if status['rag'] else 'OFF'}_CrewAI_{'ON' if status['crewai'] else 'OFF'}"
            run_test_scenario(scenario)
            
        elif choice == "3":
            print("\n📋 SERVICE CONTROL INSTRUCTIONS")
            print("=" * 50)
            print("\n🚀 To Start CrewAI:")
            print("   1. Open terminal in GopiAI-CrewAI folder")
            print("   2. Run: run_crewai_api_server.bat")
            print("   3. Wait for server to start on port 5050")
            
            print("\n🚀 To Start RAG:")
            print("   1. Open terminal in rag_memory_system folder")
            print("   2. Run: python -m txtai.api --port 5051")
            print("   3. Wait for server to start on port 5051")
            
            print("\n🛑 To Stop Services:")
            print("   1. Press Ctrl+C in the respective terminal")
            print("   2. Or close the terminal window")
            
            print("\n🧪 Test Scenarios to Run:")
            print("   1. Start only CrewAI → Test (RAG off, CrewAI on)")
            print("   2. Start both services → Test (RAG on, CrewAI on)")
            print("   3. Stop both services → Test (RAG off, CrewAI off)")
            
        elif choice == "4":
            print("\n👋 Exiting manual test script")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
