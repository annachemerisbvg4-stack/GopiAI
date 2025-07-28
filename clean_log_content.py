#!/usr/bin/env python3
"""
Утилита для очистки содержимого логов от нечитаемых символов
==========================================================

Очищает существующие файлы логов от:
- ANSI цветовых кодов
- Unicode escape-последовательностей
- Избыточной технической информации

Автор: Kiro AI Assistant
Дата: 2025-07-28
"""

import os
import re
import codecs

def clean_log_content(file_path):
    """Очищает содержимое лог файла от нечитаемых символов"""
    
    if not os.path.exists(file_path):
        return False, "Файл не существует"
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Убираем ANSI цветовые коды
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        content = ansi_escape.sub('', content)
        
        # Декодируем Unicode escape-последовательности
        try:
            # Заменяем \uXXXX на нормальные символы
            content = codecs.decode(content, 'unicode_escape')
        except:
            pass
        
        # Убираем избыточные технические сообщения
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Пропускаем технические сообщения
            if any(skip_phrase in line for skip_phrase in [
                'LiteLLM completion()',
                'HTTP Request: GET https://raw.githubusercontent.com',
                'Starting new HTTP connection',
                'connect_tcp.started',
                'send_request_headers',
                'receive_response_headers'
            ]):
                continue
            
            # Сокращаем очень длинные JSON строки
            if 'Raw data:' in line and len(line) > 200:
                line = line.split('Raw data:')[0] + 'Raw data: [JSON данные сокращены]'
            elif 'Parsed JSON:' in line and len(line) > 200:
                line = line.split('Parsed JSON:')[0] + 'Parsed JSON: [JSON данные сокращены]'
            
            # Сокращаем очень длинные строки
            if len(line) > 500:
                line = line[:500] + '... [строка сокращена]'
            
            cleaned_lines.append(line)
        
        # Объединяем обратно
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Записываем очищенный контент
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        new_size = len(cleaned_content)
        reduction = original_size - new_size
        
        return True, f"Размер уменьшен на {reduction} символов ({reduction/original_size*100:.1f}%)"
        
    except Exception as e:
        return False, f"Ошибка: {e}"

def main():
    """Главная функция"""
    print("GopiAI - Очистка содержимого логов")
    print("=" * 40)
    
    # Список файлов логов для очистки
    log_files = [
        "ui_debug.log",
        "GopiAI-CrewAI/crewai_api_server_debug.log",
        "GopiAI-UI/chat_debug.log",
        "GopiAI-UI/chat_widget_debug.log",
        "GopiAI-UI/crewai_client_debug.log"
    ]
    
    cleaned_count = 0
    total_reduction = 0
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n🧹 Очистка: {log_file}")
            success, message = clean_log_content(log_file)
            
            if success:
                print(f"  ✅ {message}")
                cleaned_count += 1
                # Извлекаем размер уменьшения
                if "символов" in message:
                    try:
                        reduction = int(message.split()[3])
                        total_reduction += reduction
                    except:
                        pass
            else:
                print(f"  ❌ {message}")
        else:
            print(f"  📄 Файл не найден: {log_file}")
    
    print(f"\n✅ Очистка завершена!")
    print(f"📊 Обработано файлов: {cleaned_count}")
    if total_reduction > 0:
        if total_reduction < 1024:
            size_str = f"{total_reduction} символов"
        elif total_reduction < 1024 * 1024:
            size_str = f"{total_reduction / 1024:.1f} КБ"
        else:
            size_str = f"{total_reduction / (1024 * 1024):.1f} МБ"
        print(f"💾 Общее уменьшение размера: {size_str}")
    
    print("\n🎯 Теперь логи должны быть более читаемыми!")

if __name__ == "__main__":
    main()