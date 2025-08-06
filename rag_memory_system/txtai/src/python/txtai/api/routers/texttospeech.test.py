import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from your_module import router  # Replace your_module

class TestTextToSpeech(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(router)
        self.mock_app = MagicMock()
        self.mock_pipeline = MagicMock(return_value=b"fake audio data")
        self.mock_app.pipeline = self.mock_pipeline
        
        import your_module # Replace your_module
        your_module.application.get = MagicMock(return_value=self.mock_app)

    def test_texttospeech_default(self):
        response = self.client.get("/texttospeech?text=hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"fake audio data")
        self.assertEqual(response.headers["content-disposition"], "attachment;filename=speech.mp3")

    def test_texttospeech_with_speaker(self):
        response = self.client.get("/texttospeech?text=hello&speaker=2")
        self.assertEqual(response.status_code, 200)
        self.mock_pipeline.assert_called_with("texttospeech", "hello", speaker="2", encoding="mp3")

    def test_texttospeech_with_encoding(self):
        response = self.client.get("/texttospeech?text=hello&encoding=wav")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-disposition"], "attachment;filename=speech.wav")
        self.mock_pipeline.assert_called_with("texttospeech", "hello", speaker=None, encoding="wav")

    def test_texttospeech_with_speaker_and_encoding(self):
        response = self.client.get("/texttospeech?text=hello&speaker=3&encoding=ogg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-disposition"], "attachment;filename=speech.ogg")
        self.mock_pipeline.assert_called_with("texttospeech", "hello", speaker="3", encoding="ogg")

    def test_texttospeech_empty_text(self):
        response = self.client.get("/texttospeech?text=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"fake audio data")
        self.mock_pipeline.assert_called_with("texttospeech", "", speaker=None, encoding="mp3")