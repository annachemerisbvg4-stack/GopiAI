import sys
sys.path.insert(0, r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\tools")

try:
    from gopiai_integration.terminal_tool import set_terminal_widget
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
