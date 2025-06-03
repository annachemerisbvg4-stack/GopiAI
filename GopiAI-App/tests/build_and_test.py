#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для сборки и тестирования интерфейса GopiAI.

Этот скрипт использует build_project.py из модуля GopiAI-Build для сборки проекта,
а затем запускает интерфейс для тестирования.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging
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

# Пути к модулям
BUILD_MODULE = r"C:\Users\crazy\GopiAI-Build"
CORE_MODULE = r"C:\Users\crazy\GopiAI-Core"
WIDGETS_MODULE = r"C:\Users\crazy\GopiAI-Widgets"
EXTENSIONS_MODULE = r"C:\Users\crazy\GopiAI-Extensions"
APP_MODULE = r"C:\Users\crazy\GopiAI-App"
ASSETS_MODULE = r"C:\Users\crazy\GopiAI-Assets"

# Проверяем наличие всех модулей
MODULES = {
    "GopiAI-Build": BUILD_MODULE,
    "GopiAI-Core": CORE_MODULE,
    "GopiAI-Widgets": WIDGETS_MODULE,
    "GopiAI-Extensions": EXTENSIONS_MODULE,
    "GopiAI-App": APP_MODULE,
    "GopiAI-Assets": ASSETS_MODULE
}

def check_modules():
    """Проверяет наличие всех необходимых модулей."""
    missing_modules = []
    
    for name, path in MODULES.items():
        if not Path(path).exists():
            missing_modules.append(name)
    
    if missing_modules:
        logging.error(f"Не найдены следующие модули: {', '.join(missing_modules)}")
        logging.error("Пожалуйста, убедитесь, что все модули находятся в указанных директориях.")
        return False
    
    logging.info("Все модули найдены")
    return True

def create_venv():
    """Создает виртуальное окружение для тестирования проекта."""
    try:
        venv_dir = Path("venv")
        
        # Проверяем, существует ли уже виртуальное окружение
        if venv_dir.exists():
            logging.info("Виртуальное окружение уже существует")
            return True
        
        logging.info("Создание виртуального окружения...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        logging.info("Виртуальное окружение создано успешно")
        return True
    except Exception as e:
        logging.error(f"Ошибка при создании виртуального окружения: {str(e)}")
        return False

def install_dependencies():
    """Устанавливает необходимые зависимости в виртуальное окружение."""
    try:
        logging.info("Установка зависимостей...")
        
        # Определяем путь к интерпретатору Python в виртуальном окружении
        if sys.platform == "win32":
            python_executable = Path("venv/Scripts/python.exe")
        else:
            python_executable = Path("venv/bin/python")
        
        # Обновляем pip
        logging.info("Обновление pip...")
        subprocess.run([str(python_executable), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Ищем requirements.txt в каждом модуле
        requirements_files = []
        for name, path in MODULES.items():
            req_file = Path(path) / "requirements.txt"
            if req_file.exists():
                requirements_files.append(req_file)
        
        # Устанавливаем зависимости
        for req_file in requirements_files:
            logging.info(f"Установка зависимостей из {req_file}")
            subprocess.run([str(python_executable), "-m", "pip", "install", "-r", str(req_file)], check=True)
        
        # Устанавливаем PySide6
        logging.info("Установка PySide6...")
        subprocess.run([str(python_executable), "-m", "pip", "install", "PySide6"], check=True)
        
        logging.info("Зависимости установлены успешно")
        return True
    except Exception as e:
        logging.error(f"Ошибка при установке зависимостей: {str(e)}")
        return False

def build_project():
    """Собирает проект, используя build_project.py из модуля GopiAI-Build."""
    try:
        logging.info("Запуск сборки проекта...")
        
        # Определяем путь к интерпретатору Python в виртуальном окружении
        if sys.platform == "win32":
            python_executable = Path("venv/Scripts/python.exe").absolute()
        else:
            python_executable = Path("venv/bin/python").absolute()
        
        # Переходим в директорию GopiAI-Build
        os.chdir(BUILD_MODULE)
        
        # Запускаем скрипт сборки
        subprocess.run([str(python_executable), "build_project.py"], check=True)
        
        logging.info("Проект собран успешно")
        return True
    except Exception as e:
        logging.error(f"Ошибка при сборке проекта: {str(e)}")
        return False

def run_interface():
    """Запускает интерфейс для тестирования."""
    try:
        logging.info("Запуск интерфейса...")
        
        # Определяем путь к интерпретатору Python в виртуальном окружении
        if sys.platform == "win32":
            python_executable = Path("venv/Scripts/python.exe").absolute()
        else:
            python_executable = Path("venv/bin/python").absolute()
        
        # Переходим в директорию сборки
        build_dir = Path(BUILD_MODULE) / "build"
        os.chdir(build_dir)
        
        # Запускаем main.py
        subprocess.run([str(python_executable), "main.py"], check=True)
        
        logging.info("Интерфейс закрыт")
        return True
    except Exception as e:
        logging.error(f"Ошибка при запуске интерфейса: {str(e)}")
        return False

def main():
    """Основная функция скрипта."""
    logging.info("Запуск скрипта build_and_test.py")
    
    # Проверяем наличие модулей
    if not check_modules():
        return
    
    # Устанавливаем зависимости
    if not install_dependencies():
        return
    
    # Собираем проект
    if not build_project():
        return
    
    # Запускаем интерфейс
    run_interface()
    
    logging.info("Скрипт завершен")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}", exc_info=True)
