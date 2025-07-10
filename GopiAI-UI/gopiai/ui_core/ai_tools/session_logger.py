"""
Session Logger for UI Assistant

This module provides functionality for logging UI Assistant activities to files,
with automatic cleanup of old log files.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

class SessionLogger:
    """Handles logging of UI Assistant activities to session-based log files.
    
    Automatically manages log files with the following structure:
    - Logs are stored in a 'logs' subdirectory
    - Each session gets its own file with timestamp in the name
    - Old logs are automatically cleaned up when the limit is reached
    """
    
    def __init__(self, log_dir: str = "logs", max_files: int = 100):
        """Initialize the session logger.
        
        Args:
            log_dir: Directory to store log files (default: 'logs')
            max_files: Maximum number of log files to keep (default: 100)
        """
        self.log_dir = Path(log_dir)
        self.max_files = max_files
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"ui_assistant_{self.session_id}.log"
        self.logger = None
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self._setup_logger()
        
        # Clean up old logs if needed
        self._cleanup_old_logs()
    
    def _setup_logger(self):
        """Configure the logger with file and console handlers."""
        self.logger = logging.getLogger(f"UIAssistant_{self.session_id}")
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler (optional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Log session start
        self.logger.info("=" * 50)
        self.logger.info(f"UI Assistant Session Started: {self.session_id}")
        self.logger.info("=" * 50)
    
    def _cleanup_old_logs(self):
        """Remove old log files if the number exceeds max_files."""
        try:
            # Get all log files, oldest first
            log_files = sorted(
                self.log_dir.glob("ui_assistant_*.log"),
                key=os.path.getmtime
            )
            
            # Delete oldest files if we're over the limit
            while len(log_files) > self.max_files - 1:  # -1 because we're about to add a new one
                old_file = log_files.pop(0)
                try:
                    old_file.unlink()
                    self.logger.info(f"Removed old log file: {old_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to remove old log file {old_file}: {e}")
        except Exception as e:
            print(f"Error cleaning up old logs: {e}")
    
    def log_action(self, action: str, details: Optional[dict] = None):
        """Log an action with optional details.
        
        Args:
            action: Description of the action being logged
            details: Optional dictionary with additional details
        """
        if not self.logger:
            return
            
        if details:
            # Format details as a string
            details_str = ", ".join(f"{k}={v}" for k, v in details.items())
            self.logger.info(f"{action} - {details_str}")
        else:
            self.logger.info(action)
    
    def log_error(self, error_msg: str, exc_info=None):
        """Log an error.
        
        Args:
            error_msg: Error message
            exc_info: Optional exception info from sys.exc_info()
        """
        if self.logger:
            self.logger.error(error_msg, exc_info=exc_info)
    
    def log_command(self, command_type: str, **kwargs):
        """Log a command with its parameters.
        
        Args:
            command_type: Type of the command (e.g., 'click', 'type', 'navigate')
            **kwargs: Command parameters
        """
        self.log_action(f"Command: {command_type}", kwargs)

# Global logger instance
_session_logger = None

def get_session_logger() -> SessionLogger:
    """Get or create the global session logger instance."""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger
