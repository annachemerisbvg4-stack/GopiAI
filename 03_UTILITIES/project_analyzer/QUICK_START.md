# Быстрый старт - Project Analyzer

Этот документ поможет вам быстро начать использовать новую структурированную систему анализа проекта.

## 🚀 Быстрый запуск

### 1. Простейший способ - Batch файлы (Windows)

```cmd
# Переходим в папку с исполняемыми файлами
cd 03_UTILITIES\project_analyzer\runners

# Быстрый анализ (рекомендуется для начала)
quick_analyze.bat

# Полный анализ проекта
analyze_gopi_project.bat

# Строгий анализ (только файлы проекта)
strict_analyze.bat
```

### 2. Python скрипты

```bash
cd 03_UTILITIES/project_analyzer/runners

# Быстрый анализ (без ограничений по файлам)
python quick_analyze.py --skip-duplicate

# Полный анализ
python analyze_project.py

# Демонстрация возможностей
python demo_usage.py
```

## 📊 Типы анализа

### Быстрый анализ (quick_analyze)
- ⚡ Самый быстрый (1-3 минуты)
- 🎯 Без ограничений по количеству файлов
- 🚫 Можно пропустить тяжелые анализаторы
- ✅ Подходит для регулярных проверок

```cmd
quick_analyze.bat --skip-duplicate --skip-conflict
```

### Строгий анализ (strict_analyzer)
- 🎯 Только файлы проекта (исключает системные папки)
- ⚡ Средняя скорость (3-5 минут)
- 🛡️ Безопасный (не анализирует системные файлы)
- ✅ Подходит для CI/CD

```cmd
strict_analyze.bat --timeout 300
```

### Полный анализ (analyze_project)
- 🔍 Максимальная детализация
- ⏱️ Медленный (10-30 минут)
- 📈 Все анализаторы включены
- ✅ Подходит для глубокого анализа

```cmd
analyze_gopi_project.bat
```

## 🛠️ Параметры командной строки

### Общие параметры
```cmd
--max-files N          # Ограничить количество файлов (по умолчанию: без ограничений)
--timeout N            # Таймаут в секундах (по умолчанию: 300)
--format FORMAT        # Формат отчета: markdown, html, json
--skip-duplicate       # Пропустить анализ дубликатов (ускоряет работу)
--skip-conflict        # Пропустить анализ конфликтов
```

### Примеры использования
```cmd
# Быстрый анализ в HTML формате
quick_analyze.bat --format html

# Анализ без дубликатов с таймаутом 5 минут
strict_analyze.bat --skip-duplicate --timeout 300

# Полный анализ в JSON формате
analyze_gopi_project.bat --format json
```

## 📁 Где найти результаты

Все отчеты сохраняются в:
```
GOPI_AI_MODULES/
└── project_health/
    └── reports/
        ├── quick_analysis_YYYYMMDD_HHMMSS.md
        ├── strict_analysis_YYYYMMDD_HHMMSS.md
        └── project_analysis_YYYYMMDD_HHMMSS.md
```

## 🧪 Тестирование

Проверить работоспособность системы:

```cmd
cd 03_UTILITIES\project_analyzer\tests
run_tests.bat
```

## 🔧 Программное использование

```python
# Импорт основных компонентов
from project_analyzer.core import (
    AnalysisConfig, 
    ProjectCleanupAnalyzer,
    StructureAnalyzer
)

# Создание конфигурации
config = AnalysisConfig(
    project_path="path/to/project",
    analysis_depth="quick",
    max_files_per_analyzer=0  # Без ограничений
)

# Запуск анализа
analyzer = ProjectCleanupAnalyzer(config)
results = analyzer.run_full_analysis()
```

## ❓ Решение проблем

### Проблема: "Модуль не найден"
```cmd
# Убедитесь, что находитесь в правильной директории
cd 03_UTILITIES\project_analyzer\runners
```

### Проблема: "Анализ слишком медленный"
```cmd
# Используйте ограничения
quick_analyze.bat --skip-duplicate --timeout 120
```

### Проблема: "Ошибки импорта в анализаторах"
```cmd
# Проверьте структуру проекта
python demo_usage.py
```

## 📚 Дополнительная документация

- `README.md` - Полная документация
- `MIGRATION.md` - Руководство по миграции
- `CLEANUP_LIST.md` - Список файлов для очистки
- `runners/demo_usage.py` - Примеры программного использования

## 🎯 Рекомендуемый workflow

1. **Начните с быстрого анализа:**
   ```cmd
   quick_analyze.bat
   ```

2. **Если нужна детализация:**
   ```cmd
   strict_analyze.bat --skip-duplicate
   ```

3. **Для полного аудита:**
   ```cmd
   analyze_gopi_project.bat
   ```

4. **Регулярные проверки:**
   ```cmd
   quick_analyze.bat --timeout 180
   ```
