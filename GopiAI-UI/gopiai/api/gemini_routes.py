"""
API роуты для работы с Gemini CLI.
"""

from flask import Blueprint, request, jsonify
from gopiai.services.gemini_service import gemini_service
import logging

bp = Blueprint('gemini', __name__, url_prefix='/api/gemini')
logger = logging.getLogger(__name__)

@bp.route('/generate', methods=['POST'])
def generate_text():
    """
    Генерация текста с помощью Gemini.
    
    Параметры запроса (JSON):
        prompt: Текст запроса (обязательный)
        model: Модель для генерации (по умолчанию: gemini-pro)
        **kwargs: Дополнительные параметры генерации
        
    Возвращает:
        JSON с результатом генерации
    """
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Параметр prompt обязателен'
            }), 400
            
        prompt = data['prompt']
        model = data.get('model', 'gemini-pro')
        
        # Извлекаем дополнительные параметры генерации
        generation_params = {k: v for k, v in data.items() 
                           if k not in ['prompt', 'model']}
        
        result = gemini_service.generate_text(
            prompt=prompt,
            model=model,
            **generation_params
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.exception("Ошибка при генерации текста")
        return jsonify({
            'status': 'error',
            'message': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500

@bp.route('/chat', methods=['POST'])
def chat():
    """
    Чат с сохранением контекста.
    
    Параметры запроса (JSON):
        messages: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
        model: Модель для чата (по умолчанию: gemini-pro)
        **kwargs: Дополнительные параметры генерации
        
    Возвращает:
        JSON с ответом модели
    """
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Параметр messages обязателен'
            }), 400
            
        messages = data['messages']
        model = data.get('model', 'gemini-pro')
        
        # Извлекаем дополнительные параметры генерации
        generation_params = {k: v for k, v in data.items() 
                           if k not in ['messages', 'model']}
        
        result = gemini_service.chat(
            messages=messages,
            model=model,
            **generation_params
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.exception("Ошибка в чате")
        return jsonify({
            'status': 'error',
            'message': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500

@bp.route('/models', methods=['GET'])
def list_models():
    """
    Получение списка доступных моделей.
    
    Возвращает:
        JSON со списком моделей
    """
    try:
        result = gemini_service.get_models()
        return jsonify(result)
    except Exception as e:
        logger.exception("Ошибка при получении списка моделей")
        return jsonify({
            'status': 'error',
            'message': f'Не удалось получить список моделей: {str(e)}'
        }), 500

@bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id: str):
    """
    Получение информации о модели.
    
    Аргументы:
        model_id: Идентификатор модели
        
    Возвращает:
        JSON с информацией о модели
    """
    try:
        result = gemini_service.get_model_info(model_id)
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Ошибка при получении информации о модели {model_id}")
        return jsonify({
            'status': 'error',
            'message': f'Не удалось получить информацию о модели: {str(e)}'
        }), 500
