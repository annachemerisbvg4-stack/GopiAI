import ast
import sys

# Простая проверка синтаксиса Python файла
filename = r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\ui\dialogs\settings_dialog.py"

try:
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Компиляция для проверки синтаксиса
    tree = ast.parse(source)
    print("✅ Файл синтаксически корректен!")
    
    # Попробуем найти строку 243 чтобы понять что там
    lines = source.split('\n')
    if len(lines) >= 243:
        print(f"Строка 243: {lines[242]}")  # 0-based indexing
    else:
        print(f"Файл содержит только {len(lines)} строк")
    
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка в строке {e.lineno}: {e.text}")
    print(f"   {e.msg}")
    
    # Показать контекст ошибки
    lines = e.text.split('\n') if e.text else []
    for i, line in enumerate(lines):
        marker = " --> " if i + 1 == e.lineno else "     "
        print(f"{marker}{i + e.lineno - len(lines) + 1}: {line}")
        
except Exception as e:
    print(f"❌ Ошибка чтения файла: {e}")
    
print("Тест завершен.")