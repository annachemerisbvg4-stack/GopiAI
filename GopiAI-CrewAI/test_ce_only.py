import sys
import os
sys.path.append('.')

print("Импортируем CommandExecutor...")
from tools.gopiai_integration.command_executor import CommandExecutor

print("Создаем экземпляр...")
ce = CommandExecutor()

print("Тестируем _execute_terminal_command напрямую...")
result = ce._execute_terminal_command('mkdir C:\\Users\\crazy\\GOPI_AI_MODULES\\TEST_CE_DIRECT')

print("Результат:")
print(f"success: {result.get('success')}")
print(f"output: '{result.get('output')}'")
print(f"error: '{result.get('error')}'")
print(f"return_code: {result.get('return_code')}")

# Проверяем папку
test_path = r"C:\Users\crazy\GOPI_AI_MODULES\TEST_CE_DIRECT"
print(f"Папка создана: {os.path.exists(test_path)}")

print("\nТестируем execute_command...")
cmd_data = {'tool': 'terminal', 'params': {'command': 'mkdir C:\\Users\\crazy\\GOPI_AI_MODULES\\TEST_CE_FULL'}}
result2 = ce.execute_command(cmd_data)

print("Результат execute_command:")
print(f"success: {result2.get('success')}")
print(f"output: '{result2.get('output')}'")
print(f"error: '{result2.get('error')}'")

# Проверяем вторую папку
test_path2 = r"C:\Users\crazy\GOPI_AI_MODULES\TEST_CE_FULL"
print(f"Папка 2 создана: {os.path.exists(test_path2)}")
