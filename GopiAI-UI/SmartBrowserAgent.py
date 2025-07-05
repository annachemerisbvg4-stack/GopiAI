"""
Умный агент браузера с автоматическим определением URL
Использует Brave API для поиска сайтов по названию
"""
import re
import requests
from typing import Optional, Dict, Any
import logging
from urllib.parse import urlparse, urljoin


class SmartURLDetector:
    """Класс для умного определения URL из естественных команд"""
    
    def __init__(self, brave_api_key: str):
        self.brave_api_key = brave_api_key
        self.base_search_url = "https://api.search.brave.com/res/v1/web/search"
        
        # Паттерны для разбора естественных команд
        self.command_patterns = {
            'go_to_site': [
                r'зайди на сайт (.+)',
                r'открой сайт (.+)',
                r'перейди на (.+)',
                r'go to (.+)',
                r'open (.+)',
                r'visit (.+)',
                r'navigate to (.+)'
            ],
            'search_for': [
                r'найди (.+)',
                r'поищи (.+)',
                r'search for (.+)',
                r'look for (.+)'
            ]
        }
    
    def extract_query_from_command(self, command: str) -> Optional[str]:
        """Извлекает поисковый запрос из естественной команды"""
        command = command.lower().strip()
        
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                    # Убираем лишние слова
                    query = re.sub(r'\b(сайт|website|site)\b', '', query, flags=re.IGNORECASE).strip()
                    return query
        
        return None
    
    def is_valid_url(self, text: str) -> bool:
        """Проверяет, является ли текст валидным URL"""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def search_url_with_brave(self, query: str) -> Optional[str]:
        """Ищет URL через Brave API"""
        try:
            params = {
                'q': query,
                'count': 1,
                'safesearch': 'moderate'
            }
            
            headers = {
                'X-Subscription-Token': self.brave_api_key,
                'Accept': 'application/json'
            }
            
            response = requests.get(self.base_search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'web' in data and 'results' in data['web'] and data['web']['results']:
                    return data['web']['results'][0]['url']
            
            logging.warning(f"Brave API search failed: {response.status_code}")
            return None
            
        except Exception as e:
            logging.error(f"Error searching with Brave API: {e}")
            return None
    
    def detect_url(self, command: str) -> Optional[str]:
        """Основной метод для определения URL из команды"""
        
        # 1. Сначала проверяем, не является ли команда уже URL
        if self.is_valid_url(command):
            return command
        
        # 2. Пытаемся найти URL в тексте
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, command)
        if url_match:
            return url_match.group()
        
        # 3. Извлекаем поисковый запрос из естественной команды
        query = self.extract_query_from_command(command)
        if not query:
            return None
        
        # 4. Ищем через Brave API
        url = self.search_url_with_brave(query)
        return url


class SmartBrowserAgent:
    """Умный агент браузера с автоматическим определением URL"""
    
    def __init__(self, brave_api_key: str, browser_use_agent=None):
        self.url_detector = SmartURLDetector(brave_api_key)
        self.browser_agent = browser_use_agent
        self.session_history = []
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Обрабатывает команду пользователя"""
        
        self.logger.info(f"Обработка команды: {command}")
        
        # Определяем URL
        url = self.url_detector.detect_url(command)
        
        if url:
            self.logger.info(f"✅ URL найден: {url}")
            
            # Сохраняем в историю
            self.session_history.append({
                'command': command,
                'detected_url': url,
                'timestamp': self._get_timestamp()
            })
            
            # Если есть browser agent, выполняем навигацию
            if self.browser_agent:
                try:
                    result = self.browser_agent.navigate_to(url)
                    return {
                        'success': True,
                        'url': url,
                        'message': f'Успешно перешёл на {url}',
                        'browser_result': result
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'url': url,
                        'message': f'Ошибка навигации: {str(e)}',
                        'error': str(e)
                    }
            else:
                return {
                    'success': True,
                    'url': url,
                    'message': f'URL найден: {url} (browser agent не подключен)'
                }
        else:
            self.logger.warning(f"❌ Не удалось определить URL из команды: {command}")
            return {
                'success': False,
                'url': None,
                'message': f'Не удалось определить URL из команды: "{command}"'
            }
    
    def _get_timestamp(self):
        """Возвращает текущую временную метку"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_session_history(self):
        """Возвращает историю сессии"""
        return self.session_history
    
    def clear_history(self):
        """Очищает историю сессии"""
        self.session_history = []


# Пример использования
if __name__ == "__main__":
    # Инициализация агента
    brave_api_key = "BSAEcqmI0ZUDsktUV1FKYYYq7HaQlnt"
    agent = SmartBrowserAgent(brave_api_key)
    
    # Тестовые команды
    test_commands = [
        "зайди на сайт leonardo ai",
        "открой github",
        "перейди на https://google.com",
        "visit stackoverflow",
        "найди документацию python"
    ]
    
    print("🚀 Тестирование SmartBrowserAgent:\n")
    
    for command in test_commands:
        print(f"Команда: {command}")
        result = agent.process_command(command)
        
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
        
        print("-" * 50)
    
    # Показываем историю
    print("\n📝 История сессии:")
    for entry in agent.get_session_history():
        print(f"- {entry['command']} → {entry['detected_url']}")
