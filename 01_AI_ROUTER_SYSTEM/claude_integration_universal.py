"""
🚀 Универсальный Claude интегратор для GopiAI
Поддерживает несколько методов доступа к Claude без Anthropic API ключа
"""

import os
import json
import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from urllib.parse import urljoin

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ClaudeMessage:
    """Структура сообщения для Claude"""
    role: str  # 'user', 'assistant', 'system'
    content: str

@dataclass
class ClaudeResponse:
    """Структура ответа от Claude"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None

class ClaudeIntegrator:
    """
    Универсальный интегратор для Claude AI
    Поддерживает несколько методов доступа без официального API ключа
    """
    
    def __init__(self, method: str = "unofficial_server", **kwargs):
        """
        Инициализация интегратора
        
        Args:
            method: Метод доступа ('unofficial_server', 'session_cookie', 'free_trial')
            **kwargs: Параметры для выбранного метода
        """
        self.method = method
        self.config = kwargs
        self._setup_method()
    
    def _setup_method(self):
        """Настройка выбранного метода доступа"""
        if self.method == "unofficial_server":
            self._setup_unofficial_server()
        elif self.method == "session_cookie":
            self._setup_session_cookie()
        elif self.method == "free_trial":
            self._setup_free_trial()
        else:
            raise ValueError(f"Неподдерживаемый метод: {self.method}")
    
    def _setup_unofficial_server(self):
        """Настройка UnofficialClaude сервера"""
        self.base_url = self.config.get('base_url', 'http://localhost:8008')
        self.api_key = self.config.get('api_key', 'local-claude-key')
        self.model = self.config.get('model', 'claude-3-5-sonnet-20240620')
        
        logger.info("Настроен unofficial server метод")
    
    def _setup_session_cookie(self):
        """Настройка прямого доступа через session cookie"""
        try:
            from claude import claude_client, claude_wrapper
            
            session_key = self.config.get('session_key')
            if not session_key:
                raise ValueError("session_key обязателен для этого метода")
            
            self.client = claude_client.ClaudeClient(session_key)
            organizations = self.client.get_organizations()
            
            org_uuid = self.config.get('organization_uuid')
            if not org_uuid and organizations:
                org_uuid = organizations[0]['uuid']
            
            self.claude = claude_wrapper.ClaudeWrapper(
                self.client, 
                organization_uuid=org_uuid
            )
            
            logger.info("Настроен session cookie метод")
            
        except ImportError:
            raise ImportError("Установите claude-api-py: pip install claude-api-py")
    
    def _setup_free_trial(self):
        """Настройка официального API с free trial"""
        self.api_key = self.config.get('anthropic_key')
        if not self.api_key:
            raise ValueError("anthropic_key обязателен для free trial")
        
        self.base_url = 'https://api.anthropic.com'
        self.model = self.config.get('model', 'claude-3-haiku-20240307')
        
        logger.info("Настроен free trial метод")
    
    def chat(self, message: str, history: Optional[List[ClaudeMessage]] = None) -> ClaudeResponse:
        """
        Отправка сообщения Claude
        
        Args:
            message: Текст сообщения
            history: История диалога (опционально)
            
        Returns:
            ClaudeResponse с ответом
        """
        try:
            if self.method == "unofficial_server":
                return self._chat_unofficial_server(message, history)
            elif self.method == "session_cookie":
                return self._chat_session_cookie(message, history)
            elif self.method == "free_trial":
                return self._chat_free_trial(message, history)
        except Exception as e:
            logger.error(f"Ошибка в chat: {e}")
            return ClaudeResponse(
                content=f"Ошибка: {str(e)}",
                model=getattr(self, 'model', 'unknown'),
                error=str(e)
            )
    
    def _chat_unofficial_server(self, message: str, history: Optional[List[ClaudeMessage]] = None) -> ClaudeResponse:
        """Чат через UnofficialClaude сервер"""
        messages = []
        
        if history:
            messages.extend([
                {"role": msg.role, "content": msg.content} 
                for msg in history
            ])
        
        messages.append({"role": "user", "content": message})
        
        url = urljoin(self.base_url, '/v1/chat/completions')
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': self.config.get('max_tokens', 1000),
            'temperature': self.config.get('temperature', 0.7)
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return ClaudeResponse(
                content=result['choices'][0]['message']['content'],
                model=result.get('model', self.model),
                usage=result.get('usage')
            )
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def _chat_session_cookie(self, message: str, history: Optional[List[ClaudeMessage]] = None) -> ClaudeResponse:
        """Чат через session cookie (claude-api-py)"""
        if not hasattr(self, 'current_conversation'):
            # Создаем новый разговор
            conversation = self.claude.start_new_conversation("GopiAI Chat", message)
            self.current_conversation = conversation['uuid']
            response_text = conversation['response']
        else:
            # Продолжаем существующий разговор
            response_text = self.claude.send_message(message)
        
        return ClaudeResponse(
            content=response_text,
            model="claude-session-api"
        )
    
    def _chat_free_trial(self, message: str, history: Optional[List[ClaudeMessage]] = None) -> ClaudeResponse:
        """Чат через официальный API (free trial)"""
        messages = []
        
        if history:
            messages.extend([
                {"role": msg.role, "content": msg.content} 
                for msg in history
            ])
        
        messages.append({"role": "user", "content": message})
        
        url = urljoin(self.base_url, '/v1/messages')
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': self.model,
            'max_tokens': self.config.get('max_tokens', 1000),
            'messages': messages
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return ClaudeResponse(
                content=result['content'][0]['text'],
                model=result.get('model', self.model),
                usage=result.get('usage')
            )
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def test_connection(self) -> bool:
        """Тест соединения с Claude"""
        try:
            response = self.chat("Привет! Ответь просто: Привет!")
            return not response.error and "привет" in response.content.lower()
        except Exception as e:
            logger.error(f"Тест соединения неудачен: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Получение списка доступных моделей"""
        if self.method == "unofficial_server":
            return [
                'claude-3-5-sonnet-20240620',
                'claude-3-opus-20240229',
                'claude-3-haiku-20240307'
            ]
        elif self.method == "session_cookie":
            return ['claude-session-api']
        elif self.method == "free_trial":
            return [
                'claude-3-haiku-20240307',
                'claude-3-sonnet-20240229',
                'claude-3-opus-20240229'
            ]
        return []

class GopiAIClaudeService:
    """Сервис Claude для интеграции с GopiAI"""
    
    def __init__(self, config_file: str = "claude_config.json"):
        """
        Инициализация сервиса
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file
        self.integrator = None
        self._load_config()
    
    def _load_config(self):
        """Загрузка конфигурации"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                method = config.get('method', 'unofficial_server')
                self.integrator = ClaudeIntegrator(method=method, **config.get('params', {}))
                
                logger.info(f"Конфигурация загружена: {method}")
            else:
                self._create_default_config()
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Создание конфигурации по умолчанию"""
        default_config = {
            "method": "unofficial_server",
            "params": {
                "base_url": "http://localhost:8008",
                "api_key": "local-claude-key",
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 1000,
                "temperature": 0.7
            },
            "alternatives": {
                "session_cookie": {
                    "method": "session_cookie",
                    "params": {
                        "session_key": "sk-ant-sid01-YOUR-SESSION-KEY",
                        "organization_uuid": "your-org-uuid"
                    }
                },
                "free_trial": {
                    "method": "free_trial",
                    "params": {
                        "anthropic_key": "sk-ant-api03-YOUR-API-KEY",
                        "model": "claude-3-haiku-20240307"
                    }
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Создан файл конфигурации: {self.config_file}")
    
    def chat(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Основная функция чата для GopiAI
        
        Args:
            message: Сообщение пользователя
            context: Контекст разговора (опционально)
            
        Returns:
            Словарь с ответом и метаданными
        """
        if not self.integrator:
            return {
                'success': False,
                'error': 'Claude интегратор не инициализирован',
                'response': 'Ошибка конфигурации Claude'
            }
        
        try:
            # Добавляем контекст если есть
            if context:
                full_message = f"Контекст: {context}\n\nСообщение: {message}"
            else:
                full_message = message
            
            # Отправляем сообщение
            response = self.integrator.chat(full_message)
            
            if response.error:
                return {
                    'success': False,
                    'error': response.error,
                    'response': response.content
                }
            
            return {
                'success': True,
                'response': response.content,
                'model': response.model,
                'usage': response.usage,
                'method': self.integrator.method
            }
            
        except Exception as e:
            logger.error(f"Ошибка в chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f'Ошибка обращения к Claude: {str(e)}'
            }
    
    def test_all_methods(self) -> Dict[str, bool]:
        """Тестирование всех доступных методов"""
        results = {}
        
        methods = [
            ('unofficial_server', {
                'base_url': 'http://localhost:8008',
                'api_key': 'local-claude-key'
            }),
            ('session_cookie', {
                'session_key': 'test-key'  # Нужен реальный ключ
            }),
            ('free_trial', {
                'anthropic_key': 'test-key'  # Нужен реальный ключ
            })
        ]
        
        for method, params in methods:
            try:
                integrator = ClaudeIntegrator(method=method, **params)
                results[method] = integrator.test_connection()
            except Exception as e:
                logger.warning(f"Метод {method} недоступен: {e}")
                results[method] = False
        
        return results

# Пример использования
if __name__ == "__main__":
    # Тест с UnofficialClaude сервером
    print("🧪 Тестирование Claude интеграции...")
    
    service = GopiAIClaudeService()
    
    # Тест чата
    result = service.chat("Привет! Как дела?")
    
    if result['success']:
        print(f"✅ Успех: {result['response']}")
        print(f"📊 Модель: {result['model']}")
        print(f"🔧 Метод: {result['method']}")
    else:
        print(f"❌ Ошибка: {result['error']}")
    
    # Тест всех методов
    print("\n🔍 Тестирование всех методов:")
    test_results = service.test_all_methods()
    
    for method, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {method}: {'Работает' if status else 'Не работает'}")