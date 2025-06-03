#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска примеров после сборки проекта.

Этот скрипт запускает указанный пример из директории examples после сборки проекта.
"""

import os
import sys
import subprocess
import argparse
import logging
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

# Путь к GopiAI-Build
BUILD_MODULE = r"C:\Users\crazy\GopiAI-Build"

def get_examples():
    """Возвращает список доступных примеров в директории examples."""
    examples_dir = Path("examples")
    if not examples_dir.exists() or not examples_dir.is_dir():
        return []
    
    return [f.stem for f in examples_dir.glob("*.py")]

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

def run_example(example_name):
    """Запускает указанный пример."""
    try:
        # Проверяем, существует ли пример
        example_file = Path("examples") / f"{example_name}.py"
        if not example_file.exists():
            logging.error(f"Пример {example_name} не найден в директории examples")
            return False
        
        logging.info(f"Запуск примера {example_name}...")
        
        # Получаем путь к Python из виртуального окружения
        python_executable = get_venv_python()
        
        # Запускаем пример
        subprocess.run([python_executable, str(example_file)], check=True)
        
        logging.info(f"Пример {example_name} успешно завершен")
        return True
    except Exception as e:
        logging.error(f"Ошибка при запуске примера {example_name}: {str(e)}")
        return False

def main():
    """Основная функция скрипта."""
    logging.info("Запуск скрипта run_example.py")
    
    # Получаем список доступных примеров
    examples = get_examples()
    
    if not examples:
        logging.error("Не найдено ни одного примера в директории examples")
        return
    
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Запуск примеров GopiAI")
    parser.add_argument("example", choices=examples + ["all"], help="Имя примера для запуска (без .py) или 'all' для запуска всех примеров")
    
    # Разбор аргументов
    args = parser.parse_args()
    
    # Запускаем примеры
    if args.example == "all":
        logging.info("Запуск всех примеров...")
        for example in examples:
            run_example(example)
    else:
        run_example(args.example)
    
    logging.info("Скрипт завершен")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}", exc_info=True)
