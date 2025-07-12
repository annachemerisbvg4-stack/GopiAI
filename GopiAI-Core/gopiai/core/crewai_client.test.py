import unittest
from unittest.mock import patch, MagicMock
from crewai_client import CrewAIClient
import requests
import json

class TestCrewAIClient(unittest.TestCase):

    @patch('requests.post')
    def test_analyze_request_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "analysis_result"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = CrewAIClient()
        result = client.analyze_request("test message")
        self.assertEqual(result, {"result": "analysis_result"})

    @patch('requests.post')
    def test_analyze_request_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        client = CrewAIClient()
        result = client.analyze_request("test message")
        self.assertIn("Connection Error", result["error_message"])
        self.assertFalse(result["processed_with_crewai"])

    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "online"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = CrewAIClient()
        result = client.health_check()
        self.assertEqual(result, {"status": "online"})

    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        client = CrewAIClient()
        result = client.health_check()
        self.assertIn("Health Check Error", result["error_message"])
        self.assertFalse(result["processed_with_crewai"])

    @patch('crewai_client.CrewAIClient.health_check')
    def test_is_available(self, mock_health_check):
        mock_health_check.return_value = {"status": "online"}
        client = CrewAIClient()
        self.assertTrue(client.is_available())

if __name__ == '__main__':
    unittest.main()