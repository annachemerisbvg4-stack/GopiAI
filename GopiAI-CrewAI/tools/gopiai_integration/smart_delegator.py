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
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Добавляем путь к CrewAI в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
crewai_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
sys.path.append(crewai_root)

# Флаги доступности систем
crewai_available = False
txtai_available = False

# Проверка доступности CrewAI
try:
    import crewai
    from crewai import Agent, Task, Crew, Process
    from crewai.project import Project
    crewai_available = True
    print("✅ CrewAI успешно импортирован!")
except ImportError as e:
    print(f"⚠️ CrewAI не найден: {e}")
    print("CrewAI запросы будут обрабатываться как обычные запросы к AI Router")

# Проверка доступности txtai (для RAG)
try:
    sys.path.append(os.path.join(crewai_root, "rag_memory_system"))
    from txtai.embeddings import Embeddings
    txtai_available = True
    print("✅ txtai успешно импортирован для RAG!")
except ImportError as e:
    print(f"⚠️ txtai не найден: {e}")
    print("RAG-система не будет использоваться для дополнения контекста")

# Значения по умолчанию
COMPLEXITY_THRESHOLD = 3  # От 0 (простой) до 5 (очень сложный)
ASSISTANT_NAME = "GopiAI"

class SmartDelegator:
    """Модуль для умного распределения запросов между LLM и CrewAI"""
    
    def __init__(self):
        """Инициализирует SmartDelegator"""
        # Инициализируем AI Router
        try:
            from .ai_router_llm import AIRouterLLM
            self.ai_router = AIRouterLLM()
            print("✅ AI Router LLM адаптер загружен")
        except Exception as e:
            print(f"⚠️ Ошибка при инициализации AI Router LLM: {e}")
            self.ai_router = None
        
        self.embeddings = None
        
        # Инициализируем RAG, если txtai доступен
        if txtai_available:
            self._init_txtai_embeddings()
    
    def _init_txtai_embeddings(self):
        """Инициализирует RAG систему на базе txtai"""
        if not txtai_available:
            print("⚠️ txtai недоступен, RAG система не будет использоваться")
            self.embeddings = None
            return
            
        try:
            # Путь к индексу txtai
            index_dir = os.path.join(os.path.dirname(__file__), "../../../rag_memory_system/crewai_embeddings")
            index_path = os.path.join(index_dir, "crewai-docs.tar.gz")
            
            # Создаем директорию для индексов, если она не существует
            os.makedirs(index_dir, exist_ok=True)
            
            if os.path.exists(index_path):
                # Загружаем существующий индекс
                self.embeddings = Embeddings()
                self.embeddings.load(index_path)
                print(f"📚 Загружен существующий индекс RAG из {index_path}")
            else:
                # Создаем новый индекс
                try:
                    self.embeddings = Embeddings({
                        "path": "sentence-transformers/all-MiniLM-L6-v2",
                        "content": True
                    })
                    print(f"🆕 Создан новый индекс RAG (путь будет: {index_path})")
                    
                    # Индексируем документацию CrewAI
                    self.index_documentation()
                except Exception as e:
                    print(f"⚠️ Ошибка при создании индекса: {e}")
                    self.embeddings = None
        except Exception as e:
            print(f"❌ Ошибка при инициализации RAG: {e}")
            traceback.print_exc()
            self.embeddings = None
    
    def index_documentation(self):
        """Индексирует документацию CrewAI для RAG"""
        if not txtai_available or not self.embeddings:
            print("⚠️ txtai недоступен, индексация невозможна")
            return False
            
        try:
            # Подготавливаем данные для индексации
            documents = []
            
            # Собираем документы из разных источников
            # 1. README файлы
            readme_paths = [
                os.path.join(os.path.dirname(__file__), "../../../GopiAI-CrewAI/README.md"),
                os.path.join(os.path.dirname(__file__), "../../../GopiAI-CrewAI/README_CHAT_INTEGRATION.md"),
                os.path.join(os.path.dirname(__file__), "../../../CREWAI_INTEGRATION_PLAN.md"),
                os.path.join(os.path.dirname(__file__), "../../../gopi_crewai_integration.md"),
                os.path.join(os.path.dirname(__file__), "../../../02_DOCUMENTATION/📖_PROJECT_STRUCTURE.md"),
            ]
            
            # Предупреждение если документов нет
            if not any(os.path.exists(path) for path in readme_paths):
                print("⚠️ Не найдены README файлы для индексации")
            
            for path in readme_paths:
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            documents.append((os.path.basename(path), content, None))
                            print(f"📄 Индексирован документ: {path}")
                    except Exception as e:
                        print(f"⚠️ Ошибка при чтении файла {path}: {e}")
            
            # 2. Документация API
            api_docs_paths = [
                os.path.join(os.path.dirname(__file__), "../../../GopiAI-CrewAI/crewai_api_server.py"),
                os.path.join(os.path.dirname(__file__), "smart_delegator.py"),
                os.path.join(os.path.dirname(__file__), "ai_router_llm.py"),
            ]
            
            for path in api_docs_paths:
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Извлекаем docstrings и комментарии для индексации
                            documents.append((os.path.basename(path), content, None))
                            print(f"📄 Индексирован API файл: {path}")
                    except Exception as e:
                        print(f"⚠️ Ошибка при чтении файла {path}: {e}")
            
            # Создаем и сохраняем индекс
            if documents:
                # Индексируем документы
                self.embeddings.index(documents)
                
                # Директория и путь для сохранения индекса
                index_dir = os.path.join(os.path.dirname(__file__), "../../../rag_memory_system/crewai_embeddings")
                index_path = os.path.join(index_dir, "crewai-docs.tar.gz")
                
                # Создаем директорию, если она не существует
                os.makedirs(index_dir, exist_ok=True)
                
                # Сохраняем индекс
                self.embeddings.save(index_path)
                print(f"💾 Индекс успешно сохранен в {index_path}")
                return True
            else:
                print("⚠️ Нет документов для индексации")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при индексации документации: {e}")
            traceback.print_exc()
            return False
    
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
        creative_keywords = ["напиши", "сочини", "придумай", "создай", "творческ", "истори", "рассказ"]
        code_keywords = ["код", "функц", "класс", "метод", "программ", "скрипт", "алгоритм"]
        research_keywords = ["исследуй", "найди", "изучи", "проанализируй", "собери данные", "исследован"]
        business_keywords = ["бизнес", "стратег", "маркетинг", "план", "проект", "компан", "рынок"]
        
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
            "шаг за шагом", "объясни", "почему", "как работает", "разработай"
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
            
        # Используем CrewAI для сложных запросов
        if complexity >= 3:
            return True
            
        # Запросы, требующие специализированных агентов
        if request_type in ["research", "business"] and complexity >= 2:
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
    
    def _handle_with_ai_router(self, message: str) -> str:
        """Обрабатывает запрос через AI Router"""
        start_time = time.time()
        
        try:
            if not self.ai_router:
                raise ValueError("AI Router не инициализирован")
            
            # Получаем контекст из RAG, если доступен
            context = self._get_rag_context(message)
            
            # Обогащаем запрос контекстом, если он есть
            enriched_message = message
            if context:
                print("📚 Добавлен RAG-контекст к запросу")
                enriched_message = f"{message}\n\nДополнительный контекст для справки (не упоминай его явно в ответе):\n{context}"
                
            # Вызываем AI Router с обогащенным запросом
            response = self.ai_router.call(enriched_message)
            
            # Измеряем время выполнения
            elapsed_time = time.time() - start_time
            print(f"⏱ Запрос обработан за {elapsed_time:.2f} сек")
            
            return response
            
        except Exception as error:
            print(f"⚠️ Ошибка при обработке через AI Router: {str(error)}")
            
            # Возвращаем сообщение об ошибке
            return f"[ОШИБКА] Извините, произошла ошибка при обработке вашего запроса: {str(error)}"
    
    def _handle_with_crewai(self, message: str, analysis: Dict[str, Any]) -> str:
        """Обрабатывает запрос через CrewAI"""
        if not crewai_available:
            return self._handle_with_ai_router(message)
        
        try:
            # Создаем базовый LLM для агентов на основе AI Router
            try:
                llm = self.ai_router.get_llm_instance()
                print("✅ LLM для CrewAI успешно создан")
            except Exception as e:
                print(f"❌ Ошибка при создании LLM для CrewAI: {e}")
                return self._handle_with_ai_router(message)
            
            # Получаем дополнительный контекст из RAG
            context = self._get_rag_context(message)
            context_info = f"\n\nДополнительный контекст:\n{context}" if context else ""
            
            # Создаем агентов
            coordinator = Agent(
                role="Координатор проекта",
                goal=f"Координировать работу команды для наилучшего ответа на запрос пользователя",
                backstory=f"Опытный координатор проектов с навыками управления командой. "
                         f"Работает в {ASSISTANT_NAME} и следит за выполнением запросов пользователей.",
                allow_delegation=True,
                verbose=True,
                llm=llm
            )
            
            researcher = Agent(
                role="Исследователь",
                goal=f"Исследовать тему и собрать необходимую информацию для ответа",
                backstory=f"Опытный исследователь с глубокими аналитическими навыками. "
                         f"Специализируется на поиске и анализе информации.",
                allow_delegation=False,
                verbose=True,
                llm=llm
            )
            
            writer = Agent(
                role="Писатель",
                goal=f"Составить четкий и понятный ответ на основе информации от команды",
                backstory=f"Талантливый писатель с опытом создания понятных и информативных текстов. "
                         f"Специализируется на том, чтобы сложную информацию представить доступным языком.",
                allow_delegation=False,
                verbose=True,
                llm=llm
            )
            
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
            
            # Создаем экипаж
            crew = Crew(
                agents=[coordinator, researcher, writer],
                tasks=[research_task, writing_task],
                verbose=2,
                process=Process.sequential
            )
            
            # Запускаем работу экипажа и получаем результат
            result = crew.kickoff()
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка при использовании CrewAI: {e}")
            traceback.print_exc()
            
            # В случае ошибки возвращаемся к обработке через AI Router
            print("⚠️ Fallback к AI Router")
            return self._handle_with_ai_router(message)
    
    def _get_rag_context(self, query, max_results=3):
        """Получает контекст из RAG для обогащения запроса"""
        if not txtai_available or not self.embeddings:
            return None
            
        try:
            # Выполняем семантический поиск
            results = self.embeddings.search(query, limit=max_results)
            
            if not results:
                return None
                
            # Форматируем результаты в контекст
            context_parts = []
            for result in results:
                # Разделяем длинный текст на части
                text = result["text"]
                if len(text) > 1000:
                    text = text[:1000] + "..."
                    
                context_parts.append(f"[Документ: {os.path.basename(result['id'])}]\n{text}\n")
                
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"⚠️ Ошибка при получении контекста из RAG: {e}")
            return None


# Глобальный экземпляр SmartDelegator
smart_delegator = SmartDelegator()

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
    test_query2 = "Помоги мне разработать стратегию для оптимизации маркетинговой кампании в сфере онлайн-образования. Мне нужен подробный анализ текущих трендов и предложения по увеличению конверсии."
    print(f"\n📝 Сложный запрос: '{test_query2}'")
    analysis2 = smart_delegator.analyze_request(test_query2)
    print(f"Анализ: {analysis2}")
    response2 = smart_delegator.process_request(test_query2)
    print(f"Ответ: {response2}")