#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска тестов в виртуальном окружении.

Этот скрипт запускает указанный тест из директории корня проекта, используя
интерпретатор Python из виртуального окружения (если оно создано).
"""

import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path
import datetime

# Настройка логирования
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_venv_python():
    """Возвращает путь к интерпретатору Python в виртуальном окружении."""
    venv_dir = Path("venv")
    
    # Проверяем, существует ли виртуальное окружение
    if not venv_dir.exists():
        logging.warning("Виртуальное окружение не найдено. Запуск будет выполнен с системным Python.")
        return sys.executable
    
    # Определяем путь к интерпретатору Python в виртуальном окружении
    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
    
    if not python_executable.exists():
        logging.warning("Python в виртуальном окружении не найден. Запуск будет выполнен с системным Python.")
        return sys.executable
    
    return str(python_executable)

def get_test_files():
    """Возвращает список доступных тестовых файлов."""
    test_files = []
    
    # Поиск в корне проекта
    for file in Path(".").glob("test_*.py"):
        test_files.append(file.stem)
    
    # Поиск в директории tests
    for file in Path("tests").glob("test_*.py"):
        test_files.append(f"tests/{file.stem}")
    
    return sorted(test_files)

def run_test(test_name):
    """Запускает указанный тест."""
    try:
        # Проверяем, существует ли тест
        if "/" in test_name:
            # Тест в поддиректории
            test_file = Path(f"{test_name}.py")
        else:
            # Тест в корне
            test_file = Path(f"{test_name}.py")
        
        if not test_file.exists():
            logging.error(f"Тест {test_name} не найден")
            return False
        
        logging.info(f"Запуск теста {test_name}...")
        
        # Получаем путь к Python из виртуального окружения
        python_executable = get_venv_python()
        
        # Запускаем тест
        subprocess.run([python_executable, str(test_file)], check=True)
        
        logging.info(f"Тест {test_name} успешно завершен")
        return True
    except Exception as e:
        logging.error(f"Ошибка при запуске теста {test_name}: {str(e)}")
        return False

def main():
    """Основная функция скрипта."""
    logging.info("Запуск скрипта run_test.py")
    
    # Получаем список доступных тестов
    tests = get_test_files()
    
    if not tests:
        logging.error("Не найдено ни одного тестового файла")
        return
    
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Запуск тестов GopiAI")
    parser.add_argument("test", choices=tests + ["all"], help="Имя теста для запуска (без .py) или 'all' для запуска всех тестов")
    
    # Разбор аргументов
    args = parser.parse_args()
    
    # Запускаем тесты
    if args.test == "all":
        logging.info("Запуск всех тестов...")
        for test in tests:
            run_test(test)
    else:
        run_test(args.test)
    
    logging.info("Скрипт завершен")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}", exc_info=True)
