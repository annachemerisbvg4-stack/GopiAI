import sys
import os
import subprocess
import logging

# Настраиваем подробное логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=== ДИАГНОСТИКА ВЫПОЛНЕНИЯ КОМАНД ===")

# Тест 1: Прямой subprocess
print("\n1. Тестируем прямой subprocess...")
try:
    result = subprocess.run(
        "mkdir C:\\Users\\crazy\\GOPI_AI_MODULES\\TEST_SUBPROCESS",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=os.getcwd()
    )
    print(f"Код возврата: {result.returncode}")
    print(f"Stdout: '{result.stdout}'")
    print(f"Stderr: '{result.stderr}'")
    
    # Проверяем результат
    test_path = r"C:\Users\crazy\GOPI_AI_MODULES\TEST_SUBPROCESS"
    if os.path.exists(test_path):
        print("✅ Папка создана через subprocess!")
    else:
        print("❌ Папка НЕ создана через subprocess!")
        
except Exception as e:
    print(f"Ошибка subprocess: {e}")

# Тест 2: Тестируем CommandExecutor с подробными логами
print("\n2. Тестируем CommandExecutor...")
sys.path.append('.')

try:
    from tools.gopiai_integration.command_executor import CommandExecutor
    
    ce = CommandExecutor()
    print("CommandExecutor создан")
    
    # Тестируем команду
    command_data = {
        'tool': 'terminal', 
        'params': {'command': 'mkdir C:\\Users\\crazy\\GOPI_AI_MODULES\\TEST_COMMANDEXECUTOR'}
    }
    
    print(f"Выполняем команду: {command_data}")
    result = ce.execute_command(command_data)
    
    print(f"Результат CommandExecutor:")
    print(f"  success: {result.get('success')}")
    print(f"  output: '{result.get('output')}'")
    print(f"  error: '{result.get('error')}'")
    print(f"  return_code: {result.get('return_code')}")
    
    # Проверяем результат
    test_path2 = r"C:\Users\crazy\GOPI_AI_MODULES\TEST_COMMANDEXECUTOR"
    if os.path.exists(test_path2):
        print("✅ Папка создана через CommandExecutor!")
    else:
        print("❌ Папка НЕ создана через CommandExecutor!")
        
except Exception as e:
    print(f"Ошибка CommandExecutor: {e}")
    import traceback
    traceback.print_exc()

# Тест 3: Проверяем текущую рабочую директорию
print(f"\n3. Текущая рабочая директория: {os.getcwd()}")

# Тест 4: Проверяем права на запись
print("\n4. Проверяем права на запись...")
test_write_path = r"C:\Users\crazy\GOPI_AI_MODULES\test_write.txt"
try:
    with open(test_write_path, 'w') as f:
        f.write("test")
    if os.path.exists(test_write_path):
        print("✅ Права на запись есть!")
        os.remove(test_write_path)
    else:
        print("❌ Файл не создался!")
except Exception as e:
    print(f"❌ Ошибка записи: {e}")

# Тест 5: Проверяем существующие папки
print("\n5. Содержимое целевой директории:")
target_dir = r"C:\Users\crazy\GOPI_AI_MODULES"
try:
    items = os.listdir(target_dir)
    for item in items:
        if item.startswith('TEST'):
            print(f"  📁 {item}")
except Exception as e:
    print(f"Ошибка чтения директории: {e}")

print("\n=== КОНЕЦ ДИАГНОСТИКИ ===")
