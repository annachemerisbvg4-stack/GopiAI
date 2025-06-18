#!/usr/bin/env python3
"""
Скрипт для очистки ненужных зависимостей в pyproject.toml файлах
"""
import os
import re
from pathlib import Path

def clean_pyproject_dependencies():
    """Очищает ненужные зависимости из всех pyproject.toml файлов"""
    
    # Ненужные зависимости для удаления
    deps_to_remove = [
        "gopiai-assets",
        "autogen",
        "pyautogen",
    ]
    
    # Найти все pyproject.toml файлы
    modules = [
        "GopiAI",
        "GopiAI-Core",
        "GopiAI-UI", 
        "GopiAI-WebView",
        "GopiAI-Extensions",
        "GopiAI-Widgets",
    ]
    
    for module in modules:
        pyproject_path = Path(module) / "pyproject.toml"
        
        if pyproject_path.exists():
            print(f"🔧 Обрабатываем {pyproject_path}")
            
            # Читаем файл
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Удаляем ненужные зависимости
            for dep in deps_to_remove:
                # Паттерн для удаления строки с зависимостью
                pattern = rf'\s*"{dep}[^"]*",?\n?'
                content = re.sub(pattern, '', content)
                
                # Паттерн для удаления без кавычек
                pattern = rf'\s*{dep}[^,\n]*,?\n?'
                content = re.sub(pattern, '', content)
            
            # Убираем лишние запятые
            content = re.sub(r',(\s*\])', r'\1', content)
            
            # Записываем обратно
            with open(pyproject_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Очищен {pyproject_path}")
        else:
            print(f"❌ Не найден {pyproject_path}")

def check_dependencies():
    """Проверяет текущие зависимости"""
    modules = [
        "GopiAI",
        "GopiAI-Core",
        "GopiAI-UI", 
        "GopiAI-WebView", 
        "GopiAI-Extensions",
        "GopiAI-Widgets",
    ]
    
    print("📋 Текущие зависимости:")
    print("=" * 50)
    
    for module in modules:
        pyproject_path = Path(module) / "pyproject.toml"
        
        if pyproject_path.exists():
            print(f"\n📦 {module}:")
            
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Найти секцию dependencies
            deps_match = re.search(r'dependencies = \[(.*?)\]', content, re.DOTALL)
            if deps_match:
                deps_str = deps_match.group(1)
                deps = [dep.strip().strip('"').strip("'") for dep in deps_str.split(',') if dep.strip()]
                for dep in deps:
                    if dep:
                        print(f"  - {dep}")
            else:
                print("  Нет зависимостей")

if __name__ == "__main__":
    print("🧹 GopiAI Dependency Cleaner")
    print("=" * 50)
    
    print("\n1. Проверка текущих зависимостей:")
    check_dependencies()
    
    print("\n2. Очистка ненужных зависимостей:")
    clean_pyproject_dependencies()
    
    print("\n3. Проверка после очистки:")
    check_dependencies()
    
    print(f"\n✅ Готово! Теперь попробуйте:")
    print("cd GopiAI-UI && pip install -e .")