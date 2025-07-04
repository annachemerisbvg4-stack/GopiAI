#!/usr/bin/env python3
"""
🧠 Smart Delegator для GopiAI

Анализирует запросы пользователей и решает, как их обрабатывать:
1. Простые запросы: прямой ответ через AI Router
2. Сложные запросы: делегирование команде специализированных агентов CrewAI
"""

import os
import sys
import time
import json
import traceback
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
try:
    from .ai_router_llm import AIRouterLLM
    from .self_reflection import ReflectionEnabledAIRouter
except ImportError:
    AIRouterLLM = None
    ReflectionEnabledAIRouter = None

import logging

# Добавляем путь к CrewAI в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
crewai_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
sys.path.append(crewai_root)

# Флаги доступности систем
crewai_available = False # This will be set by the try-except block below
RAG_API_URL = "http://127.0.0.1:5051" # URL для нашего нового RAG-сервиса
RAG_TIMEOUT = int(os.environ.get('GOPIAI_RAG_TIMEOUT', 4))  # Таймаут для RAG запросов

# Проверка доступности CrewAI
try:
    import crewai
    from crewai import Agent, Task, Crew, Process
    crewai_available = True
    print("✅ CrewAI успешно импортирован!")
except ImportError as e:
    print(f"⚠️ CrewAI не найден: {e}")
    print("CrewAI запросы будут обрабатываться как обычные запросы к AI Router")

def is_rag_service_available():
    """Проверяет доступность RAG-сервиса."""
    try:
        response = requests.get(f"{RAG_API_URL}/api/health", timeout=min(RAG_TIMEOUT, 2))
        return response.status_code == 200 and response.json().get("status") == "online"
    except requests.exceptions.RequestException:
        return False

# Значения по умолчанию
COMPLEXITY_THRESHOLD = 3  # От 0 (простой) до 5 (очень сложный)
ASSISTANT_NAME = "GopiAI"
RAG_DISABLE_TIMEOUT = 300  # seconds

# Конфигурация CrewAI для оптимизации
CREWAI_CONFIG = {
    'max_iterations': 3,  # Ограничиваем количество итераций
    'max_rpm': 10,  # Ограничиваем количество запросов в минуту
    'agent_cache_timeout': 600,  # Кэшируем агентов на 10 минут
    'allow_delegation': True,  # Разрешаем делегирование, но контролируем
    'verbose': False,  # Отключаем verbose для production
    'memory_enabled': True  # Включаем память для агентов
}

