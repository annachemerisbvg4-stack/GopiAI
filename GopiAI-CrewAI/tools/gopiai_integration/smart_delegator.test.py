import unittest
from unittest.mock import patch, MagicMock
from smart_delegator import SmartDelegator

class TestSmartDelegator(unittest.TestCase):

    def setUp(self):
        self.delegator = SmartDelegator(enable_reflection=False)

    def test_analyze_request_simple(self):
        analysis = self.delegator.analyze_request("What is the capital of France?")
        self.assertLessEqual(analysis['complexity'], 3)
        self.assertFalse(analysis['requires_crewai'])

    def test_analyze_request_complex(self):
        analysis = self.delegator.analyze_request("Develop a comprehensive marketing strategy for a new electric vehicle, including market analysis, target audience identification, and a detailed budget plan.")
        self.assertGreaterEqual(analysis['complexity'], 3)

    @patch('smart_delegator.SmartDelegator._handle_with_ai_router')
    def test_process_request_ai_router(self, mock_ai_router):
        mock_ai_router.return_value = "AI Router Response"
        response = self.delegator.process_request("Simple question")
        self.assertEqual(response, "AI Router Response")

    @patch('smart_delegator.SmartDelegator._handle_with_crewai')
    @patch('smart_delegator.SmartDelegator.analyze_request')
    def test_process_request_crewai(self, mock_analyze, mock_crewai):
        mock_analyze.return_value = {'requires_crewai': True, 'complexity': 4, 'type': 'business'}
        mock_crewai.return_value = "CrewAI Response"
        response = self.delegator.process_request("Complex question needing CrewAI")
        self.assertEqual(response, "CrewAI Response")