import unittest
from unittest.mock import patch, MagicMock
import os
from crewai.tools import EnvVar
from io import StringIO
import sys

class TestSerpApiBaseTool(unittest.TestCase):

    @patch.dict(os.environ, {"SERPAPI_API_KEY": "test_key"})
    def test_initialization_success(self):
        from crewai.tools.serpapi import SerpApiBaseTool
        tool = SerpApiBaseTool()
        self.assertIsNotNone(tool.client)

    @patch.dict(os.environ, {})
    def test_initialization_missing_api_key(self):
        from crewai.tools.serpapi import SerpApiBaseTool
        with self.assertRaises(ValueError):
            SerpApiBaseTool()

    @patch.dict(os.environ, {"SERPAPI_API_KEY": "test_key"})
    @patch("crewai.tools.serpapi.Client")
    def test_omit_fields_dict(self, MockClient):
        from crewai.tools.serpapi import SerpApiBaseTool
        tool = SerpApiBaseTool()
        data = {"sensitive_info": "value", "other_info": {"nested_sensitive": "value2", "nested_ok": "value3"}}
        omit_patterns = ["sensitive"]
        tool._omit_fields(data, omit_patterns)
        self.assertNotIn("sensitive_info", data)
        self.assertNotIn("nested_sensitive", data["other_info"])
        self.assertIn("nested_ok", data["other_info"])

    @patch.dict(os.environ, {"SERPAPI_API_KEY": "test_key"})
    @patch("crewai.tools.serpapi.Client")
    def test_omit_fields_list(self, MockClient):
        from crewai.tools.serpapi import SerpApiBaseTool
        tool = SerpApiBaseTool()
        data = [{"sensitive_info": "value"}, {"other_info": "ok"}]
        omit_patterns = ["sensitive"]
        tool._omit_fields(data, omit_patterns)
        self.assertNotIn("sensitive_info", data[0])
        self.assertIn("other_info", data[1])

    @patch.dict(os.environ, {"SERPAPI_API_KEY": "test_key"})
    @patch("crewai.tools.serpapi.Client")
    @patch('subprocess.run')
    @patch('click.confirm')
    def test_install_package(self, mock_confirm, mock_run, MockClient):
        from crewai.tools.serpapi import SerpApiBaseTool
        mock_confirm.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        sys.modules['serpapi'] = None
        with self.assertRaises(ImportError) as context:
            SerpApiBaseTool()
        del sys.modules['serpapi']