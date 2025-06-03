#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для создания баннера в консоли для отображения статуса
"""

import sys
import platform
import os
from pathlib import Path

def print_banner():
    """Выводит информационный баннер в консоль"""
    banner = """
    ╔═════════════════════════════════════════════════════════╗
    ║                    GopiAI Тестовая среда                ║
    ╠═════════════════════════════════════════════════════════╣
    ║                                                         ║
    ║  - Используйте 'python enhanced_build_and_test.py'      ║
    ║    для сборки проекта и запуска интерфейса              ║
    ║                                                         ║
    ║  - Используйте 'python run_interface.py --simple'       ║
    ║    для запуска простого тестового интерфейса            ║
    ║                                                         ║
    ║  - Используйте 'python test_agents.py'                  ║
    ║    для проверки работы агентов                          ║
    ║                                                         ║
    ╚═════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Проверяет окружение и выводит информацию о нем"""
    print(f"Операционная система: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # Проверка виртуального окружения
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    venv_status = "Активно" if in_venv else "Не активно"
    print(f"Виртуальное окружение: {venv_status}")
    
    # Проверка важных компонентов
    try:
        import PySide6
        pyside_version = PySide6.__version__
        print(f"PySide6: Установлен (версия {pyside_version})")
    except ImportError:
        print("PySide6: Не установлен")
    
    try:
        import yaml
        yaml_version = yaml.__version__
        print(f"PyYAML: Установлен (версия {yaml_version})")
    except ImportError:
        print("PyYAML: Не установлен")
    
    try:
        import requests
        requests_version = requests.__version__
        print(f"Requests: Установлен (версия {requests_version})")
    except ImportError:
        print("Requests: Не установлен")

def main():
    """Основная функция скрипта"""
    print_banner()
    print("\nИнформация о системе:")
    print("-" * 50)
    check_environment()
    print("-" * 50)
    print("\nДля дополнительной информации см. ИНСТРУКЦИЯ_ПО_ТЕСТИРОВАНИЮ.md\n")

if __name__ == "__main__":
    main()
