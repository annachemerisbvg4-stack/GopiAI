#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для улучшенной сборки и запуска интерфейса GopiAI.

Этот скрипт:
1. Проверяет наличие всех необходимых модулей
2. Копирует необходимые файлы из каждого модуля
3. Устанавливает все зависимости в виртуальное окружение
4. Запускает интерфейс для тестирования
"""

import os
import sys
import subprocess
import shutil
import importlib.util
from pathlib import Path
import logging
import datetime
import json

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
BUILD_MODULE = Path(r"C:\Users\crazy\GopiAI-Build")
CORE_MODULE = Path(r"C:\Users\crazy\GopiAI-Core")
WIDGETS_MODULE = Path(r"C:\Users\crazy\GopiAI-Widgets")
EXTENSIONS_MODULE = Path(r"C:\Users\crazy\GopiAI-Extensions")
APP_MODULE = Path(r"C:\Users\crazy\GopiAI-App")
ASSETS_MODULE = Path(r"C:\Users\crazy\GopiAI-Assets")

# Путь к текущему рабочему каталогу
WORK_DIR = Path(os.getcwd()).absolute()

# Проверяем наличие всех модулей
MODULES = {
    "GopiAI-Build": BUILD_MODULE,
    "GopiAI-Core": CORE_MODULE,
    "GopiAI-Widgets": WIDGETS_MODULE,
    "GopiAI-Extensions": EXTENSIONS_MODULE,
    "GopiAI-App": APP_MODULE,
    "GopiAI-Assets": ASSETS_MODULE
}

# Целевая директория для сборки
BUILD_DIR = BUILD_MODULE / "build"

def get_venv_python():
    """Возвращает путь к интерпретатору Python в виртуальном окружении."""
    venv_dir = WORK_DIR / "venv"
    
    if sys.platform == "win32":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python"
    
    return python_path

def check_modules():
    """Проверяет наличие всех необходимых модулей."""
    missing_modules = []
    
    for name, path in MODULES.items():
        if not path.exists():
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
        venv_dir = WORK_DIR / "venv"
        
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
        python_executable = get_venv_python()
        
        # Обновляем pip
        logging.info("Обновление pip...")
        subprocess.run([str(python_executable), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Ищем requirements.txt в каждом модуле
        requirements_files = []
        for name, path in MODULES.items():
            req_file = path / "requirements.txt"
            if req_file.exists():
                requirements_files.append(req_file)
        
        # Устанавливаем зависимости
        for req_file in requirements_files:
            logging.info(f"Установка зависимостей из {req_file}")
            subprocess.run([str(python_executable), "-m", "pip", "install", "-r", str(req_file)], check=True)
          # Устанавливаем дополнительные важные пакеты
        logging.info("Установка дополнительных пакетов...")
        packages = ["PySide6", "requests", "chardet", "pyyaml", "selenium"]
        for package in packages:
            logging.info(f"Установка {package}...")
            try:
                subprocess.run([str(python_executable), "-m", "pip", "install", package], check=True)
            except subprocess.CalledProcessError as e:
                logging.warning(f"Ошибка при установке {package}: {e}")
                logging.warning(f"Продолжаем без установки {package}")
        
        logging.info("Зависимости установлены успешно")
        return True
    except Exception as e:
        logging.error(f"Ошибка при установке зависимостей: {str(e)}")
        return False

def clean_build_dir():
    """Очищает директорию сборки."""
    try:
        logging.info(f"Очистка директории сборки: {BUILD_DIR}")
        
        # Создаем директорию, если она не существует
        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Удаляем все содержимое
        for item in BUILD_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        
        logging.info("Директория сборки очищена")
        return True
    except Exception as e:
        logging.error(f"Ошибка при очистке директории сборки: {str(e)}")
        return False

def copy_module_files(module_path, target_dir, module_name):
    """Копирует файлы из модуля в целевую директорию."""
    try:
        # Копируем библиотеку gopiai (исключая __pycache__ и т.д.)
        gopiai_dir = module_path / "gopiai"
        if gopiai_dir.exists():
            target_gopiai_dir = target_dir / "gopiai"
            target_gopiai_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем только Python файлы и директории (кроме __pycache__)
            for item in gopiai_dir.glob("**/*"):
                if item.is_dir():
                    if item.name == "__pycache__":
                        continue
                    
                    rel_path = item.relative_to(module_path)
                    (target_dir / rel_path).mkdir(parents=True, exist_ok=True)
                elif item.is_file():
                    if item.suffix in [".py", ".pyw", ".json", ".yaml", ".yml", ".svg", ".html", ".css", ".js"]:
                        rel_path = item.relative_to(module_path)
                        shutil.copy2(item, target_dir / rel_path)
        
        # Копируем ресурсы, если есть
        resources_dir = module_path / "resources"
        if resources_dir.exists():
            target_resources_dir = target_dir / "resources"
            target_resources_dir.mkdir(parents=True, exist_ok=True)
            
            for item in resources_dir.glob("**/*"):
                if item.is_dir():
                    rel_path = item.relative_to(module_path)
                    (target_dir / rel_path).mkdir(parents=True, exist_ok=True)
                elif item.is_file():
                    rel_path = item.relative_to(module_path)
                    shutil.copy2(item, target_dir / rel_path)
        
        # Копируем assets, если есть
        assets_dir = module_path / "assets"
        if assets_dir.exists():
            target_assets_dir = target_dir / "assets"
            target_assets_dir.mkdir(parents=True, exist_ok=True)
            
            for item in assets_dir.glob("**/*"):
                if item.is_dir():
                    rel_path = item.relative_to(module_path)
                    (target_dir / rel_path).mkdir(parents=True, exist_ok=True)
                elif item.is_file():
                    rel_path = item.relative_to(module_path)
                    shutil.copy2(item, target_dir / rel_path)
        
        logging.info(f"Скопированы файлы из {module_name}")
        return True
    except Exception as e:
        logging.error(f"Ошибка при копировании файлов из {module_name}: {str(e)}")
        return False

def special_asset_processing():
    """Обработка иконок и других специальных ресурсов."""
    try:
        # Создаем директории для иконок
        icons_dir = BUILD_DIR / "gopiai" / "assets" / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        lucide_dir = icons_dir / "lucide"
        lucide_dir.mkdir(exist_ok=True)
        
        # Копируем иконки Lucide из ASSETS_MODULE, если они есть
        assets_lucide = ASSETS_MODULE / "icons" / "lucide"
        if assets_lucide.exists():
            logging.info(f"Копирование иконок из {assets_lucide}")
            
            for icon in assets_lucide.glob("*.svg"):
                shutil.copy2(icon, lucide_dir)
        else:
            logging.warning(f"Директория с иконками не найдена: {assets_lucide}")
            
            # Попробуем найти иконки в node_modules
            node_modules = ASSETS_MODULE / "node_modules" / "lucide-static" / "icons"
            if node_modules.exists():
                logging.info(f"Копирование иконок из node_modules: {node_modules}")
                
                for icon in node_modules.glob("*.svg"):
                    shutil.copy2(icon, lucide_dir)
            else:
                logging.warning(f"Иконки не найдены в node_modules")
                
                # Создадим пустую иконку, чтобы система не падала
                with open(lucide_dir / "app.svg", "w", encoding="utf-8") as f:
                    f.write('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2" ry="2"></rect></svg>')
        
        # Копируем файл simple_theme_manager_fix.py как simple_theme_manager.py
        try:
            source_file = APP_MODULE / "gopiai" / "app" / "ui" / "simple_theme_manager_fix.py"
            target_file = BUILD_DIR / "gopiai" / "app" / "ui" / "simple_theme_manager.py"
            
            if source_file.exists():
                logging.info(f"Копирование файла {source_file} как {target_file}")
                shutil.copy2(source_file, target_file)
            else:
                logging.warning(f"Файл {source_file} не найден!")
        except Exception as e:
            logging.error(f"Ошибка при копировании файла simple_theme_manager_fix.py: {str(e)}")
        
        logging.info("Обработка ресурсов завершена")
        return True
    except Exception as e:
        logging.error(f"Ошибка при обработке ресурсов: {str(e)}")
        return False

def build_project():
    """Собирает проект из всех модулей."""
    try:
        logging.info("Сборка проекта...")
        
        # Очищаем директорию сборки
        if not clean_build_dir():
            return False
        
        # Копируем файлы из каждого модуля
        modules_to_copy = {
            "GopiAI-Core": CORE_MODULE,
            "GopiAI-Widgets": WIDGETS_MODULE,
            "GopiAI-Extensions": EXTENSIONS_MODULE,
            "GopiAI-App": APP_MODULE,
            "GopiAI-Assets": ASSETS_MODULE
        }
        
        for name, path in modules_to_copy.items():
            if not copy_module_files(path, BUILD_DIR, name):
                logging.error(f"Ошибка при копировании файлов из {name}")
                return False
        
        # Обрабатываем специальные ресурсы
        if not special_asset_processing():
            return False
        
        # Создаем файл main.py для запуска
        main_file = BUILD_DIR / "main.py"
        logging.info(f"Создание файла запуска: {main_file}")
        
        with open(main_file, "w", encoding="utf-8") as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
Точка входа в приложение GopiAI.
\"\"\"

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.abspath("."))

# Импортируем и запускаем приложение
try:
    from gopiai.app.ui.main import main
    main()
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
""")
        
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
        python_executable = get_venv_python()
        
        # Переходим в директорию сборки
        os.chdir(BUILD_DIR)
        
        # Запускаем main.py
        subprocess.run([str(python_executable), "main.py"], check=True)
        
        logging.info("Интерфейс закрыт")
        return True
    except Exception as e:
        logging.error(f"Ошибка при запуске интерфейса: {str(e)}")
        return False

def main():
    """Основная функция скрипта."""
    logging.info("Запуск скрипта enhanced_build_and_test.py")
    
    # Проверяем наличие модулей
    if not check_modules():
        return
    
    # Создаем виртуальное окружение
    if not create_venv():
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
