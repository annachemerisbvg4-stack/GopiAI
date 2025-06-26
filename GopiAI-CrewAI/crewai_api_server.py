#!/usr/bin/env python3
"""
🌐 CrewAI API Server
Микросервис для доступа к CrewAI из основного окружения через REST API
"""

from flask import Flask, request, jsonify
import os
import sys
import json
import time
import traceback
from pathlib import Path

# Настройки сервера
HOST = "127.0.0.1"
PORT = 5050
DEBUG = False

app = Flask(__name__)

# Настройка путей для импорта модулей
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Определяем глобальные переменные для состояния сервера
API_STATUS = {
    "status": "initializing",
    "timestamp": time.time(),
    "crewai_available": False,
    "txtai_available": False
}

# Импорт Smart Delegator (должен быть доступен в окружении CrewAI)
try:
    from tools.gopiai_integration.smart_delegator import smart_delegator
    from tools.gopiai_integration.smart_delegator import crewai_available, txtai_available
    API_STATUS["status"] = "online"
    API_STATUS["crewai_available"] = crewai_available
    API_STATUS["txtai_available"] = txtai_available
    print("✅ Smart Delegator успешно импортирован")
except ImportError as e:
    print(f"❌ Ошибка импорта Smart Delegator: {e}")
    print("⚠️ API сервер запущен в ограниченном режиме")
    API_STATUS["status"] = "limited"
    smart_delegator = None

@app.route('/', methods=['GET'])
def index():
    """Главная страница с информацией о API"""
    API_STATUS["timestamp"] = time.time()
    
    # Формируем HTML страницу
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CrewAI API Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            .status {{ padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
            .online {{ background-color: #d4edda; color: #155724; }}
            .limited {{ background-color: #fff3cd; color: #856404; }}
            .offline {{ background-color: #f8d7da; color: #721c24; }}
            .endpoint {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
            .method {{ display: inline-block; padding: 3px 6px; border-radius: 3px; font-size: 12px; margin-right: 10px; }}
            .get {{ background-color: #61affe; color: white; }}
            .post {{ background-color: #49cc90; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CrewAI API Server</h1>
            
            <div class="status {API_STATUS['status']}">
                <strong>Статус:</strong> {API_STATUS['status'].upper()}<br>
                <strong>CrewAI доступен:</strong> {'✅' if API_STATUS['crewai_available'] else '❌'}<br>
                <strong>txtai доступен:</strong> {'✅' if API_STATUS['txtai_available'] else '❌'}<br>
                <strong>Время последнего обновления:</strong> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(API_STATUS['timestamp']))}
            </div>
            
            <h2>Доступные эндпоинты</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span> <strong>/api/health</strong>
                <p>Проверка работоспособности API. Возвращает текущий статус сервера.</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/analyze</strong>
                <p>Анализ запроса пользователя. Определяет сложность и требуемый тип обработки.</p>
                <p><em>Параметры:</em> {{ "message": "текст запроса" }}</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/process</strong>
                <p>Обработка запроса пользователя через AI Router или CrewAI.</p>
                <p><em>Параметры:</em> {{ "message": "текст запроса", "force_crewai": false }}</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/index_docs</strong>
                <p>Запуск индексации документации CrewAI для RAG.</p>
            </div>
            
            <hr>
            <p><small>Время запуска сервера: {time.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    API_STATUS["timestamp"] = time.time()
    return jsonify(API_STATUS)

@app.route('/api/analyze', methods=['POST'])
def analyze_request():
    """Анализ запроса пользователя"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Отсутствует поле 'message'"}), 400
    
    try:
        message = data['message']
        analysis = smart_delegator.analyze_request(message)
        return jsonify(analysis)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_request():
    """Обработка запроса через CrewAI"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Отсутствует поле 'message'"}), 400
    
    try:
        message = data['message']
        force_crewai = data.get('force_crewai', False)
        
        # Безопасная обработка запроса с перехватом всех исключений
        try:
            # Анализируем запрос
            analysis = smart_delegator.analyze_request(message)
            
            # Обрабатываем запрос
            if force_crewai:
                # Принудительно через CrewAI
                response = smart_delegator._handle_with_crewai(message, analysis)
            else:
                # Стандартная обработка
                response = smart_delegator.process_request(message)
                
            return jsonify({
                "response": response,
                "processed_with_crewai": force_crewai or analysis.get("requires_crewai", False)
            })
        except Exception as inner_e:
            # В случае любой ошибки возвращаем fallback ответ
            traceback.print_exc()
            return jsonify({
                "response": f"[ОШИБКА ОБРАБОТКИ] Извините, произошла ошибка при обработке вашего запроса: {str(inner_e)}",
                "processed_with_crewai": False,
                "error": str(inner_e)
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/index_docs', methods=['POST'])
def index_documentation():
    """Запуск индексации документации CrewAI"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    try:
        # Проверяем, доступна ли функция индексации
        if not hasattr(smart_delegator, "index_documentation"):
            return jsonify({
                "success": False,
                "error": "Функция индексации недоступна (отсутствует txtai)"
            })
            
        try:
            result = smart_delegator.index_documentation()
            return jsonify({"success": result})
        except Exception as inner_e:
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(inner_e)
            })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"🚀 Запуск CrewAI API сервера на http://{HOST}:{PORT}")
    print("👉 Этот сервер должен быть запущен из окружения CrewAI (crewai_env)")
    
    # Проверяем корректность окружения
    import sys
    print(f"🔧 Используется Python: {sys.executable}")
    
    # Проверяем доступность основных модулей
    try:
        import crewai
        print("✅ Модуль crewai доступен")
    except ImportError:
        print("⚠️ Модуль crewai НЕ доступен")
    
    try:
        import langchain
        print("✅ Модуль langchain доступен")
    except ImportError:
        print("⚠️ Модуль langchain НЕ доступен")
        
    try:
        import txtai
        print("✅ Модуль txtai доступен")
    except ImportError:
        print("⚠️ Модуль txtai НЕ доступен")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)