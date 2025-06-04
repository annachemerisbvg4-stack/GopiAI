"""
Тестирование системы определения типов файлов и иконок
====================================================

Скрипт для проверки корректности работы FileTypeDetector и получения иконок.
"""

import os
from ui_components.file_type_detector import FileTypeDetector

def test_file_types():
    """Тестирование определения типов файлов"""
    print("🧪 Тестирование системы определения типов файлов\n")
    
    # Тестовые файлы (примеры)
    test_files = [
        "document.pdf",
        "image.png",
        "code.py",
        "video.mp4",
        "audio.mp3",
        "archive.zip",
        "spreadsheet.xlsx",
        "text.txt",
        "webpage.html",
        "config.json",
        "README.md",
        "Dockerfile",
        "package.json",
        "requirements.txt",
        ".gitignore",
        "Makefile",
        "font.ttf",
        "database.sqlite",
        "presentation.pptx",
        "executable.exe",
        "script.js",
        "style.css",
        "hidden_file.secret",
        "unknown_extension.xyz"
    ]
    
    # Добавим также папку
    test_files.append("folder_example")
    
    print("📋 Результаты определения типов файлов:\n")
    print(f"{'Файл':<25} {'Тип':<15} {'Иконка':<15}")
    print("-" * 55)
    
    for filename in test_files:
        if filename == "folder_example":
            # Создаем временную папку для теста
            file_path = os.path.join(os.getcwd(), filename)
            if not os.path.exists(file_path):
                os.makedirs(file_path, exist_ok=True)
        else:
            file_path = filename
            
        file_type = FileTypeDetector.get_file_type(file_path)
        icon_name = FileTypeDetector.get_icon_for_file(file_path)
        
        print(f"{filename:<25} {file_type:<15} {icon_name:<15}")
    
    print("\n" + "=" * 55)
    
    # Очистка тестовой папки
    folder_path = os.path.join(os.getcwd(), "folder_example")
    if os.path.exists(folder_path):
        try:
            os.rmdir(folder_path)
        except:
            pass

def test_real_files():
    """Тестирование на реальных файлах из текущей директории"""
    print("\n📁 Тестирование на реальных файлах:\n")
    
    current_dir = os.getcwd()
    real_files = []
    
    # Получаем первые 10 файлов из текущей директории
    try:
        for item in os.listdir(current_dir)[:15]:
            item_path = os.path.join(current_dir, item)
            real_files.append((item, item_path))
    except Exception as e:
        print(f"Ошибка чтения директории: {e}")
        return
    
    print(f"{'Файл/Папка':<30} {'Тип':<15} {'Иконка':<15}")
    print("-" * 60)
    
    for filename, file_path in real_files:
        file_type = FileTypeDetector.get_file_type(file_path)
        icon_name = FileTypeDetector.get_icon_for_file(file_path)
        
        # Обрезаем длинные имена
        display_name = filename[:27] + "..." if len(filename) > 30 else filename
        print(f"{display_name:<30} {file_type:<15} {icon_name:<15}")

def test_icon_manager_integration():
    """Тестирование интеграции с менеджером иконок"""
    print("\n🎨 Тестирование интеграции с менеджером иконок:\n")
    
    try:
        from ui_components.icon_system import AutoIconSystem
        
        # Инициализируем систему иконок
        icon_system = AutoIconSystem()
        
        test_icons = ['folder', 'file', 'image', 'code', 'video', 'audio', 'archive']
        
        print("Проверка доступности иконок:")
        for icon_name in test_icons:
            if hasattr(icon_system, 'get_icon'):
                try:
                    icon = icon_system.get_icon(icon_name)
                    status = "✅ Доступна" if icon and not icon.isNull() else "❌ Недоступна"
                except Exception as e:
                    status = f"❌ Ошибка: {e}"
            else:
                status = "❌ Метод get_icon недоступен"
            
            print(f"  {icon_name:<10}: {status}")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта системы иконок: {e}")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования системы файловых иконок\n")
    
    test_file_types()
    test_real_files()
    test_icon_manager_integration()
    
    print("\n✅ Тестирование завершено!")
