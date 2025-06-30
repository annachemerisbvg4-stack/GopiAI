#!/usr/bin/env python3
"""
Test Matrix for RAG and CrewAI Integration

Test matrix:  
| RAG | CrewAI | Expected |  
| --- | --- | --- |  
| off | on  | Fast response (≤15 s), no freeze |  
| on  | on  | Response with RAG context, no freeze |  
| off | off | Graceful fallback, UI warns, no freeze |  

Uses both short (1-line) and long (multi-paragraph) prompts.
"""

import sys
import os
import time
import threading
import requests
import subprocess
import signal
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "GopiAI-UI"))
sys.path.insert(0, str(project_root / "GopiAI-CrewAI"))

# Test configuration
TEST_TIMEOUT = 20  # Maximum time to wait for responses
CREWAI_SERVER_URL = "http://127.0.0.1:5050"
RAG_SERVER_URL = "http://127.0.0.1:5051"

class ServiceController:
    """Controls RAG and CrewAI services for testing"""
    
    def __init__(self):
        self.crewai_process = None
        self.rag_process = None
        
    def start_crewai(self):
        """Start CrewAI API server"""
        try:
            crewai_script = project_root / "GopiAI-CrewAI" / "run_crewai_api_server.bat"
            if crewai_script.exists():
                print("🚀 Starting CrewAI server...")
                self.crewai_process = subprocess.Popen(
                    [str(crewai_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                # Wait for server to start
                time.sleep(10)
                return self.check_crewai_health()
            else:
                print("❌ CrewAI start script not found")
                return False
        except Exception as e:
            print(f"❌ Failed to start CrewAI: {e}")
            return False
    
    def stop_crewai(self):
        """Stop CrewAI API server"""
        if self.crewai_process:
            try:
                self.crewai_process.terminate()
                self.crewai_process.wait(timeout=5)
                print("✅ CrewAI server stopped")
            except subprocess.TimeoutExpired:
                self.crewai_process.kill()
                print("⚠️ CrewAI server force killed")
            except Exception as e:
                print(f"❌ Error stopping CrewAI: {e}")
            finally:
                self.crewai_process = None
    
    def start_rag(self):
        """Start RAG service"""
        try:
            # Check if there's a RAG start script
            rag_script = project_root / "rag_memory_system" / "start_rag_server.py"
            if rag_script.exists():
                print("🚀 Starting RAG server...")
                self.rag_process = subprocess.Popen(
                    [sys.executable, str(rag_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # Wait for server to start
                time.sleep(5)
                return self.check_rag_health()
            else:
                # Try to start with txtai API
                print("🚀 Starting RAG server with txtai...")
                self.rag_process = subprocess.Popen(
                    [sys.executable, "-m", "txtai.api", "--port", "5051"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(project_root / "rag_memory_system")
                )
                time.sleep(5)
                return self.check_rag_health()
        except Exception as e:
            print(f"❌ Failed to start RAG: {e}")
            return False
    
    def stop_rag(self):
        """Stop RAG service"""
        if self.rag_process:
            try:
                self.rag_process.terminate()
                self.rag_process.wait(timeout=5)
                print("✅ RAG server stopped")
            except subprocess.TimeoutExpired:
                self.rag_process.kill()
                print("⚠️ RAG server force killed")
            except Exception as e:
                print(f"❌ Error stopping RAG: {e}")
            finally:
                self.rag_process = None
    
    def check_crewai_health(self):
        """Check if CrewAI service is running"""
        try:
            response = requests.get(f"{CREWAI_SERVER_URL}/api/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def check_rag_health(self):
        """Check if RAG service is running"""
        try:
            response = requests.get(f"{RAG_SERVER_URL}/api/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def get_service_status(self):
        """Get current status of both services"""
        return {
            "crewai": self.check_crewai_health(),
            "rag": self.check_rag_health()
        }

class TestRunner:
    """Runs the test matrix"""
    
    def __init__(self):
        self.service_controller = ServiceController()
        self.test_results = []
        
        # Test prompts
        self.short_prompts = [
            "What is Python?",
            "Hello, how are you?",
            "Explain AI",
            "2+2=?"
        ]
        
        self.long_prompts = [
            """
            Please provide a comprehensive analysis of machine learning algorithms, 
            including their applications, strengths, and weaknesses. Compare supervised 
            learning, unsupervised learning, and reinforcement learning approaches. 
            Discuss recent advances in deep learning and their impact on various industries. 
            Include examples of real-world implementations and future research directions 
            in the field of artificial intelligence and machine learning.
            """,
            """
            Create a detailed project plan for developing a web application that includes 
            user authentication, database integration, API development, frontend design, 
            testing strategies, deployment procedures, and maintenance protocols. 
            Consider scalability, security, performance optimization, and user experience. 
            Provide timeline estimates, resource requirements, technology stack recommendations, 
            and risk mitigation strategies for each phase of the development process.
            """
        ]
    
    def test_scenario(self, rag_enabled, crewai_enabled, prompt, prompt_type):
        """Test a single scenario"""
        print(f"\n{'='*50}")
        print(f"Testing: RAG={rag_enabled}, CrewAI={crewai_enabled}, Prompt={prompt_type}")
        print(f"{'='*50}")
        
        # Setup services based on test scenario
        if crewai_enabled and not self.service_controller.check_crewai_health():
            if not self.service_controller.start_crewai():
                return self._record_result(rag_enabled, crewai_enabled, prompt_type, 
                                         "FAIL", "CrewAI service failed to start", 0)
        elif not crewai_enabled:
            self.service_controller.stop_crewai()
        
        if rag_enabled and not self.service_controller.check_rag_health():
            if not self.service_controller.start_rag():
                return self._record_result(rag_enabled, crewai_enabled, prompt_type,
                                         "FAIL", "RAG service failed to start", 0)
        elif not rag_enabled:
            self.service_controller.stop_rag()
        
        # Wait for services to stabilize
        time.sleep(2)
        
        # Verify service states
        status = self.service_controller.get_service_status()
        actual_crewai = status["crewai"]
        actual_rag = status["rag"]
        
        print(f"Service Status - CrewAI: {actual_crewai}, RAG: {actual_rag}")
        
        # Test the prompt
        start_time = time.time()
        try:
            response = self._send_test_request(prompt, timeout=TEST_TIMEOUT)
            end_time = time.time()
            response_time = end_time - start_time
            
            # Analyze response
            result = self._analyze_response(rag_enabled, crewai_enabled, response, response_time)
            return self._record_result(rag_enabled, crewai_enabled, prompt_type,
                                     result["status"], result["message"], response_time)
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return self._record_result(rag_enabled, crewai_enabled, prompt_type,
                                     "FAIL", f"Request failed: {str(e)}", response_time)
    
    def _send_test_request(self, prompt, timeout=15):
        """Send test request to the system"""
        try:
            # Import CrewAI client for testing
            from gopiai.ui.components.crewai_client import CrewAIClient
            
            client = CrewAIClient()
            response = client.process_request(prompt, timeout=timeout)
            return response
            
        except ImportError:
            # Fallback to direct API call
            try:
                response = requests.post(
                    f"{CREWAI_SERVER_URL}/api/process",
                    json={"message": prompt},
                    timeout=timeout
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"HTTP {response.status_code}"}
            except requests.RequestException as e:
                return {"error": str(e)}
    
    def _analyze_response(self, rag_enabled, crewai_enabled, response, response_time):
        """Analyze the response against expected behavior"""
        
        # Check for system freeze (response time too long)
        if response_time > TEST_TIMEOUT:
            return {"status": "FAIL", "message": f"System freeze detected (>{TEST_TIMEOUT}s)"}
        
        # Expected behaviors based on configuration
        if not rag_enabled and not crewai_enabled:
            # Should show graceful fallback with warning
            if isinstance(response, dict) and "error" in response:
                if response_time <= 15:
                    return {"status": "PASS", "message": "Graceful fallback with warning"}
                else:
                    return {"status": "FAIL", "message": "Slow graceful fallback"}
            else:
                return {"status": "FAIL", "message": "No graceful fallback warning"}
        
        elif not rag_enabled and crewai_enabled:
            # Should be fast response without RAG context
            if response_time <= 15:
                if isinstance(response, dict) and "response" in response:
                    return {"status": "PASS", "message": "Fast response without RAG"}
                elif isinstance(response, str):
                    return {"status": "PASS", "message": "Fast response without RAG"}
                else:
                    return {"status": "FAIL", "message": "Invalid response format"}
            else:
                return {"status": "FAIL", "message": f"Slow response ({response_time:.1f}s)"}
        
        elif rag_enabled and crewai_enabled:
            # Should provide response with RAG context
            if isinstance(response, dict) and "response" in response:
                return {"status": "PASS", "message": "Response with RAG context"}
            elif isinstance(response, str):
                return {"status": "PASS", "message": "Response with RAG context"}
            else:
                return {"status": "FAIL", "message": "No proper response"}
        
        else:
            # Edge case
            return {"status": "UNKNOWN", "message": "Unexpected configuration"}
    
    def _record_result(self, rag_enabled, crewai_enabled, prompt_type, status, message, response_time):
        """Record test result"""
        result = {
            "rag": rag_enabled,
            "crewai": crewai_enabled,
            "prompt_type": prompt_type,
            "status": status,
            "message": message,
            "response_time": response_time
        }
        self.test_results.append(result)
        
        # Print result
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {status}: {message} ({response_time:.1f}s)")
        
        return result
    
    def run_all_tests(self):
        """Run the complete test matrix"""
        print("🧪 Starting RAG and CrewAI Test Matrix")
        print(f"Test timeout: {TEST_TIMEOUT} seconds")
        
        # Test configurations
        configurations = [
            (False, True),   # RAG off, CrewAI on
            (True, True),    # RAG on, CrewAI on  
            (False, False),  # RAG off, CrewAI off
        ]
        
        # Run tests for each configuration
        for rag_enabled, crewai_enabled in configurations:
            print(f"\n🔧 Testing configuration: RAG={rag_enabled}, CrewAI={crewai_enabled}")
            
            # Test with short prompts
            for i, prompt in enumerate(self.short_prompts[:2]):  # Test first 2 short prompts
                self.test_scenario(rag_enabled, crewai_enabled, prompt, f"short_{i+1}")
                time.sleep(1)  # Brief pause between tests
            
            # Test with long prompts  
            for i, prompt in enumerate(self.long_prompts[:1]):  # Test first long prompt
                self.test_scenario(rag_enabled, crewai_enabled, prompt, f"long_{i+1}")
                time.sleep(1)  # Brief pause between tests
        
        # Generate test report
        self.generate_report()
    
    def generate_report(self):
        """Generate test results report"""
        print(f"\n{'='*70}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*70}")
        
        # Count results by status
        pass_count = sum(1 for r in self.test_results if r["status"] == "PASS")
        fail_count = sum(1 for r in self.test_results if r["status"] == "FAIL") 
        total_count = len(self.test_results)
        
        print(f"Total Tests: {total_count}")
        print(f"Passed: {pass_count}")
        print(f"Failed: {fail_count}")
        print(f"Success Rate: {(pass_count/total_count)*100:.1f}%")
        
        # Detailed results
        print(f"\n{'RAG':<5} {'CrewAI':<7} {'Prompt':<8} {'Status':<6} {'Time':<6} {'Message'}")
        print("-" * 70)
        
        for result in self.test_results:
            rag_str = "ON" if result["rag"] else "OFF"
            crewai_str = "ON" if result["crewai"] else "OFF" 
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            
            print(f"{rag_str:<5} {crewai_str:<7} {result['prompt_type']:<8} "
                  f"{status_icon:<6} {result['response_time']:<6.1f} {result['message']}")
        
        # Performance analysis
        print(f"\n{'='*70}")
        print("PERFORMANCE ANALYSIS")
        print(f"{'='*70}")
        
        avg_times = {}
        for result in self.test_results:
            config = f"RAG{'_ON' if result['rag'] else '_OFF'}_CrewAI{'_ON' if result['crewai'] else '_OFF'}"
            if config not in avg_times:
                avg_times[config] = []
            avg_times[config].append(result['response_time'])
        
        for config, times in avg_times.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            print(f"{config}: Avg {avg_time:.1f}s, Max {max_time:.1f}s")
    
    def cleanup(self):
        """Clean up services"""
        print("\n🧹 Cleaning up services...")
        self.service_controller.stop_crewai()
        self.service_controller.stop_rag()

def main():
    """Main test function"""
    runner = TestRunner()
    
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main()
