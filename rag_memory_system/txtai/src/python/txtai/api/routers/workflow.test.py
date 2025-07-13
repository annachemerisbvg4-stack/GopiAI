import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from main import router  # Assuming the code is in main.py
from .. import application


class WorkflowAPITests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(router)
        self.mock_app = MagicMock()
        application.get = MagicMock(return_value=self.mock_app)

    def test_workflow_endpoint_success(self):
        self.mock_app.workflow.return_value = ["processed_element"]
        response = self.client.post("/workflow", json={"name": "test_workflow", "elements": ["element1", "element2"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["processed_element"])
        self.mock_app.workflow.assert_called_once_with("test_workflow", ["element1", "element2"])

    def test_workflow_endpoint_missing_name(self):
        response = self.client.post("/workflow", json={"elements": ["element1"]})
        self.assertEqual(response.status_code, 422)

    def test_workflow_endpoint_missing_elements(self):
        response = self.client.post("/workflow", json={"name": "test_workflow"})
        self.assertEqual(response.status_code, 422)

    def test_workflow_endpoint_empty_elements(self):
        self.mock_app.workflow.return_value = []
        response = self.client.post("/workflow", json={"name": "test_workflow", "elements": []})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.mock_app.workflow.assert_called_once_with("test_workflow", [])