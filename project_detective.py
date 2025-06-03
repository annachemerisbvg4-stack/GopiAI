#!/usr/bin/env python3
"""
🔍 ДЕТЕКТИВНЫЙ АНАЛИЗ ФАЙЛОВ ПРОЕКТА
===================================

Анализирует файлы в корне проекта на предмет:
- Пустых или почти пустых файлов
- Дублирования функциональности
- Потенциальных конфликтов
- Ненужных файлов
"""

import os
from pathlib import Path

def analyze_suspicious_files():
    """Анализ подозрительных файлов в корне проекта"""
    print("🔍 ДЕТЕКТИВНОЕ РАССЛЕДОВАНИЕ ФАЙЛОВ ПРОЕКТА")
    print("=" * 60)
    
    base_path = Path(".")
    
    # Список файлов для анализа
    python_files = list(base_path.glob("*.py"))
    
    suspicious_files = []
    empty_files = []
    small_files = []
    
    print("📋 Анализ Python файлов в корне:\n")
    
    for file_path in python_files:
        if file_path.is_file():
            size = file_path.stat().st_size
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    lines = len(content.split('\n')) if content else 0
                
                # Анализ размера и содержимого
                status = "✅"
                notes = []
                
                if size == 0:
                    status = "❌"
                    notes.append("ПУСТОЙ ФАЙЛ")
                    empty_files.append(file_path.name)
                elif size < 100:
                    status = "⚠️"
                    notes.append("ОЧЕНЬ МАЛЕНЬКИЙ")
                    small_files.append(file_path.name)
                elif lines < 10:
                    status = "⚠️"
                    notes.append("МАЛО СТРОК")
                    small_files.append(file_path.name)
                
                # Проверка на дубли функциональности
                if "interface" in file_path.name and file_path.name != "gopiai_standalone_interface_modular.py":
                    if file_path.name != "gopiai_standalone_interface.py":  # Оригинал оставляем
                        status = "🔄"
                        notes.append("ВОЗМОЖНЫЙ ДУБЛЬ")
                        suspicious_files.append(file_path.name)
                
                # Проверка тестовых файлов
                if file_path.name.startswith("test_") and "modular" not in file_path.name:
                    status = "🧪"
                    notes.append("СТАРЫЙ ТЕСТ")
                    suspicious_files.append(file_path.name)
                
                print(f"{status} {file_path.name:40} | {size:6} bytes | {lines:3} lines | {', '.join(notes) if notes else 'OK'}")
                
            except Exception as e:
                print(f"❌ {file_path.name:40} | ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    
    if empty_files:
        print(f"\n❌ ПУСТЫЕ ФАЙЛЫ ({len(empty_files)}):")
        for file in empty_files:
            print(f"   • {file}")
    
    if small_files:
        print(f"\n⚠️ ПОДОЗРИТЕЛЬНО МАЛЕНЬКИЕ ФАЙЛЫ ({len(small_files)}):")
        for file in small_files:
            print(f"   • {file}")
    
    if suspicious_files:
        print(f"\n🔄 ПОТЕНЦИАЛЬНЫЕ ДУБЛИ/СТАРЫЕ ФАЙЛЫ ({len(suspicious_files)}):")
        for file in suspicious_files:
            print(f"   • {file}")
    
    # Анализ других файлов
    print(f"\n📁 ДРУГИЕ ФАЙЛЫ В КОРНЕ:")
    other_files = [f for f in base_path.iterdir() if f.is_file() and not f.name.endswith('.py')]
    
    for file_path in other_files:
        if file_path.name.startswith('.'):
            continue
            
        size = file_path.stat().st_size
        
        if file_path.suffix in ['.png', '.jpg', '.jpeg']:
            print(f"🖼️ {file_path.name:40} | {size:6} bytes | Изображение")
        elif file_path.suffix in ['.json']:
            print(f"📄 {file_path.name:40} | {size:6} bytes | JSON")
        elif file_path.suffix in ['.md']:
            print(f"📚 {file_path.name:40} | {size:6} bytes | Документация")
        else:
            print(f"❓ {file_path.name:40} | {size:6} bytes | {file_path.suffix}")
    
    print("\n" + "=" * 60)
    print("💡 РЕКОМЕНДАЦИИ:")
    
    if empty_files:
        print("• Удалить пустые файлы")
    
    if small_files:
        print("• Проверить маленькие файлы на актуальность")
    
    if suspicious_files:
        print("• Архивировать/удалить дублирующие файлы")
    
    print("• Перенести тестовые файлы в папку tests/")
    print("• Перенести документацию в папку docs/")

def get_file_details(filename):
    """Получить детали конкретного файла"""
    try:
        file_path = Path(filename)
        if not file_path.exists():
            return f"❌ Файл {filename} не найден"
        
        size = file_path.stat().st_size
        
        if filename.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.split('\n'))
                
            # Анализ содержимого
            has_classes = 'class ' in content
            has_functions = 'def ' in content
            has_imports = 'import ' in content or 'from ' in content
            
            analysis = []
            if has_classes:
                analysis.append("содержит классы")
            if has_functions:
                analysis.append("содержит функции")
            if has_imports:
                analysis.append("имеет импорты")
            
            return f"""
📄 {filename}:
   • Размер: {size} bytes
   • Строк: {lines}
   • Анализ: {', '.join(analysis) if analysis else 'возможно пустой/шаблон'}
   • Первые строки:
{content[:200]}...
"""
        else:
            return f"📄 {filename}: {size} bytes"
            
    except Exception as e:
        return f"❌ Ошибка анализа {filename}: {e}"

if __name__ == "__main__":
    analyze_suspicious_files()
