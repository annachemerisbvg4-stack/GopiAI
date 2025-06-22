try:
    import ast
    
    with open(r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\ui\dialogs\settings_dialog.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    ast.parse(content)
    print("✅ Синтаксис корректен!")
    
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка в строке {e.lineno}: {e.msg}")
    if e.text:
        print(f"   Проблемная строка: {e.text.strip()}")
except Exception as e:
    print(f"❌ Ошибка: {e}")