import unittest
from unittest.mock import MagicMock
from ReflectionEnabledAIRouter import ReflectionEnabledAIRouter


class TestReflectionEnabledAIRouter(unittest.TestCase):

    def setUp(self):
        self.mock_ai_router = MagicMock()
        self.router = ReflectionEnabledAIRouter(self.mock_ai_router)

    def test_initialization(self):
        self.assertIsNotNone(self.router.reflection_config)
        self.assertIsNotNone(self.router.reflection_stats)

    def test_generate_initial_response(self):
        self.mock_ai_router._generate.return_value.generations = [[MagicMock(text="Test Response")]]
        response = self.router._generate_initial_response("Test Prompt")
        self.assertEqual(response, "Test Response")

    def test_fallback_quality_assessment(self):
        prompt = "Test Prompt"
        response = "This is a test response."
        quality = self.router._fallback_quality_assessment(prompt, response)
        self.assertIsInstance(quality, float)
        self.assertTrue(0.0 <= quality <= 10.0)

    def test_set_reflection_enabled(self):
        self.router.set_reflection_enabled(False)
        self.assertFalse(self.router.enable_reflection)
        self.router.set_reflection_enabled(True)
        self.assertTrue(self.router.enable_reflection)

    def test_update_reflection_config(self):
        new_config = {'min_quality_threshold': 9.0}
        self.router.update_reflection_config(new_config)
        self.assertEqual(self.router.reflection_config['min_quality_threshold'], 9.0)

if __name__ == '__main__':
    unittest.main()