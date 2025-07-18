import sys
import os

print("Python Path:")
for p in sys.path:
    print(f" - {p}")

print("\nImporting gopiai.ui_core...")
try:
    import gopiai.ui_core
    print(f"Successfully imported gopiai.ui_core from: {gopiai.ui_core.__file__}")
    
    print("\nTrying to import get_ui_assistant_tool...")
    try:
        from gopiai.ui_core.ai_tools import get_ui_assistant_tool
        print("Successfully imported get_ui_assistant_tool")
    except ImportError as e:
        print(f"Error importing get_ui_assistant_tool: {e}")
        
        print("\nContents of gopiai.ui_core:")
        print(dir(gopiai.ui_core))
        
except ImportError as e:
    print(f"Error importing gopiai.ui_core: {e}")

print("\nChecking for duplicate gopiai modules in sys.modules:")
for name, module in sys.modules.items():
    if 'gopiai.' in name:
        print(f"Found: {name} -> {getattr(module, '__file__', 'built-in')}")
