import ast
import sys

# Простая проверка синтаксиса Python файла
filename = r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\ui\dialogs\settings_dialog.py"

try:
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Компиляция для проверки синтаксиса
    ast.parse(source)
    print("✅ Файл синтаксически корректен!")
    
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка в строке {e.lineno}: {e.text}")
    print(f"   {e.msg}")
except Exception as e:
    print(f"❌ Ошибка чтения файла: {e}")