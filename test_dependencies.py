import sys
import os
import spacy
from datetime import datetime
from PySide6.QtWidgets import QApplication

# Set console output encoding to UTF-8 for Windows
if sys.platform == 'win32':
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Try different import paths for QSvgWidget
try:
    from PySide6.QtSvgWidgets import QSvgWidget
except ImportError:
    try:
        from PySide6.QtSvg import QSvgWidget
    except ImportError as e:
        print(f"Could not import QSvgWidget: {e}")
        QSvgWidget = None

def test_spacy():
    print("Testing spaCy...")
    try:
        # Test English model
        nlp_en = spacy.load("en_core_web_sm")
        doc = nlp_en("This is a test sentence.")
        print(f"[OK] English model works. Tokens: {[token.text for token in doc]}")
        
        # Test Russian model
        nlp_ru = spacy.load("ru_core_news_sm")
        doc = nlp_ru("Это тестовое предложение.")
        print(f"[OK] Russian model works. Tokens: {[token.text for token in doc]}")
        return True
    except Exception as e:
        print(f"[ERROR] spaCy test failed: {e}")
        return False

def test_qt():
    print("\nTesting PySide6...")
    try:
        # Test QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        print("[OK] QApplication created successfully")
        
        # Test QSvgWidget if available
        if QSvgWidget is not None:
            svg_widget = QSvgWidget()
            print("[OK] QSvgWidget created successfully")
            return True
        else:
            print("[WARNING] QSvgWidget not available - some UI features may not work")
            return True  # Not a critical error for basic functionality
            
    except Exception as e:
        print(f"[ERROR] PySide6 test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Dependencies ===")
    print(f"Python version: {sys.version}")
    print(f"spaCy version: {spacy.__version__}")
    print(f"Current time: {datetime.now()}")
    
    spacy_ok = test_spacy()
    qt_ok = test_qt()
    
    print("\n=== Test Summary ===")
    print(f"spaCy: {'[PASS]' if spacy_ok else '[FAIL]'}")
    print(f"PySide6: {'[PASS]' if qt_ok else '[WARN]'}")
    
    if spacy_ok and qt_ok:
        print("\n[SUCCESS] All critical tests passed!")
    elif spacy_ok:
        print("\n[WARNING] Basic functionality should work, but some UI features may be limited")
    else:
        print("\n[ERROR] Some critical tests failed. Please check the output above.")
