import requests
import json

class CrewAIClient:
    def __init__(self, base_url="http://127.0.0.1:5050"):
        self.base_url = base_url

    def _send_request(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            error_message = f"Connection Error: Could not connect to CrewAI API server at {url}. Is the server running?"
            return {"error_message": error_message, "processed_with_crewai": False}
        except requests.exceptions.Timeout as e:
            error_message = f"Timeout Error: Request to CrewAI API server at {url} timed out."
            return {"error_message": error_message, "processed_with_crewai": False}
        except requests.exceptions.RequestException as e:
            error_message = f"Request Error: An error occurred during the request to {url}: {e}"
            return {"error_message": error_message, "processed_with_crewai": False}
        except json.JSONDecodeError:
            error_message = f"JSON Decode Error: Invalid JSON response from server: {response.text}"
            return {"error_message": error_message, "processed_with_crewai": False}

    def analyze_request(self, message: str):
        data = {"message": message}
        return self._send_request("api/analyze", data)

    def process_request(self, message: str):
        data = {"message": message}
        return self._send_request("api/process", data)

    def health_check(self):
        url = f"{self.base_url}/api/health"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error_message": f"Health Check Error: Could not connect to CrewAI API server at {url}: {e}", "processed_with_crewai": False}

    def is_available(self):
        """Check if CrewAI API server is available"""
        try:
            health_status = self.health_check()
            # Check if it's an error response (has error_message) or successful
            return "error_message" not in health_status
        except Exception:
            return False

    def index_docs(self):
        # This endpoint might not be available if txtai is not installed on the CrewAI server
        # or if the smart_delegator doesn't expose it.
        # It's good to have it here for completeness if it becomes available.
        data = {}
        return self._send_request("api/index_docs", data)

if __name__ == "__main__":
    # Пример использования клиента
    client = CrewAIClient()

    print("Performing health check...")
    health_status = client.health_check()
    print(f"Health Status: {health_status}")

    if health_status.get("status") == "online":
        print("\nAnalyzing a request...")
        analysis_result = client.analyze_request("Расскажи мне о последних новостях в области ИИ.")
        print(f"Analysis Result: {analysis_result}")

        print("\nProcessing a request...")
        process_result = client.process_request("Напиши короткий отчет о влиянии ИИ на рынок труда.")
        print(f"Process Result: {process_result}")
    else:
        print("\nCrewAI API server is not online. Please start it manually.")
        print(r"Example: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\crewai_env\Scripts\python.exe C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\crewai_api_server.py")
