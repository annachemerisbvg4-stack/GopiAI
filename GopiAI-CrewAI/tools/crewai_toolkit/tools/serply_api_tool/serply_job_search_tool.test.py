import os
import unittest
from unittest.mock import patch, MagicMock

from crewai_tools.tools.serply_job_search.serply_job_search import (
    SerplyJobSearchTool,
)


class SerplyJobSearchToolTest(unittest.TestCase):
    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_search_query(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobs": [
                {
                    "position": "Software Engineer",
                    "employer": "Google",
                    "location": "Mountain View, CA",
                    "link": "https://example.com",
                    "highlights": ["Python", "Java"],
                    "is_remote": True,
                    "is_hybrid": False,
                }
            ]
        }
        mock_request.return_value = mock_response

        tool = SerplyJobSearchTool()
        result = tool._run(search_query="Software Engineer Google")

        self.assertIn("Software Engineer", result)
        self.assertIn("Google", result)
        self.assertIn("https://example.com", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_query(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobs": [
                {
                    "position": "Data Scientist",
                    "employer": "Microsoft",
                    "location": "Redmond, WA",
                    "link": "https://example2.com",
                    "highlights": ["ML", "AI"],
                    "is_remote": False,
                    "is_hybrid": True,
                }
            ]
        }
        mock_request.return_value = mock_response

        tool = SerplyJobSearchTool()
        result = tool._run(query="Data Scientist Microsoft")

        self.assertIn("Data Scientist", result)
        self.assertIn("Microsoft", result)
        self.assertIn("https://example2.com", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_no_jobs(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"jobs": []}
        mock_request.return_value = mock_response

        tool = SerplyJobSearchTool()
        result = tool._run(search_query="Unicorn Wrangler")

        self.assertEqual("\nSearch results: \n", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_missing_keys(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobs": [{"position": "Software Engineer", "employer": "Google"}]
        }
        mock_request.return_value = mock_response

        tool = SerplyJobSearchTool()
        result = tool._run(search_query="Software Engineer Google")

        self.assertIn("Software Engineer", result)
        self.assertIn("Google", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    def test_init(self):
        tool = SerplyJobSearchTool()
        self.assertEqual(tool.headers["X-API-KEY"], "test_api_key")
        self.assertEqual(tool.headers["User-Agent"], "crew-tools")
        self.assertEqual(tool.headers["X-Proxy-Location"], "US")