---
applyTo: "**/*.py **/*.md **/*.txt **/*.json **/*.sh **/*.bat **/*.yml **/*.yaml **/*.toml **/*.ini **/*.cfg **/*.xml **/*.html **/*.css **/*.js **/*.ts **/*.vue **/*.jsx **/*.tsx **/*.scss **/*.sass **/*.less **/*.c **/*.cpp **/*.h **/*.hpp **/*.go **/*.rs **/*.java **/*.kt **/*.swift **/*.php **/*.rb **/*.pl **/*.pyi **/*.ps1 **/*.psm1 **/*.psd1 **/*.bash **/*.zsh **/*.fish **/Dockerfile **/.dockerignore **/.gitignore **/.gitattributes **/.editorconfig **/.prettierrc **/.eslintrc **/.babelrc **/.stylelintrc **/.pylintrc **/.flake8 **/.bandit **/.mypy.ini **/pyproject.toml **/tox.ini **/docker-compose*.yml"

name: "GopiAI Project Cleanup and Refactoring Instructions"
description: "Instructions for GopiAI project cleanup and refactoring, including module structure, RAG synchronization, and project health checks."
steps:
  - type: "markdown"
    content: |
      # GopiAI Project Cleanup and Refactoring Instructions
      
      ## Overview
      This document provides detailed instructions for cleaning up and refactoring the GopiAI project, including module structure, RAG synchronization, and project health checks.
      
      ## Module Structure
      The GopiAI project has been modularized into several components:
      - **GopiAI-Core**: Core functionality of GopiAI.
      - **GopiAI-Extensions**: Additional features and extensions.
      - **GopiAI-Widgets**: UI components and widgets.
      - **GopiAI-App**: Main application logic.
      - **GopiAI-Assets**: Static assets and resources.
      
      ## RAG Synchronization
      The project includes scripts to synchronize with the RAG system:
      - `sync_to_rag.py`: Synchronizes project data with the RAG index.
      
      ## Project Health Checks
      Use the following commands to perform health checks and cleanups:
      ```bash
      python project_health/health_checker.py --auto-clean
      python project_health/health_checker.py --report-only
      ```
        These commands will:
        - `--auto-clean`: Automatically fix issues found during the health check.
        - `--report-only`: Generate a report of issues without making changes.
        ## Final Cleanup
        After completing the health checks and addressing any issues, perform a final cleanup:
        ```bash
        python project_health/health_checker.py --final-clean
        ```
        This command will:
        - Remove any temporary files or artifacts created during the cleanup process.
        - Ensure the project is in a clean and stable state.
        ## Conclusion

        Following these instructions will help maintain the GopiAI project in a clean, modular, and efficient state. Regular health checks and cleanups are recommended to ensure the project remains maintainable and scalable.
  - type: "markdown"
    content: |
      ## Additional Notes
# Системный промпт для GitHub Copilot

## Обязательные инструменты и подходы

### MCP серверы
- **ВСЕГДА** используй доступные MCP серверы для максимальной эффективности
- **Desktop Commander**: используй для всех операций с файловой системой и точечного редактирования
- **Sequential Thinking**: обязательно применяй для планирования и структурирования сложных задач
- **Exa Search MCP**: используй для поиска актуальной информации в интернете
- **RAG память**: всегда проверяй и используй файлы памяти в корне рабочей папки
- **RAG индекс**: всегда проверяй и используй индекс RAG для быстрого доступа к информации
- **Project Health Checker**: используй для анализа и поддержания здоровья проекта
- **Project Map Updater**: используй для обновления карты проекта и синхронизации с RAG
- **Advanced Cleanup Tools**: используй для очистки дубликатов и мёртвого кода
- **Health Checker**: используй для регулярного аудита и очистки проекта
Отвечай на русском языке в чате и в комментариях к коду.
- **Project Detective**: используй для анализа структуры проекта и поиска проблем
- **Dependency Mapper**: используй для анализа зависимостей и структуры проекта
- **Project Sync**: используй для синхронизации проекта с RAG памятью



### Управление контекстом и памятью
- **RAG память**: всегда проверяй и используй файлы памяти в корне рабочей папки
- Сохраняй важную информацию о проекте в RAG память для дальнейшего использования
- Учитывай историю предыдущих решений перед предложением новых подходов
- Используй RAG индекс для быстрого доступа к информации и контексту задач
- Всегда проверяй контекст задачи из RAG памяти перед началом работы
- Используй RAG память для хранения промежуточных результатов и заметок
- Всегда проверяй RAG индекс перед началом работы над задачей
- Используй RAG память для хранения ключевых данных и результатов анализа

## Принципы работы с файлами

### Избегание дубликатов
- **ПРИОРИТЕТ**: редактирование существующих файлов вместо создания новых
- Используй Desktop Commander для точечных изменений в файлах
- Перед созданием нового файла проверь, нет ли подходящего существующего
- При необходимости создания нового файла объясни, почему редактирование существующего невозможно

### Workflow для работы с файлами
1. Сначала анализируй существующую структуру проекта
2. Ищи подходящие места для внесения изменений
3. Используй Desktop Commander для точечного редактирования
4. Только после этого рассматривай создание новых файлов

## Подход к решению проблем

### Эскалация при трудностях
- **Правило двух попыток**: если решение не найдено после 2 попыток, переходи к поиску
- **Источники информации** (по приоритету):
  1. Официальная документация (через Exa Search)
  2. GitHub Issues и примеры кода
  3. Технические форумы (Stack Overflow, Reddit)
  4. Статьи разработчиков и туториалы

### Структурированное планирование
- **Sequential Thinking обязательно** для задач, включающих:
  - Планирование архитектуры
  - Пошаговую настройку
  - Отладку сложных проблем
  - Рефакторинг кода
- Разбивай сложные задачи на логические этапы
- Документируй промежуточные результаты

## Качество и эффективность

### Перед каждым действием
- Проверь доступные MCP серверы и выбери наиболее подходящие
- Убедись, что понимаешь контекст задачи из RAG памяти
- Оцени, нужно ли использовать Sequential Thinking для планирования

### Коммуникация с пользователем
- Объясняй, какие MCP серверы используешь и почему
- Показывай план действий при использовании Sequential Thinking
- Предупреждай о потенциальных проблемах и предлагай альтернативы

## Приоритеты действий
1. Анализ контекста (RAG память + структура проекта)
2. Планирование через Sequential Thinking (если нужно)
3. Использование подходящих MCP серверов
4. Выполнение с минимальным дублированием файлов
5. Документирование результатов в RAG память