#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки работоспособности инструментов GopiAI.
"""

import asyncio
from pathlib import Path

from gopiai.app.tool.str_replace_editor import StrReplaceEditor
from gopiai.app.tool.python_execute import PythonExecute


async def test_str_replace_editor():
    """Тестирует инструмент для редактирования строк в файлах."""
    print("Тестирование StrReplaceEditor...")
    
    # Создаем временный файл для тестирования
    test_file = Path("temp_test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Это тестовый файл.\nЭта строка будет заменена.\nЭто третья строка.")
    
    print(f"Файл создан: {test_file.exists()}")
    print(f"Абсолютный путь: {test_file.absolute()}")
    
    # Создаем экземпляр инструмента
    str_replace = StrReplaceEditor()
      # Заменяем строку в файле
    result = await str_replace.execute(
        file_path=str(test_file.absolute()),
        old_str="Эта строка будет заменена.",
        new_str="Эта строка была успешно заменена!"
    )
    
    # Выводим результат
    print(f"Результат: {result.message}")
    print(f"Успех: {result.success}")
    
    # Проверяем содержимое файла
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"Новое содержимое файла:\n{content}")
    
    # Удаляем временный файл
    test_file.unlink()


async def test_python_execute():
    """Тестирует инструмент для выполнения Python-кода."""
    print("\nТестирование PythonExecute...")
    
    # Создаем экземпляр инструмента
    python_execute = PythonExecute()    # Выполняем Python-код
    code = """
import math

# Простое вычисление факториала без рекурсии
result = 1
for i in range(1, 6):
    result *= i

print(f"5! = {result}")
"""
    
    result = await python_execute.execute(code=code)
    
    # Выводим результат
    print(f"Результат: {result.message}")
    print(f"Данные: {result.data}")
    print(f"Успех: {result.success}")


async def main():
    """Запускает тесты."""
    await test_str_replace_editor()
    await test_python_execute()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        print(f"Произошла ошибка: {e}")
        traceback.print_exc()
