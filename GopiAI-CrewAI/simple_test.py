import sys
import os
sys.path.append('.')

from tools.gopiai_integration.command_executor import CommandExecutor

print("Создаем CommandExecutor...")
ce = CommandExecutor()

print("Тестируем выполнение команды mkdir...")
result = ce.execute_command({
    'tool': 'terminal', 
    'params': {'command': 'mkdir C:\\Users\\crazy\\GOPI_AI_MODULES\\TEST_SIMPLE'}
})

print("Результат выполнения:")
print(f"Успех: {result.get('success', False)}")
print(f"Вывод: {result.get('output', 'Нет вывода')}")
print(f"Ошибка: {result.get('error', 'Нет ошибки')}")

# Проверяем, создалась ли папка
test_path = r"C:\Users\crazy\GOPI_AI_MODULES\TEST_SIMPLE"
if os.path.exists(test_path):
    print("✅ Папка создана успешно!")
else:
    print("❌ Папка НЕ создана!")
