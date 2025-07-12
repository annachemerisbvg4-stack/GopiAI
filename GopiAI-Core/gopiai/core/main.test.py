import unittest
from unittest.mock import patch, MagicMock
import sys
import os

class TestGopiAI(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args', return_value=MagicMock(debug=True, no_browser=False, no_extensions=False))
    @patch('gopiai.core.logging.get_logger')
    def test_setup_logging(self, mock_get_logger, mock_parse_args):
        import logging
        from main import setup_logging
        logger = setup_logging(debug=True)
        self.assertEqual(logging.DEBUG, logging.getLogger().getEffectiveLevel())

    @patch('PySide6.QtWidgets.QApplication', return_value=MagicMock())
    def test_setup_application(self, mock_qapplication):
        from main import setup_application
        app = setup_application()
        self.assertIsNotNone(app)

    @patch('os.path.exists', return_value=False)
    @patch('gopiai.core.logging.get_logger')
    def test_apply_theme_safely_no_theme(self, mock_get_logger, mock_exists):
        from main import apply_theme_safely
        app = MagicMock()
        apply_theme_safely(app)
        mock_get_logger.return_value.logger.warning.assert_called()

    @patch('gopiai.widgets.core.icon_adapter.IconAdapter')
    @patch('PySide6.QtWidgets.QApplication', return_value=MagicMock())
    def test_setup_icons(self, mock_qapplication, mock_icon_adapter):
        from main import setup_icons
        app = mock_qapplication.return_value
        setup_icons(app)
        self.assertTrue(app.setWindowIcon.called)

    @patch('argparse.ArgumentParser.parse_args', return_value=MagicMock(debug=False, no_browser=False, no_extensions=False))
    @patch('gopiai.core.logging.get_logger')
    @patch('main.setup_application', return_value=MagicMock())
    @patch('main.apply_theme_safely')
    @patch('main.setup_icons')
    @patch('gopiai.core.minimal_app.FramelessMainWindow', return_value=MagicMock())
    @patch('gopiai.extensions.init_all_extensions')
    def test_main_success(self, mock_init_extensions, mock_frameless_main_window, mock_setup_icons, mock_apply_theme, mock_setup_application, mock_get_logger, mock_parse_args):
        from main import main
        with patch('sys.exit') as mock_sys_exit:
            main()
            self.assertTrue(mock_sys_exit.called)

if __name__ == '__main__':
    unittest.main()