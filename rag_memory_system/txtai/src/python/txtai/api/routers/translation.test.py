import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.routes import router


class TestTranslationRoutes(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(router)
        self.mock_application = MagicMock()
        self.mock_pipeline = MagicMock()
        self.mock_application.get.return_value = self.mock_application
        self.mock_application.pipeline.return_value = self.mock_pipeline
        router.dependency_overrides = {application.get: lambda: self.mock_application}

    def tearDown(self):
        router.dependency_overrides = {}

    def test_translate_success(self):
        self.mock_pipeline.return_value = "translated text"
        response = self.app.get("/translate?text=hello&target=fr")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "translated text")

    def test_batchtranslate_success(self):
        self.mock_pipeline.return_value = ["translated text1", "translated text2"]
        response = self.app.post("/batchtranslate", json={"texts": ["hello", "world"], "target": "fr"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["translated text1", "translated text2"])

    def test_translate_default_target(self):
        self.mock_pipeline.return_value = "translated text"
        response = self.app.get("/translate?text=hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "translated text")

    def test_batchtranslate_default_target(self):
        self.mock_pipeline.return_value = ["translated text1", "translated text2"]
        response = self.app.post("/batchtranslate", json={"texts": ["hello", "world"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["translated text1", "translated text2"])