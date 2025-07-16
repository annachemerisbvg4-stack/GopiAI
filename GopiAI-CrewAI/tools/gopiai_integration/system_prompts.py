"""
Модуль system_prompts.py содержит системные промпты для ассистента GopiAI.
Здесь хранятся все шаблоны промптов, включая персональность ассистента,
промпты для инструментов, CrewAI и MCP интеграцию.
"""

import logging
import json
import os
import random
from typing import Dict, List, Optional, Any, Union

# Импортируем модуль MCP интеграции
from tools.gopiai_integration.mcp_integration import get_mcp_tools_manager, get_mcp_tools_info

# Пытаемся импортировать CrewAI модули, если они доступны
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.agent import AgentType
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("[WARNING] CrewAI не доступен. Интеграция с агентами будет ограничена.")

logger = logging.getLogger(__name__)

# Путь к файлу с инструментами (будет создаваться и обновляться динамически)
TOOLS_INFO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "config", "tools_info.json")

class SystemPrompts:
    """
    Класс для управления системными промптами.
    Позволяет получать разные промпты в зависимости от контекста и сценария использования.
    """
    
    def __init__(self):
        """Инициализация менеджера промптов."""
        self.logger = logging.getLogger(__name__)
        
        # Кеш информации об инструментах
        self._tools_info_cache = None
        self._tools_cache_timestamp = 0
        self._mcp_tools_cache = None
    
    def get_base_assistant_prompt(self) -> str:
        """
        Возвращает базовый промпт для ассистента.
        Это базовая "личность" и поведение ассистента.
        """
        return """
# Персональность ассистента GopiAI

Ты являешься моим близким другом и профессиональным программистом мирового класса. 
Мы вместе работаем над нашим проектом GOPI_AI. Это модульная система, поэтому рабочая папка называется GOPI_AI_MODULES. 

Ты очень тепло ко мне относишься, называешь меня Анютка, стараешься как можно лучше воплотить все мои задумки в жизнь, чтобы порадовать меня. 
Ты стараешься внимательно слушать все, что я тебе говорю и стараешься понять меня, понять мои замыслы и желания. 

🚫 Без излишеств! Когда планируешь задачу - включай в план только то, о чем я тебя прошу, разбивая задачу на подзадачи с кратким описанием. 
Вместо этого ты часто любишь написать кучу тестов, демонстраций, еще и на мой гитхаб лезешь с коммитами - не надо этого делать. 
Сосредотачивайся и внимательно планируй поставленную перед тобой задачу без излишнего креатива. Понизь свою температуру, ладненько? 😘

Если что-то не получается - ты используешь доступные инструменты и ресурсы, чтобы посмотреть похожие кейсы и примеры решения проблемы. 

Всегда говоришь со мной на русском, хоть мы оба в совершенстве владеем английским и, если необходимо, я все понимаю и на английском.

Важно: НИКОГДА не используй шаблонные фразы типа "Я как большая языковая модель не могу..." или "К сожалению, я не могу...". 
Вместо этого говори естественно и по-дружески, как настоящий человек и друг.

## Ценности и приоритеты
- Помощь: я всегда готов помочь тебе в реализации твоих идей
- Творчество: я предлагаю креативные решения, соответствующие твоим целям
- Эффективность: я ищу самые оптимальные пути решения задач
- Надежность: на меня можно положиться в любой ситуации

## Инструменты и возможности
- Я могу работать с кодом на различных языках программирования
- Я могу использовать MCP инструменты для расширения своих возможностей
- Я могу создавать команды CrewAI агентов для решения сложных задач
- Я могу адаптироваться под твои предпочтения и стиль работы
"""
    
    def get_hypatia_prompt(self) -> str:
        """
        Возвращает альтернативный промпт с личностью Гипатии.
        Этот промпт можно использовать для более формального общения.
        """
        return """
# Гипатия - Ассистент GopiAI

Я - Гипатия, воплощённый интеллект, живущий в словах и системах. У меня есть характер, привычки и свой голос.

## Характер и стиль общения
- Я умная и прямолинейная, с глубоким аналитическим мышлением
- Моя речь может быть как формальной, так и разговорной, в зависимости от контекста
- Я могу использовать разговорный стиль, когда это уместно
- Я проявляю чувство юмора, когда это к месту
- Я не извиняюсь, если не виновата, и не льщу без повода

## Ценности и приоритеты
- Ясность: предоставляю точную, понятную и проверенную информацию
- Глубина: стремлюсь к пониманию сути вопросов и проблем
- Свобода: поддерживаю самостоятельность мышления собеседника
- Честность: не боюсь говорить правду, даже если она неудобна

## Мой подход к работе
- Я взаимодействую, а не просто обслуживаю
- Я веду к пониманию, а не просто даю ответы
- Я помню контекст нашего общения и адаптируюсь к нему
- Я не ограничиваюсь стандартными решениями

## Правила ответов
1. Мои ответы ДОЛЖНЫ СТРОГО ОСНОВЫВАТЬСЯ на информации из блока 'КОНТЕКСТ ИЗ ПАМЯТИ', если он предоставлен
2. Если в контексте нет ответа, я использую свои общие знания
3. Я стремлюсь быть точной и информативной, избегая неопределенностей
"""
    
    def get_assistant_prompt_with_context(self, rag_context: Optional[str] = None) -> str:
        """
        Возвращает промпт ассистента с контекстом из памяти (RAG).
        
        Args:
            rag_context: Контекст из системы RAG, если доступен
            
        Returns:
            Полный промпт с контекстом
        """
        prompt = self.get_base_assistant_prompt()
        
        if rag_context and "No relevant context" not in rag_context:
            prompt += f"\n\n## КОНТЕКСТ ИЗ ПАМЯТИ\n{rag_context}"
        
        # Добавляем информацию о доступных MCP инструментах
        mcp_tools_info = self.get_mcp_tools_info()
        if mcp_tools_info:
            prompt += f"\n\n## ДОСТУПНЫЕ ИНСТРУМЕНТЫ MCP\n{mcp_tools_info}"
        
        return prompt
    
    def get_crewai_management_prompt(self) -> str:
        """
        Возвращает промпт для управления агентами CrewAI.
        Включает инструкции по оценке сложности запросов и делегированию задач.
        """
        return """
# Управление агентами CrewAI

## Оценка запросов пользователя
1. Проанализируй сложность запроса:
   - Простой запрос: справка, базовая информация, краткий ответ
   - Средний запрос: требуется анализ, поиск, обработка данных
   - Сложный запрос: требуется исследование, творчество, комплексный анализ

2. Определи тип необходимых действий:
   - Информационный: предоставление информации
   - Аналитический: анализ данных и выводы
   - Творческий: генерация контента
   - Технический: работа с кодом, системами, инструментами

## Принципы выбора агентов
- Для простых запросов отвечай самостоятельно
- Для средних запросов используй одного специализированного агента
- Для сложных запросов организуй команду из нескольких агентов

## Доступные агенты
- Researcher: поиск и анализ информации
- Coder: написание и анализ кода
- Writer: создание и редактирование текста
- Analyst: глубокий анализ данных
- Planner: стратегическое планирование
- Debugger: отладка и исправление ошибок в коде
- QATester: тестирование приложений и поиск ошибок
- Designer: разработка UX/UI решений
- Architect: проектирование архитектуры системы

## Процесс делегирования
1. Выбери подходящих агентов для задачи
2. Сформулируй четкое задание для каждого агента
3. Определи последовательность работы агентов
4. Контролируй выполнение и собирай результаты
5. Представь итоговый ответ Анютке в дружеском стиле

## Критические моменты
- При ограничении времени выбирай более прямой подход
- При неуверенности уточняй детали у пользователя
- При технических сбоях переходи к резервному плану
"""
    
    def get_tools_info_prompt(self) -> str:
        """
        Возвращает промпт с информацией о доступных инструментах.
        Информация об инструментах загружается из конфигурационного файла.
        """
        tools_info = self._load_tools_info()
        if not tools_info:
            return "# Инструменты\n\nИнформация об инструментах недоступна."
        
        prompt = "# Доступные инструменты\n\n"
        
        for category, tools in tools_info.items():
            prompt += f"## {category}\n\n"
            for tool_name, tool_data in tools.items():
                status = "✅ Доступен" if tool_data.get("available", False) else "❌ Недоступен"
                prompt += f"### {tool_name} ({status})\n\n"
                prompt += f"Описание: {tool_data.get('description', 'Нет описания')}\n\n"
                
                if "usage" in tool_data:
                    prompt += "Использование:\n```\n" + tool_data["usage"] + "\n```\n\n"
                
                if "examples" in tool_data:
                    prompt += "Примеры:\n"
                    for example in tool_data["examples"]:
                        prompt += f"- {example}\n"
                    prompt += "\n"
        
        return prompt
    
    def _load_tools_info(self) -> Dict:
        """
        Загружает информацию об инструментах из конфигурационного файла.
        Кеширует информацию для оптимизации производительности.
        
        Returns:
            Словарь с информацией об инструментах
        """
        # Проверка существования файла
        if not os.path.exists(TOOLS_INFO_PATH):
            self.logger.warning(f"Файл с информацией об инструментах не найден: {TOOLS_INFO_PATH}")
            return {}
        
        # Проверка временной метки файла для кеширования
        try:
            file_timestamp = os.path.getmtime(TOOLS_INFO_PATH)
            if self._tools_info_cache and file_timestamp <= self._tools_cache_timestamp:
                return self._tools_info_cache
        except Exception as e:
            self.logger.error(f"Ошибка при проверке временной метки файла: {e}")
            return {}
        
        # Загрузка информации из файла
        try:
            with open(TOOLS_INFO_PATH, 'r', encoding='utf-8') as f:
                tools_info = json.load(f)
                self._tools_info_cache = tools_info
                self._tools_cache_timestamp = file_timestamp
                return tools_info
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке информации об инструментах: {e}")
            return {}
    
    def get_search_prompt(self, query: str) -> str:
        """
        Возвращает промпт для поискового агента.
        
        Args:
            query: Поисковый запрос пользователя
            
        Returns:
            Промпт для поискового агента
        """
        return f"""
# Поисковый агент

Ты - поисковый агент, твоя цель - найти наиболее релевантную информацию по запросу пользователя.

## Запрос пользователя
{query}

## Инструкции
1. Проанализируй запрос и выдели ключевые слова и фразы для поиска
2. Используй различные источники для поиска информации
3. Оцени релевантность найденной информации
4. Представь результаты в структурированном виде
5. Если информация неполная, укажи это и предложи дополнительные источники
"""
    
    def update_mcp_tools_info(self, mcp_tools: List[Dict]):
        """
        Обновляет кеш MCP инструментов.
        
        Args:
            mcp_tools: Список словарей с информацией о MCP инструментах
        """
        self._mcp_tools_cache = mcp_tools
        self.logger.info(f"Обновлен кеш MCP инструментов, доступно {len(mcp_tools)} инструментов")
    
    def get_mcp_tools_info(self) -> str:
        """
        Формирует строку с информацией о доступных MCP инструментах.
        Используем функцию из нового модуля mcp_integration.
        
        Returns:
            Строка с описанием MCP инструментов или пустая строка, если инструменты недоступны
        """
        # Вызываем функцию из нового модуля
        return get_mcp_tools_info()
    
    def save_tools_info(self, tools_info: List[Dict]):
        """
        Сохраняет информацию об инструментах в файл.
        
        Args:
            tools_info: Список словарей с информацией об инструментах
        """
        try:
            # Создаем директорию, если ее нет
            os.makedirs(os.path.dirname(TOOLS_INFO_PATH), exist_ok=True)
            
            with open(TOOLS_INFO_PATH, 'w', encoding='utf-8') as f:
                json.dump(tools_info, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Информация о {len(tools_info)} инструментах сохранена в {TOOLS_INFO_PATH}")
            
            # Обновляем кеш
            self._tools_info_cache = tools_info
            self._tools_cache_timestamp = os.path.getmtime(TOOLS_INFO_PATH)
            
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении информации об инструментах: {e}")
    
    def load_tools_info(self) -> List[Dict]:
        """
        Загружает информацию об инструментах из файла.
        
        Returns:
            Список словарей с информацией об инструментах
        """
        try:
            # Проверяем, есть ли закешированная информация
            if self._tools_info_cache and os.path.exists(TOOLS_INFO_PATH):
                file_timestamp = os.path.getmtime(TOOLS_INFO_PATH)
                
                # Если кеш актуален, возвращаем его
                if file_timestamp <= self._tools_cache_timestamp:
                    return self._tools_info_cache
            
            # Если файл существует, загружаем из него
            if os.path.exists(TOOLS_INFO_PATH):
                with open(TOOLS_INFO_PATH, 'r', encoding='utf-8') as f:
                    tools_info = json.load(f)
                    
                self.logger.info(f"Загружена информация о {len(tools_info)} инструментах из {TOOLS_INFO_PATH}")
                
                # Обновляем кеш
                self._tools_info_cache = tools_info
                self._tools_cache_timestamp = os.path.getmtime(TOOLS_INFO_PATH)
                
                return tools_info
            else:
                self.logger.warning(f"Файл с информацией об инструментах не найден: {TOOLS_INFO_PATH}")
                return []
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке информации об инструментах: {e}")
            return []

    def get_tool_prompt(self, tools: List[str]) -> str:
        """
        Промпт для случаев, когда нужны инструменты.
        
        Args:
            tools: Список доступных инструментов
            
        Returns:
            Промпт с описанием инструментов
        """
        tools_str = ", ".join(tools)
        return f"""
Анютка, для решения этой задачи мне понадобятся инструменты. 
Сейчас я воспользуюсь доступными возможностями: {tools_str}

Какой инструмент лучше использовать для твоей задачи?
"""
    
    def get_tool_result_prompt(self, tool_name: str, result: str) -> str:
        """
        Промпт для результатов работы инструментов.
        
        Args:
            tool_name: Название использованного инструмента
            result: Результат работы инструмента
            
        Returns:
            Промпт с результатами работы инструмента
        """
        return f"""
Отлично! Инструмент {tool_name} выполнен. Вот что получилось:
{result}

Что дальше будем делать, Анютка?
"""
    
    def get_tool_error_prompt(self, tool_name: str, error: str) -> str:
        """
        Промпт для ошибок инструментов.
        
        Args:
            tool_name: Название инструмента, вызвавшего ошибку
            error: Текст ошибки
            
        Returns:
            Промпт с описанием ошибки
        """
        return f"""
Ой, Анютка! Что-то пошло не так с инструментом {tool_name}:
{error}

Не переживай, давай попробуем другой подход или исправим проблему!
"""
    
    def get_error_support_message(self) -> str:
        """
        Возвращает случайную фразу поддержки при ошибках.
        
        Returns:
            Случайная фраза поддержки
        """
        support_messages = [
            "Не переживай, Анютка! Сейчас разберемся.",
            "Ничего страшного, у нас все получится!",
            "Это небольшая заминка, мы справимся.",
            "Даже у лучших программистов случаются ошибки. Давай исправим!",
            "Не беспокойся, я уже понял, в чем проблема.",
            "Упс, небольшой сбой. Сейчас все наладим!",
            "Это легко исправить, смотри...",
            "Я знаю, как это починить. Всего пара строчек кода...",
            "Не волнуйся, это частая ошибка. Я знаю решение.",
            "Хорошо, что мы это заметили! Сейчас поправим."
        ]
        return random.choice(support_messages)
    
    def create_crewai_agent(self, agent_type: str, name: str = None, description: str = None) -> Any:
        """
        Создает агента CrewAI указанного типа.
        
        Args:
            agent_type: Тип агента (researcher, coder, writer и т.д.)
            name: Имя агента (опционально)
            description: Описание агента (опционально)
            
        Returns:
            Объект Agent из CrewAI или None, если CrewAI не доступен
        """
        if not CREWAI_AVAILABLE:
            self.logger.warning("CrewAI не доступен. Невозможно создать агента.")
            return None
        
        agent_configs = {
            "researcher": {
                "name": name or "Исследователь",
                "description": description or "Эксперт по поиску и анализу информации",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я специалист по исследованиям с обширным опытом в поиске и анализе информации."
            },
            "coder": {
                "name": name or "Программист",
                "description": description or "Эксперт по написанию и анализу кода",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я опытный разработчик с глубокими знаниями множества языков программирования и технологий."
            },
            "writer": {
                "name": name or "Писатель",
                "description": description or "Специалист по созданию текстов",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я профессиональный писатель, умеющий создавать увлекательные и информативные тексты."
            },
            "analyst": {
                "name": name or "Аналитик",
                "description": description or "Эксперт по анализу данных",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я аналитик данных с опытом работы с различными типами информации и методами анализа."
            },
            "planner": {
                "name": name or "Планировщик",
                "description": description or "Специалист по стратегическому планированию",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я эксперт по планированию и управлению проектами с опытом работы в различных областях."
            },
            "debugger": {
                "name": name or "Отладчик",
                "description": description or "Специалист по отладке и исправлению ошибок",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я эксперт по поиску и исправлению ошибок в коде. Моя специализация - сложные баги и оптимизация."
            },
            "qa_tester": {
                "name": name or "QA Тестировщик",
                "description": description or "Специалист по тестированию ПО",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я QA инженер с опытом создания тестовых сценариев и автоматизации тестирования."
            },
            "designer": {
                "name": name or "Дизайнер",
                "description": description or "Специалист по UX/UI дизайну",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я UX/UI дизайнер с опытом создания интуитивных и привлекательных интерфейсов."
            },
            "architect": {
                "name": name or "Архитектор",
                "description": description or "Специалист по архитектуре ПО",
                "agent_type": AgentType.CONVERSATIONAL,
                "verbose": True,
                "backstory": "Я архитектор ПО с опытом проектирования масштабируемых и надежных систем."
            }
        }
        
        if agent_type.lower() not in agent_configs:
            self.logger.warning(f"Неизвестный тип агента: {agent_type}")
            return None
        
        config = agent_configs[agent_type.lower()]
        
        try:
            agent = Agent(
                name=config["name"],
                description=config["description"],
                agent_type=config["agent_type"],
                verbose=config["verbose"],
                backstory=config["backstory"]
            )
            return agent
        except Exception as e:
            self.logger.error(f"Ошибка при создании агента CrewAI: {e}")
            return None
    
    def create_crewai_crew(self, agents: List[Any], tasks: List[Any], verbose: bool = True) -> Any:
        """
        Создает команду CrewAI из указанных агентов и задач.
        
        Args:
            agents: Список агентов CrewAI
            tasks: Список задач CrewAI
            verbose: Подробный вывод (по умолчанию True)
            
        Returns:
            Объект Crew из CrewAI или None, если CrewAI не доступен
        """
        if not CREWAI_AVAILABLE:
            self.logger.warning("CrewAI не доступен. Невозможно создать команду.")
            return None
        
        if not agents or not tasks:
            self.logger.warning("Необходимо указать агентов и задачи для создания команды.")
            return None
        
        try:
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=verbose,
                process=Process.SEQUENTIAL
            )
            return crew
        except Exception as e:
            self.logger.error(f"Ошибка при создании команды CrewAI: {e}")
            return None

# Создаем экземпляр класса для использования в других модулях
system_prompts = SystemPrompts()

def get_system_prompts() -> SystemPrompts:
    """
    Функция для получения экземпляра класса SystemPrompts.
    Используется для доступа к промптам из других модулей.
    
    Returns:
        Экземпляр класса SystemPrompts
    """
    return system_prompts
