#!/usr/bin/env python3
"""Скрипт для запуска тестов модели переключения провайдеров."""
import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Запуск тестов с правильной настройкой окружения."""
    
    # Получаем путь к текущей директории
    current_dir = Path(__file__).parent.absolute()
    
    # Устанавливаем переменные окружения для тестов
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{current_dir};{current_dir.parent / 'GopiAI-UI' / 'gopiai'}"
    
    # Путь к файлу тестов
    test_file = current_dir / "test_model_switching.py"
    
    if not test_file.exists():
        print(f"❌ Файл тестов не найден: {test_file}")
        return False
    
    print(f"Запуск тестов из файла: {test_file}")
    print("=" * 50)
    
    try:
        # Запускаем тесты
        result = subprocess.run([
            sys.executable, 
            str(test_file)
        ], 
        cwd=current_dir,
        env=env,
        capture_output=False,
        text=True
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ Все тесты успешно пройдены!")
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ Некоторые тесты провалены!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