class SmartDelegator:
    """Модуль для умного распределения запросов между LLM и CrewAI"""
    
    def __init__(self, enable_reflection=True, reflection_config=None):
        """Инициализирует SmartDelegator"""
        self.logger = logging.getLogger(__name__)
        
        # Кэш для агентов CrewAI
        self._agent_cache = {}
        self._agent_cache_timestamps = {}
        self._crew_cache = {}
        self._crew_cache_timestamps = {}
        
        # Конфигурация саморефлексии
        self.enable_reflection = enable_reflection
        self.reflection_config = reflection_config or {
            'min_quality_threshold': 8.0,
            'max_iterations': 3
        }
        
        # Инициализируем AI Router
        try:
            if AIRouterLLM is None or ReflectionEnabledAIRouter is None:
                raise ImportError("AI Router modules not available")
            
            base_ai_router = AIRouterLLM()
            
            # Если саморефлексия включена, оборачиваем AI Router
            if self.enable_reflection:
                self.ai_router = ReflectionEnabledAIRouter(
                    ai_router=base_ai_router,
                    enable_reflection=True,
                    reflection_config=self.reflection_config
                )
                print(f"✅ AI Router с саморефлексией загружен (порог качества: {self.reflection_config['min_quality_threshold']})")
            else:
                self.ai_router = base_ai_router
                print("✅ AI Router LLM адаптер загружен (без саморефлексии)")
                
        except Exception as e:
            print(f"⚠️ Ошибка при инициализации AI Router LLM: {e}")
            self.ai_router = None
        
        self.rag_available = is_rag_service_available()
        self._rag_last_failure = 0  # Initialize RAG failure tracking
        if self.rag_available:
            print("✅ RAG-сервис доступен. Запускаем индексацию в фоновом режиме...")
            self.index_documentation() # Запускаем индексацию при старте
        else:
            print("⚠️ RAG-сервис недоступен. Контекст из документов не будет добавляться.")
    
    def index_documentation(self):
        """Отправляет запрос на индексацию документов на RAG-сервер."""
        if not self.rag_available:
            print("⚠️ RAG-сервис недоступен, индексация невозможна.")
            return False

        def do_index():
            try:
                response = requests.post(f"{RAG_API_URL}/api/index", timeout=120) # 2-минутный таймаут
                if response.status_code == 200:
                    print(f"✅ Ответ от RAG-сервиса по индексации: {response.json().get('message')}")
                else:
                    print(f"⚠️ Ошибка при индексации на RAG-сервисе: {response.status_code} {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Не удалось подключиться к RAG-сервису для индексации: {e}")

        # Запускаем в фоновом потоке, чтобы не блокировать старт сервера
        import threading
        threading.Thread(target=do_index, daemon=True).start()
        return True

    def _get_rag_context(self, query: str, max_results: int = 3) -> Optional[str]:
        """Получает контекст из RAG-сервиса для обогащения запроса."""
        if not self.rag_available:
            return None

        if time.time() - self._rag_last_failure < RAG_DISABLE_TIMEOUT:
            return None

        try:
            response = requests.post(f"{RAG_API_URL}/api/search", json={"query": query, "max_results": max_results}, timeout=RAG_TIMEOUT)
            if response.status_code == 200:
                return response.json().get("context")
            else:
                print(f"⚠️ Ошибка при получении контекста из RAG-сервиса: {response.status_code} {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ошибка при подключении к RAG-сервису: {e}")
            self._rag_last_failure = time.time()
            traceback.print_exc()
            return None
    
    def analyze_request(self, message: str) -> Dict[str, Any]:
        """
        Анализирует запрос пользователя и определяет его сложность
        
        Возвращает:
            dict: Словарь с результатами анализа
        """
        start_time = time.time()
        
        # Базовый анализ
        message_lower = message.lower()
        
        # Определяем тип запроса
        request_type = self._detect_request_type(message_lower)
        
        # Определяем сложность (0-5)
        complexity = self._calculate_complexity(message_lower)
        
        # Определяем, требуется ли CrewAI
        requires_crewai = self._should_use_crewai(complexity, request_type, message_lower)
        
        # Вычисляем затраченное время
        elapsed_time = time.time() - start_time
        
        # Формируем результат
        result = {
            "complexity": complexity,
            "type": request_type,
            "requires_crewai": requires_crewai and crewai_available,
            "analysis_time": elapsed_time
        }
        
        print(f"📊 Анализ запроса: сложность={complexity}, тип={request_type}, CrewAI={requires_crewai and crewai_available}")
        
        return result
    
    def _detect_request_type(self, message_lower: str) -> str:
        """Определяет тип запроса на основе текста"""
        
        # Категории запросов
        creative_keywords = ["напиши", "сочини", "придумай", "создай", "творческ", "истори", "рассказ", "генерируй", "создание", "креатив"]
        code_keywords = ["код", "функц", "класс", "метод", "программ", "скрипт", "алгоритм", "разработай", "реализуй", "отладка", "баг", "ошибка"]
        research_keywords = ["исследуй", "найди", "изучи", "проанализируй", "собери данные", "исследован", "анализ", "обзор", "информация", "факты", "статистика", "данные", "сравни", "выяви", "определи"]
        business_keywords = ["бизнес", "стратег", "маркетинг", "план", "проект", "компан", "рынок", "финанс", "продажи", "клиент", "управлени", "оптимизац", "развитие", "эффективность"]
        
        # Проверяем по ключевым словам
        if any(kw in message_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in message_lower for kw in code_keywords):
            return "code"
        elif any(kw in message_lower for kw in research_keywords):
            return "research"
        elif any(kw in message_lower for kw in business_keywords):
            return "business"
        else:
            return "general"
            
    def _calculate_complexity(self, message_lower: str) -> int:
        """
        Рассчитывает примерную сложность запроса по шкале от 0 до 5
        
        Факторы, влияющие на сложность:
        - Длина сообщения
        - Количество вопросов/задач
        - Наличие специфических ключевых слов
        """
        complexity = 0
        
        # Длина сообщения
        message_length = len(message_lower)
        if message_length > 500:
            complexity += 2
        elif message_length > 200:
            complexity += 1
            
        # Количество вопросов
        question_count = message_lower.count("?")
        if question_count > 3:
            complexity += 2
        elif question_count > 1:
            complexity += 1
            
        # Ключевые слова, указывающие на сложность
        complexity_indicators = [
            "сложн", "многоэтапн", "комплексн", "детальн", "подробн",
            "анализ", "сравни", "исследуй", "оптимизируй", "стратеги",
            "шаг за шагом", "объясни", "почему", "как работает", "разработай",
            "глубокий", "всесторонний", "всеобъемлющий", "перспектив", "прогноз",
            "рекомендац", "решение", "проблем", "кейс", "сценарий", "влияние",
            "фактор", "метрика", "показатель", "оценка", "критерий", "методология",
            "фреймворк", "архитектур", "интеграц", "взаимодействи", "оптимизац",
            "масштабирован", "безопасность", "производительность", "эффективность",
            "аналитик", "эксперт", "специалист", "консультант", "отчет", "доклад",
            "презентац", "план", "дорожная карта", "бюджет", "риск", "возможность",
            "тренд", "инновац", "будущее", "развитие", "эволюция", "трансформац",
            "глобальн", "международн", "кросс-культурн", "мультидисциплинарн"
        ]
        
        indicators_found = sum(1 for ind in complexity_indicators if ind in message_lower)
        complexity += min(indicators_found, 2)
        
        return min(complexity, 5)  # Максимум 5
        
    def _should_use_crewai(self, complexity: int, request_type: str, message_lower: str) -> bool:
        """Определяет, следует ли использовать CrewAI для обработки запроса"""
        
        # Проверяем наличие явных указаний на использование CrewAI
        explicit_crewai_request = any(kw in message_lower for kw in [
            "используй crewai", "через crewai", "командой агентов", 
            "многоагентн", "несколько агентов", "группой"
        ])
        
        if explicit_crewai_request:
            return True
            
        # Используем CrewAI для сложных запросов (оптимизировано)
        if complexity >= 3:  # Повышаем порог для избежания излишней обработки
            return True
            
        # Запросы, требующие специализированных агентов (более строгие условия)
        if request_type in ["research", "business"] and complexity >= 3:
            return True
            
        # Запросы, явно требующие многоэтапной обработки
        multi_step_indicators = [
            "поэтапно", "пошагово", "последовательно", "сначала", "затем", 
            "после этого", "в несколько этапов", "многоэтапный", "комплексный план"
        ]
        if any(indicator in message_lower for indicator in multi_step_indicators) and complexity >= 2:
            return True
            
        # По умолчанию - не используем CrewAI
        return False
    
    def process_request(self, message: str) -> str:
        """
        Обрабатывает запрос пользователя через AI Router или CrewAI
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            str: Ответ на запрос пользователя
        """
        start_time = time.time()
        
        try:
            # Анализируем запрос
            analysis = self.analyze_request(message)
            
            # Логируем результаты анализа
            print(f"📊 Анализ запроса: сложность={analysis['complexity']}, тип={analysis['type']}, CrewAI={analysis['requires_crewai']}")
            
            # Выбираем способ обработки запроса
            if analysis["requires_crewai"]:
                # Используем CrewAI для сложных запросов
                response = self._handle_with_crewai(message, analysis)
            else:
                # Используем AI Router для простых запросов
                response = self._handle_with_ai_router(message)
            
            # Логируем время обработки
            elapsed = time.time() - start_time
            print(f"⏱ Запрос обработан за {elapsed:.2f} сек")
            
            return response
            
        except Exception as e:
            print(f"❌ Ошибка при обработке запроса: {e}")
            traceback.print_exc()
            return f"Произошла ошибка при обработке запроса: {str(e)}"
    
    def clear_agent_cache(self):
        """Очищает кэш агентов"""
        self._agent_cache.clear()
        self._agent_cache_timestamps.clear()
        self._crew_cache.clear()
        self._crew_cache_timestamps.clear()
        print("🧹 Кэш агентов CrewAI очищен")
    
    def get_cache_stats(self) -> Dict:
        """Возвращает статистику кэша агентов"""
        current_time = time.time()
        active_agents = sum(
            1 for timestamp in self._agent_cache_timestamps.values()
            if current_time - timestamp < CREWAI_CONFIG['agent_cache_timeout']
        )
        
        return {
            'cached_agents': len(self._agent_cache),
            'active_cached_agents': active_agents,
            'cache_timeout': CREWAI_CONFIG['agent_cache_timeout'],
            'total_cache_hits': getattr(self, '_cache_hits', 0)
        }
    
    def _handle_with_ai_router(self, message: str) -> str:
        """Обрабатывает запрос через AI Router"""
        start_time = time.time()
        
        try:
            self.logger.info("🔍 Проверка AI Router...")
            if not self.ai_router:
                self.logger.error("❌ AI Router не найден (self.ai_router is None)")
                raise ValueError("AI Router не инициализирован")
            
            self.logger.info("✅ AI Router проверки пройдены")

            # Получаем контекст из RAG, если доступен
            context = self._get_rag_context(message)

            # Обогащаем запрос контекстом, если он есть
            enriched_message = message
            if context:
                self.logger.info("📚 Добавлен RAG-контекст к запросу")
                enriched_message = f"""{message}

Дополнительный контекст для справки (не упоминай его явно в ответе):
{context}"""

            # Вызываем AI Router с обогащенным запросом
            try:
                self.logger.info("🚀 Вызов AI Router...")
                result = self.ai_router._generate(prompts=[enriched_message])
                response = result.generations[0][0].text
                self.logger.info("✅ Ответ от AI Router получен")
            except Exception as inner_error:
                self.logger.error(f"❌ Ошибка при вызове AI Router: {inner_error}")
                traceback.print_exc()
                # Возвращаем базовый ответ
                return f"Извините, я не смог обработать ваш запрос через AI маршрутизатор. Пожалуйста, попробуйте позже или обратитесь к администратору системы. (Ошибка: {str(inner_error)})"
            
            # Измеряем время выполнения
            elapsed_time = time.time() - start_time
            self.logger.info(f"⏱ Запрос обработан за {elapsed_time:.2f} сек")
            
            return response
            
        except Exception as error:
            self.logger.error(f"⚠️ Ошибка при обработке через AI Router: {str(error)}")
            traceback.print_exc()
            
            # Возвращаем сообщение об ошибке
            return f"[ОШИБКА] Извините, произошла ошибка при обработке вашего запроса: {str(error)}"
    
    def _get_cached_agents(self, message_hash: str):
        """Получает закэшированных агентов для повторного использования"""
        current_time = time.time()
        
        # Проверяем кэш агентов
        if (message_hash in self._agent_cache and 
            current_time - self._agent_cache_timestamps.get(message_hash, 0) < CREWAI_CONFIG['agent_cache_timeout']):
            return self._agent_cache[message_hash]
            
        return None
    
    def _cache_agents(self, message_hash: str, agents: dict):
        """Кэширует агентов для повторного использования"""
        self._agent_cache[message_hash] = agents
        self._agent_cache_timestamps[message_hash] = time.time()
        
        # Очищаем старые записи из кэша
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._agent_cache_timestamps.items()
            if current_time - timestamp > CREWAI_CONFIG['agent_cache_timeout']
        ]
        for key in expired_keys:
            self._agent_cache.pop(key, None)
            self._agent_cache_timestamps.pop(key, None)
    
    def _handle_with_crewai(self, message: str, analysis: Dict[str, Any]) -> str:
        """Обрабатывает запрос через CrewAI с оптимизацией"""
        if not crewai_available:
            return self._handle_with_ai_router(message)
        
        try:
            # Создаем базовый LLM для агентов на основе AI Router
            try:
                if self.ai_router is None:
                    print("❌ AI Router не инициализирован")
                    return self._handle_with_ai_router(message)
                
                # Получаем экземпляр LLM без вызова как функции
                llm = self.ai_router.get_llm_instance()
                print("✅ LLM для CrewAI успешно создан")
            except Exception as e:
                print(f"❌ Ошибка при создании LLM для CrewAI: {e}")
                return self._handle_with_ai_router(message)
            
            # Получаем дополнительный контекст из RAG
            context = self._get_rag_context(message)
            context_info = f"\n\nДополнительный контекст:\n{context}" if context else ""
            
            # Создаем хэш для кэширования агентов
            import hashlib
            message_hash = hashlib.md5(f"{analysis['type']}_{analysis['complexity']}".encode()).hexdigest()
            
            # Проверяем кэш агентов
            cached_agents = self._get_cached_agents(message_hash)
            if cached_agents:
                print("✅ Используем закэшированных агентов CrewAI")
                coordinator = cached_agents['coordinator']
                researcher = cached_agents['researcher'] 
                writer = cached_agents['writer']
            else:
                print("🔄 Создаем новых агентов CrewAI")
                # Создаем агентов с оптимизированной конфигурацией
                coordinator = Agent(
                    role="Координатор проекта",
                    goal=f"Координировать работу команды для наилучшего ответа на запрос пользователя",
                    backstory=f"Опытный координатор проектов с навыками управления командой. "
                    f"Работает в {ASSISTANT_NAME} и следит за выполнением запросов пользователей.",
                    allow_delegation=CREWAI_CONFIG['allow_delegation'],
                    verbose=CREWAI_CONFIG['verbose'],
                    max_iter=CREWAI_CONFIG['max_iterations'],
                    max_rpm=CREWAI_CONFIG['max_rpm'],
                    llm=llm
                )

                researcher = Agent(
                    role="Исследователь",
                    goal=f"Исследовать тему и собрать необходимую информацию для ответа",
                    backstory=f"Опытный исследователь с глубокими аналитическими навыками.",
                    allow_delegation=False,  # Исследователь не делегирует
                    verbose=CREWAI_CONFIG['verbose'],
                    max_iter=CREWAI_CONFIG['max_iterations'],
                    max_rpm=CREWAI_CONFIG['max_rpm'],
                    llm=llm
                )
                
                writer = Agent(
                    role="Писатель",
                    goal=f"Составить четкий и понятный ответ на основе информации от команды",
                    backstory=f"Талантливый писатель с опытом создания понятных и информативных текстов. "
                    f"Специализируется на том, чтобы сложную информацию представить доступным языком.",
                    allow_delegation=False,  # Писатель не делегирует
                    verbose=CREWAI_CONFIG['verbose'],
                    max_iter=CREWAI_CONFIG['max_iterations'],
                    max_rpm=CREWAI_CONFIG['max_rpm'],
                    llm=llm
                )
                
                # Кэшируем агентов для повторного использования
                agents_to_cache = {
                    'coordinator': coordinator,
                    'researcher': researcher,
                    'writer': writer
                }
                self._cache_agents(message_hash, agents_to_cache)
            
            # Создаем задачи
            research_task = Task(
                description=f"Исследуй запрос пользователя: '{message}'{context_info}\n\n"
                f"Проведи тщательное исследование темы и собери всю необходимую информацию "
                f"для полного и точного ответа. Определи ключевые аспекты запроса и структурируй "
                f"свои выводы для дальнейшей обработки.",
                expected_output="Структурированный отчет с результатами исследования",
                agent=researcher
            )
            
            writing_task = Task(
                description=f"На основе результатов исследования составь полный ответ на запрос пользователя: "
                f"'{message}'\n\nИспользуй информацию от исследователя, чтобы создать четкий, "
                f"информативный и понятный ответ. Структурируй информацию логично. "
                f"Ответ должен быть дружелюбным и полезным.",
                expected_output="Готовый ответ для пользователя",
                agent=writer,
                context=[research_task]
            )
            
            # Создаем экипаж с оптимизированной конфигурацией
            crew = Crew(
                agents=[coordinator, researcher, writer],
                tasks=[research_task, writing_task],
                verbose=CREWAI_CONFIG['verbose'],
                process=Process.sequential,  # Используем последовательный процесс для простоты
                memory=CREWAI_CONFIG['memory_enabled'],  # Включаем память для агентов
                max_rpm=CREWAI_CONFIG['max_rpm']  # Ограничиваем количество запросов
            )
            
            # Запускаем работу экипажа и получаем результат
            result = crew.kickoff()
            
            return str(result)
            
        except Exception as e:
            print(f"❌ Ошибка при использовании CrewAI: {e}")
            traceback.print_exc()
            
            # В случае ошибки возвращаемся к обработке через AI Router
            print("⚠️ Fallback к AI Router")
            return self._handle_with_ai_router(message)

    
    def set_reflection_enabled(self, enabled: bool):
        """Включает/выключает саморефлексию"""
        self.enable_reflection = enabled
        if hasattr(self.ai_router, 'set_reflection_enabled'):
            self.ai_router.set_reflection_enabled(enabled)
            self.logger.info(f"🔄 Саморефлексия {'включена' if enabled else 'выключена'}")
        else:
            self.logger.warning("⚠️ AI Router не поддерживает управление саморефлексией")
    
    def update_reflection_config(self, config: Dict):
        """Обновляет конфигурацию саморефлексии"""
        self.reflection_config.update(config)
        if hasattr(self.ai_router, 'update_reflection_config'):
            self.ai_router.update_reflection_config(config)
            self.logger.info(f"🔧 Конфигурация саморефлексии обновлена: {config}")
        else:
            self.logger.warning("⚠️ AI Router не поддерживает обновление конфигурации саморефлексии")
    
    def get_reflection_stats(self) -> Dict:
        """Возвращает статистику по саморефлексии"""
        if self.ai_router and hasattr(self.ai_router, 'get_reflection_stats'):
            return self.ai_router.get_reflection_stats()
        else:
            return {
                'reflection_enabled': self.enable_reflection,
                'reflection_config': self.reflection_config,
                'note': 'AI Router не поддерживает детальную статистику саморефлексии'
            }


# Глобальный экземпляр SmartDelegator
# Создаем SmartDelegator с включенной саморефлексией
# Конфигурация саморефлексии:
# - min_quality_threshold: минимальная оценка качества (8.0 из 10)
# - max_iterations: максимальное количество попыток улучшения (3)
reflection_config = {
    'min_quality_threshold': 8.0,  # Требуем высокое качество ответов
    'max_iterations': 3            # Максимум 3 попытки улучшения
}

smart_delegator = SmartDelegator(
    enable_reflection=True,
    reflection_config=reflection_config
)

# Для тестирования, если запущен напрямую
if __name__ == "__main__":
    print("🧪 Тестирование Smart Delegator")
    
    # Простой запрос
    test_query1 = "Привет, как дела?"
    print(f"\n📝 Простой запрос: '{test_query1}'")
    analysis1 = smart_delegator.analyze_request(test_query1)
    print(f"Анализ: {analysis1}")
    response1 = smart_delegator.process_request(test_query1)
    print(f"Ответ: {response1}")
    
    # Сложный запрос
    test_query2 = "Помоги мне разработать стратегию для оптимизации маркетинговой кампании в сфере онлайн-образования. Мне нужен подробный поэтапный план с анализом рынка и целевой аудитории."
    print(f"\n📝 Сложный запрос: '{test_query2}'")
    analysis2 = smart_delegator.analyze_request(test_query2)
    print(f"Анализ: {analysis2}")
    response2 = smart_delegator.process_request(test_query2)
    print(f"Ответ: {response2}")