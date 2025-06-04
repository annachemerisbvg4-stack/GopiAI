import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Добавляем корень проекта в sys.path для импортов
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui_components.file_type_detector import FileTypeDetector

# Ensure Qt runs in offscreen mode
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

app = QApplication.instance() or QApplication([])


def test_file_type_detection_basic(tmp_path):
    files = {
        "sample.py": ("code", "code"),
        "image.png": ("image", "image"),
        "document.pdf": ("document", "file-text"),
    }
    for name, expected in files.items():
        path = tmp_path / name
        path.write_text("test")
        file_type, icon = FileTypeDetector.get_file_type_and_icon(str(path))
        assert (file_type, icon) == expected


def test_special_file_detection(tmp_path):
    docker = tmp_path / "Dockerfile"
    docker.write_text("FROM python")
    assert FileTypeDetector.get_file_type(str(docker)) == "docker"
    hidden = tmp_path / ".gitignore"
    hidden.write_text("*.pyc")
    assert FileTypeDetector.get_file_type(str(hidden)) == "git"


def test_folder_detection(tmp_path):
    folder = tmp_path / "folder_example"
    folder.mkdir()
    assert FileTypeDetector.get_file_type(str(folder)) == "folder"
