import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from gopiai.ui.main import FallbackThemeManager

#!/usr/bin/env python3
"""
Tests for GopiAI Standalone Interface Main Module
===============================================

Comprehensive test suite for the main GopiAI application window and its components.
Tests cover initialization, UI setup, theme management, and core functionality.

Author: GitHub Copilot
Date: 2025-01-11
"""


# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Mock PySide6 before importing main
with patch.dict('sys.modules', {
    'PySide6': Mock(),
    'PySide6.QtWidgets': Mock(),
    'PySide6.QtCore': Mock(),
    'PySide6.QtGui': Mock(),
    'dotenv': Mock(),
    'qtawesome': Mock(),
    'gopiai.ui.utils.theme_manager': Mock(),
    'gopiai.ui.dialogs.settings_dialog': Mock(),
    'gopiai.ui.components': Mock(),
    'gopiai.ui.memory_initializer': Mock(),
}):
    from gopiai.ui.main import (
        FramelessGopiAIStandaloneWindow,
        main,
        MODULES_LOADED,
        SimpleWidget,
        SimpleMenuBar
    )


class TestEnvironmentSetup:
    """Test environment variable setup and configuration"""
    
    def test_webengine_environment_variables(self):
        """Test that WebEngine environment variables are set correctly"""
        expected_flags = "--disable-gpu --disable-software-rasterizer --disable-3d-apis --disable-accelerated-2d-canvas --no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox --disable-gpu-compositing --disable-webgl --disable-webgl2"
        
        assert os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS") == expected_flags
        assert os.environ.get("QT_OPENGL") == "software"
        assert os.environ.get("QTWEBENGINE_DISABLE_SANDBOX") == "1"

    def test_module_paths_setup(self):
        """Test that module paths are correctly configured"""
        # This test verifies the path setup logic without actual filesystem checks
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gopiai_modules_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        
        expected_paths = [
            os.path.join(gopiai_modules_root, "GopiAI-Core"),
            os.path.join(gopiai_modules_root, "GopiAI-Widgets"),
            os.path.join(gopiai_modules_root, "GopiAI-App"),
            os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
            os.path.join(gopiai_modules_root, "rag_memory_system"),
            gopiai_modules_root,
        ]
        
        # Verify paths are added to sys.path
        for path in expected_paths:
            assert path in sys.path


class TestFallbackComponents:
    """Test fallback components when modules are not loaded"""
    
    def test_simple_widget_initialization(self):
        """Test SimpleWidget fallback component"""
        with patch('gopiai.ui.main.QWidget'), \
             patch('gopiai.ui.main.QVBoxLayout'), \
             patch('gopiai.ui.main.QLabel'), \
             patch('gopiai.ui.main.Signal'):
            
            widget = SimpleWidget("TestWidget")
            assert widget is not None
    
    def test_simple_widget_methods(self):
        """Test SimpleWidget fallback methods"""
        with patch('gopiai.ui.main.QWidget'), \
             patch('gopiai.ui.main.QVBoxLayout'), \
             patch('gopiai.ui.main.QLabel'), \
             patch('gopiai.ui.main.Signal'):
            
            widget = SimpleWidget("TestWidget")
            
            # Test methods don't raise exceptions
            widget.add_new_tab("title", "content")
            assert widget.get_current_text() == "Fallback content"
            widget.set_window(None)
            widget.add_browser_tab()
            widget.open_file_in_tab("test.txt")

    def test_simple_menu_bar(self):
        """Test SimpleMenuBar fallback component"""
        with patch('gopiai.ui.main.QMenuBar'):
            menu_bar = SimpleMenuBar()
            menu_bar.refresh_icons()  # Should not raise exception


