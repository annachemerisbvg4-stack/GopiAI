import unittest
from gopiai.exceptions import (
    GopiAIException,
    TokenLimitExceeded,
    AgentError,
    ToolError,
    ConfigError,
    APIError,
    AuthenticationError
)

class TestExceptions(unittest.TestCase):

    def test_gopiai_exception(self):
        with self.assertRaises(GopiAIException):
            raise GopiAIException

    def test_token_limit_exceeded(self):
        with self.assertRaises(TokenLimitExceeded):
            raise TokenLimitExceeded

    def test_agent_error(self):
        with self.assertRaises(AgentError):
            raise AgentError

    def test_config_error(self):
        with self.assertRaises(ConfigError):
            raise ConfigError

    def test_api_error(self):
        with self.assertRaises(APIError):
            raise APIError

if __name__ == '__main__':
    unittest.main()