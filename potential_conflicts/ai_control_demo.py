"""
AI Control Demo

A simple demo UI for testing the AI Control System.
"""

import sys
import asyncio
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, Slot
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen

from .ai_control import AIControlSystem, AICommand, CommandType

class AIWorker(QObject):
    """Worker for running async tasks in a separate thread."""
    finished = Signal()
    status_updated = Signal(str)
    
    def __init__(self, ai_control: AIControlSystem, task: str):
        super().__init__()
        self.ai_control = ai_control
        self.task = task
        self._is_running = True
        
    def run(self):
        """Run the AI control loop."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the AI control loop
            loop.run_until_complete(self._run_ai_control())
            
        except Exception as e:
            self.status_updated.emit(f"Error in worker: {str(e)}")
        finally:
            self.finished.emit()
    
    async def _run_ai_control(self):
        """Run the AI control loop."""
        await self.ai_control.run_ai_control_loop(self.task)
    
    def stop(self):
        """Stop the worker."""
        self._is_running = False
        self.ai_control.stop_ai_control()

class AIControlDemo(QMainWindow):
    """Demo UI for the AI Control System."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Control Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize AI Control System
        self.ai_control = AIControlSystem()
        self.ai_control.status_updated.connect(self.update_status)
        self.ai_control.command_started.connect(self.on_command_started)
        self.ai_control.command_completed.connect(self.on_command_completed)
        self.ai_control.screenshot_captured.connect(self.on_screenshot_captured)
        
        # Worker thread for AI control
        self.worker: Optional[AIWorker] = None
        self.worker_thread: Optional[QThread] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Task input
        task_layout = QHBoxLayout()
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Enter a task for the AI (e.g., 'Click the button labeled Save')")
        self.task_input.setMaximumHeight(80)
        task_layout.addWidget(QLabel("Task:"))
        task_layout.addWidget(self.task_input, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start AI Control")
        self.start_button.clicked.connect(self.start_ai_control)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_ai_control)
        self.stop_button.setEnabled(False)
        
        self.capture_button = QPushButton("Capture Screen")
        self.capture_button.clicked.connect(self.capture_screen)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.capture_button)
        button_layout.addStretch()
        
        # Status display
        self.status_label = QLabel("Status: Ready")
        
        # Screenshot display
        self.screenshot_label = QLabel()
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                background-color: #f0f0f0;
                min-height: 300px;
            }
        """)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("AI control log will appear here...")
        
        # Add widgets to layout
        layout.addLayout(task_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.screenshot_label, 1)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_text, 1)
    
    def log_message(self, message: str):
        """Add a message to the log."""
        self.log_text.append(f"{message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def update_status(self, status: str):
        """Update the status label and log."""
        self.status_label.setText(f"Status: {status}")
        self.log_message(f"[STATUS] {status}")
    
    def on_command_started(self, command: AICommand):
        """Handle command started event."""
        self.log_message(f"[COMMAND] Started: {command}")
    
    def on_command_completed(self, command: AICommand, success: bool):
        """Handle command completed event."""
        status = "succeeded" if success else "failed"
        self.log_message(f"[COMMAND] {status}: {command}")
    
    def on_screenshot_captured(self, screenshot: QPixmap):
        """Handle screenshot captured event."""
        # Scale the screenshot to fit the label while maintaining aspect ratio
        scaled = screenshot.scaled(
            self.screenshot_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.screenshot_label.setPixmap(scaled)
    
    def capture_screen(self):
        """Capture and display the screen."""
        screenshot = self.ai_control.capture_screen()
        if screenshot:
            self.on_screenshot_captured(screenshot)
            self.log_message("Screenshot captured")
    
    def start_ai_control(self):
        """Start the AI control loop."""
        task = self.task_input.toPlainText().strip()
        if not task:
            QMessageBox.warning(self, "Error", "Please enter a task for the AI.")
            return
        
        # Disable UI elements
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.task_input.setReadOnly(True)
        
        # Create and start worker thread
        self.worker_thread = QThread()
        self.worker = AIWorker(self.ai_control, task)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.status_updated.connect(self.update_status)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self.on_ai_control_finished)
        
        # Start the thread
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
        
        self.log_message(f"Starting AI control with task: {task}")
    
    def stop_ai_control(self):
        """Stop the AI control loop."""
        if self.worker:
            self.worker.stop()
        self.log_message("Stopping AI control...")
    
    def on_ai_control_finished(self):
        """Clean up after AI control finishes."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.task_input.setReadOnly(False)
        self.worker = None
        self.worker_thread = None
        self.log_message("AI control finished")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker:
            self.stop_ai_control()
            event.ignore()
        else:
            event.accept()

def main():
    """Run the AI Control Demo."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = AIControlDemo()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
