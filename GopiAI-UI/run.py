#!/usr/bin/env python3
"""
Простой скрипт для запуска GopiAI-UI
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Настраиваем сервер
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 12001))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    
    print(f"🚀 Запуск GopiAI-UI на http://{host}:{port}")
    print(f"📝 Веб-интерфейс: http://{host}:{port}")
    print(f"🔧 API документация: http://{host}:{port}/api")
    
    if not os.environ.get('GEMINI_API_KEY') and not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  ВНИМАНИЕ: API ключ не настроен!")
        print("   Создайте файл .env и добавьте GEMINI_API_KEY=your_key")
        print("   Получить ключ: https://makersuite.google.com/app/apikey")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )