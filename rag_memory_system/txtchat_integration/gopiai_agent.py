#!/usr/bin/env python3
"""
🤖 GopiAI Agent with txtchat-inspired architecture
Адаптация подхода txtchat для интеграции RAG в существующий проект

Основные возможности:
- Workflow-based обработка сообщений
- Конфигурируемые персоны агента
- Умное обогащение контекста через RAG
- Graceful degradation при недоступности RAG
- Кэширование и метрики
"""

import os
import sys
import time
import json
import yaml
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Добавляем путь к модулям проекта
sys.path.append(str(Path(__file__).parent.parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Конфигурация агента"""
    name: str = "GopiAI Assistant"
    description: str = ""
    version: str = "1.0.0"
    persona: str = "helpful_assistant"
    config_path: Optional[str] = None
    
@dataclass
class PersonaConfig:
    """Конфигурация персоны агента"""
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    use_rag: bool = True
    rag_threshold: float = 0.6

@dataclass 
class RAGConfig:
    """Конфигурация RAG системы"""
    enabled: bool = True
    server_url: str = "http://127.0.0.1:5051"
    timeout: int = 4
    max_results: int = 5
    min_score: float = 0.5
    context_window: int = 2000
    enrichment_strategy: str = "smart"
    context_template: str = ""

@dataclass
class CacheEntry:
    """Элемент кэша"""
    data: Any
    timestamp: datetime
    ttl: int
    
    def is_expired(self) -> bool:
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl)

class GopiAIAgent:
    """
    Основной класс агента с txtchat-архитектурой
    """
    
    def __init__(self, config_path: str = None):
        """Инициализация агента"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.cache = {}
        self.metrics = {
            "total_requests": 0,
            "rag_calls": 0,
            "cache_hits": 0,
            "errors": 0,
            "response_times": []
        }
        
        # Настройка логирования
        self._setup_logging()
        
        logger.info(f"GopiAI Agent initialized: {self.config['agent']['name']}")
        logger.info(f"Current persona: {self.config['agent']['persona']}")
        logger.info(f"RAG enabled: {self.config['rag']['enabled']}")
    
    def _get_default_config_path(self) -> str:
        """Получить путь к конфигурации по умолчанию"""
        return str(Path(__file__).parent / "gopiai_agent.yml")
    
    def _load_config(self) -> Dict:
        """Загрузить конфигурацию из YAML файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Конфигурация по умолчанию"""
        return {
            "agent": {
                "name": "GopiAI Assistant",
                "description": "Default configuration",
                "version": "1.0.0",
                "persona": "helpful_assistant"
            },
            "personas": {
                "helpful_assistant": {
                    "system_prompt": "You are a helpful AI assistant.",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "use_rag": True,
                    "rag_threshold": 0.6
                }
            },
            "rag": {
                "enabled": True,
                "server_url": "http://127.0.0.1:5051",
                "timeout": 4,
                "max_results": 5,
                "min_score": 0.5,
                "context_window": 2000,
                "enrichment_strategy": "smart",
                "context_template": "Context: {context}\n\nQuestion: {query}"
            },
            "workflow": {
                "message_processing": {
                    "steps": ["validate_input", "enrich_with_context", "generate_response"]
                },
                "error_handling": {
                    "rag_unavailable": "graceful_degradation"
                }
            },
            "cache": {
                "enabled": True,
                "context_cache_ttl": 300,
                "response_cache_ttl": 60,
                "max_cache_size": 1000
            },
            "logging": {
                "level": "INFO",
                "log_rag_calls": True
            }
        }
    
    def _setup_logging(self):
        """Настройка логирования"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        logger.setLevel(level)
    
    def process_message(self, message: str, context: Dict = None) -> Dict:
        """
        Основной метод обработки сообщения (txtchat workflow)
        
        Args:
            message: Входящее сообщение
            context: Дополнительный контекст
            
        Returns:
            Dict с ответом и метаданными
        """
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Workflow steps
            workflow_steps = self.config['workflow']['message_processing']['steps']
            
            result = {
                "message": message,
                "response": "",
                "context_used": None,
                "persona": self.config['agent']['persona'],
                "workflow_steps": [],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "processing_time": 0,
                    "rag_used": False,
                    "cache_hit": False
                }
            }
            
            for step in workflow_steps:
                step_start = time.time()
                
                if step == "validate_input":
                    result = self._validate_input(message, result)
                elif step == "enrich_with_context":
                    result = self._enrich_with_context(message, result)
                elif step == "generate_response":
                    result = self._generate_response(message, result)
                elif step == "format_output":
                    result = self._format_output(result)
                elif step == "log_interaction":
                    self._log_interaction(result)
                
                step_time = time.time() - step_start
                result["workflow_steps"].append({
                    "step": step,
                    "duration": step_time,
                    "status": "completed"
                })
            
            # Финальная обработка
            processing_time = time.time() - start_time
            result["metadata"]["processing_time"] = processing_time
            self.metrics["response_times"].append(processing_time)
            
            logger.info(f"Message processed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error processing message: {e}")
            return self._handle_error(message, str(e))
    
    def _validate_input(self, message: str, result: Dict) -> Dict:
        """Валидация входящего сообщения"""
        if not message or not message.strip():
            raise ValueError("Empty message")
        
        max_length = self.config.get('security', {}).get('max_query_length', 5000)
        if len(message) > max_length:
            raise ValueError(f"Message too long: {len(message)} > {max_length}")
        
        logger.debug("Input validation passed")
        return result
    
    def _enrich_with_context(self, message: str, result: Dict) -> Dict:
        """Обогащение контекстом через RAG"""
        rag_config = self.config['rag']
        persona_config = self.config['personas'][self.config['agent']['persona']]
        
        # Проверяем, нужно ли использовать RAG
        if not rag_config['enabled'] or not persona_config['use_rag']:
            logger.debug("RAG disabled for this request")
            return result
        
        # Проверяем стратегию обогащения
        strategy = rag_config['enrichment_strategy']
        if strategy == "off":
            return result
        elif strategy == "minimal" and len(message) < 50:
            return result
        
        # Поиск в кэше
        cache_key = self._get_cache_key(message, "context")
        cached_context = self._get_from_cache(cache_key)
        
        if cached_context:
            result["context_used"] = cached_context
            result["metadata"]["cache_hit"] = True
            self.metrics["cache_hits"] += 1
            logger.debug("Context retrieved from cache")
            return result
        
        # Запрос к RAG серверу
        context = self._fetch_rag_context(message)
        
        if context:
            result["context_used"] = context
            result["metadata"]["rag_used"] = True
            self.metrics["rag_calls"] += 1
            
            # Сохраняем в кэш
            self._save_to_cache(cache_key, context, self.config['cache']['context_cache_ttl'])
            
            logger.debug(f"Context enriched with {len(context)} characters")
        else:
            logger.debug("No relevant context found")
        
        return result
    
    def _fetch_rag_context(self, message: str) -> Optional[str]:
        """Получение контекста из RAG сервера"""
        rag_config = self.config['rag']
        
        try:
            url = f"{rag_config['server_url']}/api/search"
            payload = {
                "query": message,
                "max_results": rag_config['max_results']
            }
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=rag_config['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                context = data.get('context')
                
                if context and len(context) > rag_config['min_score'] * 100:
                    # Обрезаем контекст до максимального размера
                    max_length = rag_config['context_window']
                    if len(context) > max_length:
                        context = context[:max_length] + "..."
                    
                    return context
            else:
                logger.warning(f"RAG server returned {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning("RAG server timeout")
        except requests.exceptions.ConnectionError:
            logger.warning("RAG server connection failed")
        except Exception as e:
            logger.error(f"RAG request failed: {e}")
        
        return None
    
    def _generate_response(self, message: str, result: Dict) -> Dict:
        """Генерация ответа (заглушка для интеграции с LLM)"""
        persona_config = self.config['personas'][self.config['agent']['persona']]
        context = result.get("context_used")
        
        # Формируем промпт
        if context:
            template = self.config['rag']['context_template']
            full_prompt = template.format(context=context, query=message)
        else:
            full_prompt = f"{persona_config['system_prompt']}\n\nUser: {message}\nAssistant:"
        
        # Здесь должна быть интеграция с вашим LLM
        # Пока возвращаем заглушку
        response = self._mock_llm_response(full_prompt, persona_config)
        
        result["response"] = response
        logger.debug(f"Response generated: {len(response)} characters")
        
        return result
    
    def _mock_llm_response(self, prompt: str, persona_config: Dict) -> str:
        """Заглушка для LLM (замените на реальную интеграцию)"""
        return f"""[Mock Response]
Persona: {self.config['agent']['persona']}
Temperature: {persona_config['temperature']}
Context available: {'Yes' if 'context' in prompt.lower() else 'No'}
Message processed successfully!

Note: Replace this with actual LLM integration."""
    
    def _format_output(self, result: Dict) -> Dict:
        """Форматирование выходных данных"""
        # Можно добавить дополнительное форматирование
        return result
    
    def _log_interaction(self, result: Dict):
        """Логирование взаимодействия"""
        if self.config['logging']['log_rag_calls'] and result["metadata"]["rag_used"]:
            logger.info(f"RAG used for query: {result['message'][:50]}...")
    
    def _handle_error(self, message: str, error: str) -> Dict:
        """Обработка ошибок"""
        return {
            "message": message,
            "response": "Извините, произошла ошибка при обработке вашего запроса.",
            "error": error,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
        }
    
    def _get_cache_key(self, data: str, prefix: str = "") -> str:
        """Генерация ключа для кэша"""
        hash_obj = hashlib.md5(data.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    def _get_from_cache(self, key: str) -> Any:
        """Получение данных из кэша"""
        if not self.config['cache']['enabled']:
            return None
            
        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            return entry.data
        elif entry:
            del self.cache[key]  # Удаляем устаревшую запись
        
        return None
    
    def _save_to_cache(self, key: str, data: Any, ttl: int):
        """Сохранение данных в кэш"""
        if not self.config['cache']['enabled']:
            return
            
        max_size = self.config['cache']['max_cache_size']
        if len(self.cache) >= max_size:
            # Удаляем самую старую запись
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
        
        self.cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl=ttl
        )
    
    def get_metrics(self) -> Dict:
        """Получение метрик агента"""
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"] else 0
        )
        
        return {
            "total_requests": self.metrics["total_requests"],
            "rag_calls": self.metrics["rag_calls"],
            "cache_hits": self.metrics["cache_hits"],
            "errors": self.metrics["errors"],
            "avg_response_time": avg_response_time,
            "cache_size": len(self.cache),
            "rag_usage_rate": (
                self.metrics["rag_calls"] / max(1, self.metrics["total_requests"])
            ) * 100
        }
    
    def switch_persona(self, persona_name: str) -> bool:
        """Переключение персоны агента"""
        if persona_name in self.config['personas']:
            self.config['agent']['persona'] = persona_name
            logger.info(f"Switched to persona: {persona_name}")
            return True
        else:
            logger.warning(f"Unknown persona: {persona_name}")
            return False
    
    def health_check(self) -> Dict:
        """Проверка состояния агента"""
        rag_status = "unknown"
        
        # Проверяем доступность RAG сервера
        if self.config['rag']['enabled']:
            try:
                url = f"{self.config['rag']['server_url']}/api/health"
                response = requests.get(url, timeout=2)
                rag_status = "online" if response.status_code == 200 else "offline"
            except:
                rag_status = "offline"
        else:
            rag_status = "disabled"
        
        return {
            "agent_status": "online",
            "rag_status": rag_status,
            "current_persona": self.config['agent']['persona'],
            "cache_enabled": self.config['cache']['enabled'],
            "metrics": self.get_metrics()
        }

# Вспомогательные функции для быстрого использования
def create_agent(config_path: str = None) -> GopiAIAgent:
    """Создание экземпляра агента"""
    return GopiAIAgent(config_path)

def quick_chat(message: str, agent: GopiAIAgent = None) -> str:
    """Быстрый чат с агентом"""
    if agent is None:
        agent = create_agent()
    
    result = agent.process_message(message)
    return result.get("response", "Ошибка обработки")

if __name__ == "__main__":
    # Пример использования
    agent = create_agent()
    
    print("🤖 GopiAI Agent with txtchat architecture")
    print(f"Agent: {agent.config['agent']['name']}")
    print(f"Persona: {agent.config['agent']['persona']}")
    print("\nHealth check:")
    print(json.dumps(agent.health_check(), indent=2))
    
    # Тестовые сообщения
    test_messages = [
        "Привет! Как дела?",
        "Расскажи о CrewAI",
        "Что такое RAG и как он работает?"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*50}")
        print(f"User: {msg}")
        print(f"Agent: {quick_chat(msg, agent)}")