class TestFramelessGopiAIStandaloneWindow:
    """Test the main application window"""
    
    @pytest.fixture
    def mock_qt_components(self):
        """Mock Qt components for testing"""
        with patch('gopiai.ui.main.QMainWindow'), \
             patch('gopiai.ui.main.QApplication'), \
             patch('gopiai.ui.main.QWidget'), \
             patch('gopiai.ui.main.QVBoxLayout'), \
             patch('gopiai.ui.main.QSplitter'), \
             patch('gopiai.ui.main.QSizePolicy'), \
             patch('gopiai.ui.main.Qt'), \
             patch('gopiai.ui.main.QKeySequence'), \
             patch('gopiai.ui.main.QShortcut'):
            yield

    @pytest.fixture
    def mock_window_components(self):
        """Mock window-specific components"""
        with patch('gopiai.ui.main.StandaloneTitlebarWithMenu') as mock_titlebar, \
             patch('gopiai.ui.main.FileExplorerWidget') as mock_explorer, \
             patch('gopiai.ui.main.TabDocumentWidget') as mock_tabs, \
             patch('gopiai.ui.main.WebViewChatWidget') as mock_chat, \
             patch('gopiai.ui.main.TerminalWidget') as mock_terminal, \
             patch('gopiai.ui.main.CustomGrip') as mock_grip, \
             patch('gopiai.ui.main.ThemeManager') as mock_theme:
            
            # Setup mock instances
            mock_titlebar_instance = Mock()
            mock_titlebar_instance.menu_bar = Mock()
            mock_titlebar.return_value = mock_titlebar_instance
            
            mock_explorer_instance = Mock()
            mock_explorer_instance.file_double_clicked = Mock()
            mock_explorer_instance.file_selected = Mock()
            mock_explorer.return_value = mock_explorer_instance
            
            mock_tabs_instance = Mock()
            mock_tabs.return_value = mock_tabs_instance
            
            mock_chat_instance = Mock()
            mock_chat.return_value = mock_chat_instance
            
            mock_terminal_instance = Mock()
            mock_terminal.return_value = mock_terminal_instance
            
            mock_theme_instance = Mock()
            mock_theme_instance.apply_theme.return_value = True
            mock_theme.return_value = mock_theme_instance
            
            yield {
                'titlebar': mock_titlebar,
                'explorer': mock_explorer,
                'tabs': mock_tabs,
                'chat': mock_chat,
                'terminal': mock_terminal,
                'grip': mock_grip,
                'theme': mock_theme
            }

    def test_window_initialization(self, mock_qt_components, mock_window_components):
        """Test window initialization"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            assert window.TITLEBAR_HEIGHT == 40
            assert window.GRIP_SIZE == 10
            assert hasattr(window, 'theme_manager')
            assert hasattr(window, 'icon_manager')

    def test_theme_system_initialization(self, mock_qt_components):
        """Test theme system initialization"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon') as mock_qta, \
             patch('gopiai.ui.main.ThemeManager') as mock_theme_manager, \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            mock_theme_instance = Mock()
            mock_theme_instance.apply_theme.return_value = True
            mock_theme_manager.return_value = mock_theme_instance
            
            window = FramelessGopiAIStandaloneWindow()
            
            assert window.theme_manager is not None
            assert window.icon_manager is not None

    def test_theme_system_fallback(self, mock_qt_components):
        """Test theme system fallback when ThemeManager is unavailable"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('gopiai.ui.main.ThemeManager', None), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            assert window.theme_manager is not None
            assert window.theme_manager.current_theme == "default"

    def test_ui_setup(self, mock_qt_components, mock_window_components):
        """Test UI setup process"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Verify UI components are created
            assert hasattr(window, 'titlebar_with_menu')
            assert hasattr(window, 'file_explorer')
            assert hasattr(window, 'tab_document')
            assert hasattr(window, 'chat_widget')
            assert hasattr(window, 'terminal_widget')

    def test_grips_initialization(self, mock_qt_components, mock_window_components):
        """Test window grips initialization"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            expected_directions = [
                "top", "bottom", "left", "right",
                "top-left", "top-right", "bottom-left", "bottom-right"
            ]
            
            assert hasattr(window, 'grips')
            for direction in expected_directions:
                assert direction in window.grips

    def test_menu_signals_connection(self, mock_qt_components, mock_window_components):
        """Test menu signals connection"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Verify menu bar exists and has expected attributes
            menu_bar = getattr(window.titlebar_with_menu, "menu_bar", None)
            assert menu_bar is not None

    def test_panel_shortcuts_setup(self, mock_qt_components, mock_window_components):
        """Test panel shortcuts setup"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()), \
             patch('gopiai.ui.main.QShortcut') as mock_shortcut:
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Verify shortcuts are created
            assert mock_shortcut.call_count >= 4  # At least 4 shortcuts expected

    def test_splitter_behavior_configuration(self, mock_qt_components, mock_window_components):
        """Test splitter behavior configuration"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Test splitter moved handler
            mock_splitter = Mock()
            mock_splitter.sizes.return_value = [100, 200, 300]
            
            with patch.object(window, 'sender', return_value=mock_splitter):
                window._on_splitter_moved(150, 1)  # Should not raise exception

    def test_theme_change_handling(self, mock_qt_components, mock_window_components):
        """Test theme change handling"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            window.theme_manager.apply_theme = Mock(return_value=True)
            
            window.on_change_theme("dark")
            
            window.theme_manager.apply_theme.assert_called_with("dark")

    def test_file_operations(self, mock_qt_components, mock_window_components):
        """Test file operations"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()), \
             patch('gopiai.ui.main.QFileDialog') as mock_dialog, \
             patch('builtins.open', mock_open=True):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Test new file creation
            window._on_new_file()
            
            # Test file opening
            mock_dialog.getOpenFileName.return_value = ("test.txt", "")
            with patch('builtins.open', mock=Mock()) as mock_file:
                mock_file.return_value.__enter__.return_value.read.return_value = "test content"
                window._on_open_file()

    def test_panel_visibility_toggles(self, mock_qt_components, mock_window_components):
        """Test panel visibility toggle methods"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Mock visibility methods
            window.chat_widget.setVisible = Mock()
            window.chat_widget.isVisible = Mock(return_value=True)
            window.terminal_widget.setVisible = Mock()
            window.terminal_widget.isVisible = Mock(return_value=True)
            
            # Test toggle methods
            window._toggle_chat()
            window.chat_widget.setVisible.assert_called_with(False)
            
            window._toggle_terminal()
            window.terminal_widget.setVisible.assert_called_with(False)

    def test_settings_dialog_handling(self, mock_qt_components, mock_window_components):
        """Test settings dialog handling"""
        with patch('gopiai.ui.main.GopiAISettingsDialog') as mock_settings, \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = 1  # Accepted
            mock_dialog_instance.DialogCode.Accepted = 1
            mock_settings.return_value = mock_dialog_instance
            
            window = FramelessGopiAIStandaloneWindow()
            window._open_settings()
            
            mock_settings.assert_called_once()
            mock_dialog_instance.exec.assert_called_once()

    def test_settings_change_handling(self, mock_qt_components, mock_window_components):
        """Test settings change handling"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Mock font and widget visibility methods
            window.font = Mock()
            window.setFont = Mock()
            window.file_explorer.setVisible = Mock()
            window.terminal_widget.setVisible = Mock()
            window.chat_widget.setVisible = Mock()
            
            settings_dict = {
                "font_size": 12,
                "theme": "dark",
                "show_panels": {
                    "file_explorer": True,
                    "terminal": False,
                    "chat": True
                },
                "extensions": {"ext1": True}
            }
            
            window._on_settings_changed(settings_dict)
            
            # Verify settings are applied
            window.file_explorer.setVisible.assert_called_with(True)
            window.terminal_widget.setVisible.assert_called_with(False)
            window.chat_widget.setVisible.assert_called_with(True)

    def test_file_explorer_signal_connection(self, mock_qt_components, mock_window_components):
        """Test file explorer signal connection"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            
            # Test file selection and opening
            test_file_path = "/test/file.txt"
            
            with patch('os.path.isfile', return_value=True), \
                 patch('builtins.open', mock=Mock()) as mock_file:
                mock_file.return_value.__enter__.return_value.read.return_value = "test content"
                
                window._open_file_in_editor(test_file_path)
                window._on_file_selected(test_file_path)

    def test_resize_and_show_events(self, mock_qt_components, mock_window_components):
        """Test resize and show event handling"""
        with patch('gopiai.ui.main.GopiAISettingsDialog'), \
             patch('qtawesome.icon'), \
             patch('gopiai.ui.main.QApplication.instance', return_value=Mock()):
            
            window = FramelessGopiAIStandaloneWindow()
            window._update_grips = Mock()
            
            # Test resize event
            mock_event = Mock()
            with patch('gopiai.ui.main.QMainWindow.resizeEvent'):
                window.resizeEvent(mock_event)
                window._update_grips.assert_called_once()
            
            # Test show event
            window.titlebar_with_menu.menu_bar.refresh_icons = Mock()
            with patch('gopiai.ui.main.QMainWindow.showEvent'):
                window.showEvent(mock_event)


class TestMainFunction:
    """Test the main application function"""
    
    def test_main_function_setup(self):
        """Test main function setup and configuration"""
        with patch('gopiai.ui.main.QApplication') as mock_app, \
             patch('gopiai.ui.main.FramelessGopiAIStandaloneWindow') as mock_window, \
             patch('sys.exit') as mock_exit, \
             patch('warnings.filterwarnings'):
            
            mock_app_instance = Mock()
            mock_app.return_value = mock_app_instance
            mock_window_instance = Mock()
            mock_window.return_value = mock_window_instance
            mock_app_instance.exec.return_value = 0
            
            main()
            
            # Verify application setup
            mock_app.assert_called_once()
            mock_app_instance.setApplicationName.assert_called_with("GopiAI")
            mock_app_instance.setApplicationVersion.assert_called_with("0.3.0")
            mock_app_instance.setOrganizationName.assert_called_with("GopiAI Team")
            
            # Verify window creation and display
            mock_window.assert_called_once()
            mock_window_instance.show.assert_called_once()
            
            # Verify application execution
            mock_exit.assert_called_with(0)

    def test_main_function_exception_handling(self):
        """Test main function exception handling"""
        with patch('gopiai.ui.main.QApplication') as mock_app, \
             patch('gopiai.ui.main.FramelessGopiAIStandaloneWindow') as mock_window, \
             patch('sys.exit') as mock_exit, \
             patch('warnings.filterwarnings'), \
             patch('traceback.print_exc') as mock_traceback:
            
            mock_app.return_value = Mock()
            mock_window.side_effect = Exception("Test exception")
            
            main()
            
            # Verify exception handling
            mock_traceback.assert_called_once()
            mock_exit.assert_called_with(1)

    def test_webengine_flags_in_main(self):
        """Test WebEngine flags setup in main function"""
        with patch('gopiai.ui.main.QApplication'), \
             patch('gopiai.ui.main.FramelessGopiAIStandaloneWindow'), \
             patch('sys.exit'), \
             patch('warnings.filterwarnings'):
            
            main()
            
            expected_flags = "--disable-gpu --disable-software-rasterizer --disable-3d-apis --disable-accelerated-2d-canvas --no-sandbox"
            assert os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS") == expected_flags


class TestModuleLoading:
    """Test module loading and fallback behavior"""
    
    def test_modules_loaded_flag(self):
        """Test MODULES_LOADED flag behavior"""
        # The actual value depends on whether imports succeeded
        assert isinstance(MODULES_LOADED, bool)

    def test_fallback_theme_manager(self, mock_qt_components):
        """Test fallback theme manager when imports fail"""
        with patch('gopiai.ui.main.ThemeManager', None):
            
            fallback = FallbackThemeManager()
            assert fallback.current_theme == "default"
            assert fallback.apply_theme("test") is False


if __name__ == "__main__":
    pytest.main([__file__])