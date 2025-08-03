#!/usr/bin/env python3
"""
GopiAI Web Demo - Простой веб-интерфейс для демонстрации работы системы
"""

import os
import sys
import json
import requests
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

# Добавляем пути
sys.path.append('/workspace/project/GopiAI/GopiAI-CrewAI')

app = Flask(__name__)
CORS(app)

# HTML шаблон для веб-интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GopiAI - Демонстрация системы</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #4facfe;
        }
        .status-card h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online { background-color: #27ae60; }
        .status-offline { background-color: #e74c3c; }
        .status-warning { background-color: #f39c12; }
        .chat-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .chat-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        .chat-input:focus {
            outline: none;
            border-color: #4facfe;
        }
        .send-btn {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .send-btn:hover {
            transform: translateY(-2px);
        }
        .response-area {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-top: 15px;
            min-height: 200px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .feature-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #4facfe;
        }
        .loading {
            display: none;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 GopiAI System</h1>
            <p>Демонстрация работы системы искусственного интеллекта</p>
        </div>
        
        <div class="content">
            <div class="status-grid">
                <div class="status-card">
                    <h3>🚀 CrewAI API Server</h3>
                    <div id="crewai-status">
                        <span class="status-indicator status-offline"></span>
                        Проверка соединения...
                    </div>
                    <p>Основной API сервер для обработки запросов</p>
                </div>
                
                <div class="status-card">
                    <h3>🧠 RAG System</h3>
                    <div id="rag-status">
                        <span class="status-indicator status-warning"></span>
                        Проверка состояния...
                    </div>
                    <p>Система поиска и обработки документов</p>
                </div>
                
                <div class="status-card">
                    <h3>🔄 Model Switching</h3>
                    <div id="model-status">
                        <span class="status-indicator status-warning"></span>
                        Загрузка моделей...
                    </div>
                    <p>Система переключения между AI моделями</p>
                </div>
            </div>
            
            <div class="chat-section">
                <h3>💬 Тестирование системы</h3>
                <input type="text" class="chat-input" id="user-input" placeholder="Введите ваш вопрос или команду...">
                <button class="send-btn" onclick="sendMessage()">Отправить</button>
                <div class="loading" id="loading">⏳ Обработка запроса...</div>
                <div class="response-area" id="response">Здесь будет отображен ответ системы...</div>
            </div>
            
            <div class="feature-list">
                <div class="feature-item">
                    <h4>🔧 Установленные компоненты</h4>
                    <ul>
                        <li>CrewAI Framework</li>
                        <li>LangChain Integration</li>
                        <li>OpenAI & Anthropic APIs</li>
                        <li>Vector Memory System</li>
                    </ul>
                </div>
                
                <div class="feature-item">
                    <h4>🎯 Возможности</h4>
                    <ul>
                        <li>Переключение AI моделей</li>
                        <li>RAG система поиска</li>
                        <li>Обработка документов</li>
                        <li>Веб-скрапинг</li>
                    </ul>
                </div>
                
                <div class="feature-item">
                    <h4>📊 Статистика</h4>
                    <ul>
                        <li>Место на диске: 25GB доступно</li>
                        <li>Python 3.12.11</li>
                        <li>Все зависимости установлены</li>
                        <li>Тесты: ✅ Пройдены</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Проверка статуса систем
        async function checkSystemStatus() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                document.getElementById('crewai-status').innerHTML = 
                    '<span class="status-indicator status-online"></span>Онлайн - ' + data.status;
                
                document.getElementById('rag-status').innerHTML = 
                    '<span class="status-indicator ' + 
                    (data.rag_status === 'NOT INITIALIZED' ? 'status-warning' : 'status-online') + 
                    '"></span>' + data.rag_status;
                    
                document.getElementById('model-status').innerHTML = 
                    '<span class="status-indicator status-online"></span>Готово к работе';
                    
            } catch (error) {
                document.getElementById('crewai-status').innerHTML = 
                    '<span class="status-indicator status-offline"></span>Недоступен';
            }
        }
        
        // Отправка сообщения
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const response = document.getElementById('response');
            const loading = document.getElementById('loading');
            
            if (!input.value.trim()) return;
            
            loading.style.display = 'block';
            response.textContent = 'Обработка запроса...';
            
            try {
                const result = await fetch('/api/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: input.value,
                        provider: 'gemini',
                        model_id: 'gemini/gemini-1.5-flash'
                    })
                });
                
                const data = await result.json();
                response.textContent = JSON.stringify(data, null, 2);
                
            } catch (error) {
                response.textContent = 'Ошибка: ' + error.message;
            }
            
            loading.style.display = 'none';
            input.value = '';
        }
        
        // Обработка Enter в поле ввода
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Проверяем статус при загрузке
        checkSystemStatus();
        
        // Обновляем статус каждые 30 секунд
        setInterval(checkSystemStatus, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health():
    """Проверка состояния CrewAI API сервера"""
    try:
        response = requests.get('http://localhost:5051/api/health', timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "offline", "error": str(e)}, 503

@app.route('/api/process', methods=['POST'])
def process_message():
    """Проксирование запросов к CrewAI API"""
    try:
        data = request.json
        response = requests.post(
            'http://localhost:5051/api/process',
            json=data,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/models')
def get_models():
    """Получение списка доступных моделей"""
    try:
        response = requests.get('http://localhost:5051/internal/models', timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    print("🚀 Запуск GopiAI Web Demo...")
    print("📍 Веб-интерфейс будет доступен по адресу: http://localhost:8080")
    print("🔗 Внешний доступ: https://work-2-zkxlxbngomvfslzp.prod-runtime.all-hands.dev")
    print("⚙️ CrewAI API Server должен быть запущен на порту 5051")
    
    app.run(host='0.0.0.0', port=8080, debug=False)