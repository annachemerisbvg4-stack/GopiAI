#!/usr/bin/env python3
"""
🔧 Автоматическое применение исправлений для проблемы с чатом
"""
import os
import shutil
from pathlib import Path

def apply_fixes():
    """Применяет исправления к файлам проекта"""
    print("🔧 ПРИМЕНЕНИЕ ИСПРАВЛЕНИЙ ДЛЯ ПРОБЛЕМЫ С ЧАТОМ")
    print("="*60)
    
    # Пути к файлам
    user_files_dir = Path("/workspace/user_input_files")
    fixes_dir = Path("/workspace/code")
    
    original_client = user_files_dir / "crewai_client.py"
    fixed_client = fixes_dir / "fixed_crewai_client.py"
    
    # Проверяем наличие файлов
    if not original_client.exists():
        print(f"❌ Файл не найден: {original_client}")
        return False
        
    if not fixed_client.exists():
        print(f"❌ Исправленный файл не найден: {fixed_client}")
        return False
    
    try:
        # Создаем резервную копию
        backup_client = user_files_dir / "crewai_client.py.backup"
        shutil.copy2(original_client, backup_client)
        print(f"✅ Создана резервная копия: {backup_client}")
        
        # Применяем исправление
        shutil.copy2(fixed_client, original_client)
        print(f"✅ Применено исправление: {original_client}")
        
        print("\n📋 ИНСТРУКЦИИ ПО ДАЛЬНЕЙШИМ ДЕЙСТВИЯМ:")
        print("1. Обновите методы в chat_widget.py согласно инструкции")
        print("2. Перезапустите приложение")
        print("3. Протестируйте отправку сообщения")
        print("4. Проверьте логи для подтверждения корректной работы")
        
        print(f"\n💾 Резервная копия сохранена в: {backup_client}")
        print("   Для отката используйте: mv crewai_client.py.backup crewai_client.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении исправлений: {e}")
        return False

def show_comparison():
    """Показывает сравнение между оригинальным и исправленным кодом"""
    print("\n📊 СРАВНЕНИЕ КОДА:")
    print("-"*40)
    
    print("🔴 ОРИГИНАЛЬНАЯ ВЕРСИЯ (строка 87):")
    print("   return data['response']  # Возвращает только строку")
    
    print("\n🟢 ИСПРАВЛЕННАЯ ВЕРСИЯ:")
    print("   return {")
    print("       'response': data['response'],")
    print("       'processed_with_crewai': data.get('processed_with_crewai', False)")
    print("   }")
    
    print("\n💡 РЕЗУЛЬТАТ ИСПРАВЛЕНИЯ:")
    print("   ✅ ChatWidget теперь получает словарь с полем 'response'")
    print("   ✅ Условие в строке 199 chat_widget.py будет выполняться")
    print("   ✅ Ответы будут отображаться в интерфейсе")

if __name__ == "__main__":
    show_comparison()
    
    print("\n" + "="*60)
    response = input("Применить исправления? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'да']:
        success = apply_fixes()
        if success:
            print("\n🎉 ИСПРАВЛЕНИЯ УСПЕШНО ПРИМЕНЕНЫ!")
        else:
            print("\n❌ Не удалось применить исправления")
    else:
        print("\n⏸️ Исправления не применены")
        print("   Вы можете применить их вручную, следуя инструкции в docs/fix_instruction.md")
