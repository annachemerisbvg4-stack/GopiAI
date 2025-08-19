#!/usr/bin/env python3
"""
Flask API сервер для GopiAI-UI
Обеспечивает REST API для взаимодействия с Gemini
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import logging

# Добавляем путь к проекту
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gopiai.enhanced_logging import setup_logging

# Настраиваем логирование
setup_logging(log_level=logging.INFO, log_to_file=True)
logger = logging.getLogger(__name__)

def create_app():
    """Создает и настраивает Flask приложение."""
    app = Flask(__name__, static_folder='static')
    
    # Настраиваем CORS для работы с фронтендом
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Регистрируем blueprints
    # app.register_blueprint(gemini_bp) # Blueprint удален, так как API устарело
    
    @app.route('/')
    def index():
        """Главная страница с веб-интерфейсом."""
        return send_from_directory('static', 'index.html')
    
    @app.route('/api')
    def api_info():
        return jsonify({
            "message": "GopiAI API Server",
            "version": "1.0.0",
            "endpoints": {
                "generate": "/api/gemini/generate",
                "chat": "/api/gemini/chat",
                "models": "/api/gemini/models"
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Настраиваем сервер для работы в контейнере
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 12001))
    
    logger.info(f"Запуск API сервера на {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=True,
        threaded=True
    )