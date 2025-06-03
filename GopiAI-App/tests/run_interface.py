#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска интерфейса GopiAI после сборки.

Этот скрипт предполагает, что проект уже собран с помощью enhanced_build_and_test.py.
"""

import os
import sys
import subprocess
import argparse
import logging
import datetime
from pathlib import Path

# Настройка логирования
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Путь к текущему рабочему каталогу
WORK_DIR = Path(os.getcwd()).absolute()

def get_venv_python():
    """Возвращает путь к интерпретатору Python в виртуальном окружении."""
    venv_dir = WORK_DIR / "venv"
    
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

def run_interface(debug=False, use_simple=False):
    """
    Запускает интерфейс GopiAI.
    
    Args:
        debug (bool): Запускать в режиме отладки
        use_simple (bool): Использовать простой тестовый интерфейс вместо полного
    """
    try:
        # Получаем путь к интерпретатору Python из виртуального окружения
        python_executable = get_venv_python()
        
        if use_simple:
            # Запускаем простой тестовый интерфейс
            example_script = Path("examples") / "simple_test_interface.py"
            if not example_script.exists():
                logging.error(f"Файл simple_test_interface.py не найден в директории examples")
                logging.error("Пожалуйста, убедитесь, что файл существует")
                return False
            
            logging.info("Запуск простого тестового интерфейса...")
            cmd = [str(python_executable), str(example_script)]
            if debug:
                cmd.append("--debug")
                
            subprocess.run(cmd, check=True)
            logging.info("Простой тестовый интерфейс GopiAI закрыт")
            return True
        else:
            # Путь к директории сборки
            build_dir = Path(r"C:\Users\crazy\GopiAI-Build\build")
            
            # Проверяем, существует ли директория сборки
            if not build_dir.exists():
                logging.error(f"Директория сборки не найдена: {build_dir}")
                logging.error("Пожалуйста, сначала выполните сборку проекта с помощью enhanced_build_and_test.py")
                logging.error("Или используйте параметр --simple для запуска простого тестового интерфейса")
                return False
            
            # Проверяем наличие main.py
            main_script = build_dir / "main.py"
            if not main_script.exists():
                logging.error(f"Файл main.py не найден в {build_dir}")
                logging.error("Или используйте параметр --simple для запуска простого тестового интерфейса")
                return False
            
            # Переходим в директорию сборки
            os.chdir(build_dir)
            
            logging.info("Запуск интерфейса GopiAI...")
            
            # Выполняем main.py с помощью интерпретатора из виртуального окружения
            cmd = [str(python_executable), str(main_script)]
            if debug:
                cmd.append("--debug")
                
            subprocess.run(cmd, check=True)
            
            logging.info("Интерфейс GopiAI закрыт")
            return True
    except Exception as e:
        logging.error(f"Ошибка при запуске интерфейса: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция скрипта."""
    logging.info("Запуск скрипта run_interface.py")
    
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Запуск интерфейса GopiAI")
    parser.add_argument("--debug", action="store_true", help="Запустить в режиме отладки")
    parser.add_argument("--simple", action="store_true", help="Использовать простой тестовый интерфейс")
    
    # Разбор аргументов
    args = parser.parse_args()
    
    # Запускаем интерфейс
    run_interface(debug=args.debug, use_simple=args.simple)
    
    logging.info("Скрипт завершен")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}", exc_info=True)
