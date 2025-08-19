#!/usr/bin/env python3
"""
Демо версия GopiAI-UI для тестирования интерфейса
Работает без настоящего API ключа, возвращает тестовые ответы
"""

import os
import sys
import time
import random
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Добавляем путь к проекту
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

app = Flask(__name__, static_folder='static')
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

# Тестовые ответы для демонстрации
DEMO_RESPONSES = [
    "Привет! Это демо-версия GopiAI. В реальной версии здесь будет ответ от Gemini AI.",
    "Отличный вопрос! К сожалению, для полноценной работы нужен API ключ от Google Gemini.",
    "Я понимаю ваш запрос. Чтобы получить настоящие ответы от Gemini, добавьте GEMINI_API_KEY в файл .env",
    "Интересно! В демо-режиме я могу только показать, как работает интерфейс.",
    "Спасибо за вопрос! Настройте API ключ для получения реальных ответов от Gemini AI.",
    "Это демонстрация интерфейса GopiAI. Для работы с настоящим Gemini нужен API ключ.",
]

@app.route('/')
def index():
    """Главная страница с веб-интерфейсом."""
    return send_from_directory('static', 'index.html')

@app.route('/api')
def api_info():
    return jsonify({
        "message": "GopiAI Demo API Server",
        "version": "1.0.0-demo",
        "mode": "demo",
        "note": "Это демо-версия. Для работы с настоящим Gemini добавьте GEMINI_API_KEY в .env файл",
        "endpoints": {
            "generate": "/api/gemini/generate",
            "chat": "/api/gemini/chat",
            "models": "/api/gemini/models"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mode": "demo"})

@app.route('/api/gemini/generate', methods=['POST'])
def generate_text():
    """Демо генерация текста."""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Параметр prompt обязателен'
            }), 400
        
        # Имитируем задержку API
        time.sleep(random.uniform(0.5, 2.0))
        
        # Возвращаем случайный демо-ответ
        demo_response = random.choice(DEMO_RESPONSES)
        
        return jsonify({
            "status": "success",
            "data": f"{demo_response}\n\n(Ваш запрос: {data['prompt'][:100]}...)",
            "usage": {
                "prompt_tokens": len(data['prompt']) // 4,
                "completion_tokens": len(demo_response) // 4,
                "total_tokens": (len(data['prompt']) + len(demo_response)) // 4
            },
            "demo": True
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Ошибка: {str(e)}'
        }), 500

@app.route('/api/gemini/chat', methods=['POST'])
def chat():
    """Демо чат."""
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Параметр messages обязателен'
            }), 400
        
        messages = data['messages']
        if not messages:
            return jsonify({
                'status': 'error',
                'message': 'Список сообщений пуст'
            }), 400
        
        # Имитируем задержку API
        time.sleep(random.uniform(0.5, 2.0))
        
        # Получаем последнее сообщение пользователя
        last_message = messages[-1]['content'] if messages else ""
        
        # Возвращаем случайный демо-ответ с контекстом
        demo_response = random.choice(DEMO_RESPONSES)
        
        return jsonify({
            "status": "success",
            "data": f"{demo_response}\n\n(Отвечаю на: {last_message[:100]}...)",
            "usage": {
                "prompt_tokens": sum(len(msg['content']) for msg in messages) // 4,
                "completion_tokens": len(demo_response) // 4,
                "total_tokens": (sum(len(msg['content']) for msg in messages) + len(demo_response)) // 4
            },
            "demo": True
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Ошибка: {str(e)}'
        }), 500

@app.route('/api/gemini/models', methods=['GET'])
def list_models():
    """Демо список моделей."""
    return jsonify({
        "status": "success",
        "data": [
            {
                "name": "models/gemini-pro",
                "display_name": "Gemini Pro (Demo)",
                "description": "Демо-версия Gemini Pro",
                "input_token_limit": 30720,
                "output_token_limit": 2048
            },
            {
                "name": "models/gemini-1.5-pro",
                "display_name": "Gemini 1.5 Pro (Demo)",
                "description": "Демо-версия Gemini 1.5 Pro",
                "input_token_limit": 1048576,
                "output_token_limit": 8192
            },
            {
                "name": "models/gemini-1.5-flash",
                "display_name": "Gemini 1.5 Flash (Demo)",
                "description": "Демо-версия Gemini 1.5 Flash",
                "input_token_limit": 1048576,
                "output_token_limit": 8192
            }
        ],
        "demo": True
    })

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 12001))
    
    print("🚀 Запуск GopiAI-UI (ДЕМО РЕЖИМ)")
    print(f"📝 Веб-интерфейс: http://{host}:{port}")
    print(f"🔧 API документация: http://{host}:{port}/api")
    print("⚠️  ДЕМО РЕЖИМ: Используются тестовые ответы")
    print("   Для работы с настоящим Gemini добавьте GEMINI_API_KEY в .env файл")
    
    app.run(
        host=host,
        port=port,
        debug=True,
        threaded=True
    )