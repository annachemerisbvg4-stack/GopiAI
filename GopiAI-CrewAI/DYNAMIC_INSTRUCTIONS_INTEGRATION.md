# 🚀 Система динамических инструкций для CrewAI

## 📋 Обзор

Система динамических инструкций обеспечивает автоматическую подгрузку детальных инструкций для инструментов GopiAI в workflow CrewAI. Это позволяет LLM получать подробную информацию о том, как использовать каждый инструмент, только в момент его выбора, не перегружая системный промпт.

## ✅ Статус интеграции: ЗАВЕРШЕНА

**Результаты тестирования:**
- ✅ ToolsInstructionManager: 5/5 инструментов работают
- ✅ CrewAI Integration: Агенты успешно улучшены
- ✅ SystemPrompts Integration: Функциональность работает
- ✅ Все основные компоненты протестированы и функциональны

## 🏗️ Архитектура системы

### 1. ToolsInstructionManager
**Файл:** `tools/gopiai_integration/tools_instruction_manager.py`

**Функции:**
- `get_tools_summary()` - краткий список инструментов для системного промпта
- `get_tool_detailed_instructions(tool_name)` - детальные инструкции для конкретного инструмента
- Кэширование инструкций для производительности

**Поддерживаемые инструменты:**
- `filesystem_tools` - файловые операции (1682 символа инструкций)
- `local_mcp_tools` - веб-скрапинг и API (2091 символ)
- `browser_tools` - автоматизация браузера (2434 символа)
- `web_search` - поиск в интернете (961 символ)
- `page_analyzer` - анализ веб-страниц (1577 символов)

### 2. CrewAI Tools Integration
**Файл:** `tools/gopiai_integration/crewai_tools_integration.py`

**Основные компоненты:**
- `CrewAIToolsInstructionIntegrator` - основной класс интегратора
- `enhance_agent_with_instructions()` - улучшение агента
- `enhance_crew_with_instructions()` - улучшение команды
- `@with_dynamic_instructions` - декоратор для автоматического улучшения

**Принцип работы:**
1. Перехватывает вызовы методов `_run` инструментов
2. Динамически подгружает детальные инструкции
3. Временно добавляет инструкции в описание инструмента
4. Восстанавливает оригинальное описание после выполнения

### 3. SystemPrompts Integration
**Файл:** `tools/gopiai_integration/system_prompts.py`

**Новые методы:**
- `get_tools_summary_for_prompt()` - краткий список для промпта
- `get_tool_detailed_instructions(tool_name)` - детальные инструкции

## 🔧 Использование

### Базовое использование

```python
from crewai import Agent, Crew, LLM
from tools.gopiai_integration.crewai_tools_integration import enhance_agent_with_instructions
from tools.gopiai_integration.filesystem_tools import GopiAIFileSystemTool

# Создаем агента с инструментами
agent = Agent(
    role='File Manager',
    goal='Управлять файлами с детальными инструкциями',
    backstory='Специалист по работе с файлами',
    tools=[GopiAIFileSystemTool()],
    llm=LLM(model="gemini/gemini-1.5-flash"),
    verbose=True
)

# Улучшаем агента динамическими инструкциями
enhanced_agent = enhance_agent_with_instructions(agent)
```

### Использование с декоратором

```python
from tools.gopiai_integration.crewai_tools_integration import with_dynamic_instructions

@with_dynamic_instructions
def create_enhanced_crew():
    # Создание команды
    crew = Crew(
        agents=[agent1, agent2],
        tasks=[task1, task2],
        verbose=True
    )
    return crew  # Автоматически улучшается декоратором
```

### Улучшение команды

```python
from tools.gopiai_integration.crewai_tools_integration import enhance_crew_with_instructions

# Создаем команду
crew = Crew(agents=agents, tasks=tasks, verbose=True)

# Улучшаем всю команду
enhanced_crew = enhance_crew_with_instructions(crew)

# Запускаем
result = enhanced_crew.kickoff()
```

## 📁 Структура файлов

```
tools/gopiai_integration/
├── tools_instruction_manager.py      # Основной менеджер инструкций
├── crewai_tools_integration.py       # Интеграция с CrewAI
├── example_dynamic_instructions.py   # Пример использования
├── tool_instructions/                # Папка с инструкциями (будущее расширение)
├── system_prompts.py                 # Интеграция с системными промптами
├── filesystem_tools.py               # Файловые инструменты
├── browser_tools.py                  # Браузерные инструменты
├── local_mcp_tools.py                # MCP инструменты
└── ...
```

## 🧪 Тестирование

**Файл тестов:** `test_dynamic_instructions.py`

**Запуск тестов:**
```bash
cd GopiAI-CrewAI
python test_dynamic_instructions.py
```

**Результаты последнего тестирования:**
- ✅ ToolsInstructionManager: Все инструменты загружены
- ✅ CrewAI Integration: Агенты успешно улучшены
- ✅ SystemPrompts Integration: Основная функциональность работает

## 🚀 Интеграция в main.py

Система автоматически интегрирована в основной файл `main.py`:

```python
# Импорт системы динамических инструкций
from tools.gopiai_integration.crewai_tools_integration import (
    enhance_crew_with_instructions,
    enhance_agent_with_instructions
)

# В функции create_demo_agents():
# Улучшаем всех агентов динамическими инструкциями
coordinator = enhance_agent_with_instructions(coordinator)
researcher = enhance_agent_with_instructions(researcher)
writer = enhance_agent_with_instructions(writer)
coder = enhance_agent_with_instructions(coder)

# В функции run_advanced_demo():
# Применяем динамические инструкции к команде
advanced_crew = enhance_crew_with_instructions(advanced_crew)
```

## 🎯 Преимущества системы

1. **Не перегружает системный промпт** - краткие описания в промпте, детали по требованию
2. **Динамическая подгрузка** - инструкции загружаются только при использовании инструмента
3. **Кэширование** - повторные запросы инструкций выполняются быстро
4. **Простая интеграция** - одна функция или декоратор для улучшения агентов/команд
5. **Обратная совместимость** - работает с существующими агентами и командами
6. **Автоматическая очистка** - инструкции удаляются после выполнения инструмента

## 🔮 Будущие улучшения

1. **Расширение инструкций** - добавление новых инструментов в `tool_instructions/`
2. **Персонализация** - адаптация инструкций под конкретные задачи
3. **Многоязычность** - поддержка инструкций на разных языках
4. **Аналитика** - отслеживание использования инструкций
5. **A/B тестирование** - сравнение эффективности разных версий инструкций

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все зависимости установлены
3. Запустите тесты: `python test_dynamic_instructions.py`
4. Проверьте совместимость версий CrewAI и GopiAI инструментов

## 🏁 Заключение

Система динамических инструкций успешно интегрирована и готова к использованию. Она обеспечивает эффективную работу LLM с инструментами GopiAI, предоставляя детальные инструкции только при необходимости, что улучшает производительность и качество работы агентов CrewAI.

---
*Документация создана: 19 июля 2025 г.*
*Версия системы: 1.0*
*Статус: Готово к продакшену*
