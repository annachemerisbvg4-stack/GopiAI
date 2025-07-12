import unittest
import logging
from unittest.mock import patch, mock_open
from io import StringIO
import sys
from gopiai_logger import GopiAILogger, get_gopiai_logger, debug, info, warning, error, critical

class TestGopiAILogger(unittest.TestCase):

    def test_singleton_instance(self):
        logger1 = GopiAILogger()
        logger2 = GopiAILogger()
        self.assertIs(logger1, logger2)

    @patch('logging.Logger.addHandler')
    @patch('pathlib.Path.mkdir')
    @patch('datetime.datetime')
    def test_setup_logger(self, mock_datetime, mock_mkdir, mock_addHandler):
        mock_datetime.now.return_value.strftime.return_value = "test_time"
        logger = GopiAILogger()
        logger._setup_logger()
        mock_mkdir.assert_called_once()
        self.assertEqual(len(logger._logger.handlers), 2)

    @patch('gopiai_logger.GopiAILogger.info')
    def test_global_info(self, mock_info):
        info("test message")
        mock_info.assert_called_with("test message")

    def test_get_logger(self):
        logger = get_gopiai_logger()
        self.assertIsInstance(logger, GopiAILogger)