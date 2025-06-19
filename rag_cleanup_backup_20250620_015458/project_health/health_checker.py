#!/usr/bin/env python3
"""
GopiAI Project Health Checker 🏥
================================

Универсальный скрипт для проверки здоровья проекта и автоматической очистки.
Объединяет все утилиты очистки, анализа и оптимизации в одном месте.

Возможности:
- 🗑️  Удаление пустых файлов и папок
- 🧹 Поиск и удаление дублирующих файлов
- 💀 Поиск мёртвого кода
- 📊 Анализ зависимостей
- 🔍 Поиск неиспользуемых файлов
- 📝 Нормализация имён файлов
- 🔗 Проверка соединений компонентов
- 📈 Генерация отчётов

Автор: Crazy Coder
Дата: 2025-06-05
"""

import os
import sys
import json
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
import argparse
import subprocess
from collections import defaultdict
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectHealthChecker:
    """Главный класс для проверки здоровья проекта"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.reports_dir = self.project_root / "project_health" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Папки, которые нужно игнорировать
        self.ignore_dirs = {
            '__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv',
            'rag_memory_env', '.pytest_cache', 'dist', 'build', '.egg-info',
            '.mypy_cache', '.tox', 'logs'
        }
        
        # Расширения для анализа
        self.code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.css', '.html'}
        
        # Результаты проверок
        self.results = {
            'empty_files': [],
            'empty_dirs': [],
            'duplicate_files': [],
            'unused_files': [],
            'dead_code': [],
            'import_issues': [],
            'large_files': [],
            'suspicious_files': []
        }
    
    def run_full_check(self) -> Dict:
        """Запуск полной проверки проекта"""
        print("🏥 GopiAI Project Health Checker")
        print("=" * 50)
        print(f"📁 Проект: {self.project_root}")
        print(f"📊 Отчёты: {self.reports_dir}")
        print()
        
        checks = [
            ("🗑️  Поиск пустых файлов", self.find_empty_files),
            ("📂 Поиск пустых папок", self.find_empty_directories),
            ("🔍 Поиск дублирующих файлов", self.find_duplicate_files),
            ("💀 Анализ мёртвого кода", self.analyze_dead_code),
            ("🔗 Проверка импортов", self.check_imports),
            ("📏 Поиск больших файлов", self.find_large_files),
            ("⚠️  Поиск подозрительных файлов", self.find_suspicious_files),
            ("📝 Нормализация имён файлов", self.normalize_filenames),
        ]
        
        for name, check_func in checks:
            print(f"{name}...")
            try:
                check_func()
                print(f"   ✅ Завершено")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                logger.error(f"Ошибка в {name}: {e}")
        
        # Генерируем отчёт
        self.generate_report()
        
        # Предлагаем автоматическую очистку
        self.suggest_cleanup()
        
        return self.results
    
    def find_empty_files(self):
        """Поиск пустых файлов"""
        empty_files = []
        
        for file_path in self.project_root.rglob('*'):
            if (file_path.is_file() and 
                not any(ignore in file_path.parts for ignore in self.ignore_dirs)):
                
                try:
                    if file_path.stat().st_size == 0:
                        empty_files.append(str(file_path.relative_to(self.project_root)))
                    elif file_path.suffix == '.py':
                        # Проверяем Python файлы на содержимое
                        content = file_path.read_text(encoding='utf-8', errors='ignore').strip()
                        if not content or content in ['', '#!/usr/bin/env python3', '# -*- coding: utf-8 -*-']:
                            empty_files.append(str(file_path.relative_to(self.project_root)))
                except (OSError, UnicodeDecodeError):
                    continue
        
        self.results['empty_files'] = empty_files
        print(f"   📄 Найдено пустых файлов: {len(empty_files)}")
    
    def find_empty_directories(self):
        """Поиск пустых папок"""
        empty_dirs = []
        
        for dir_path in self.project_root.rglob('*'):
            if (dir_path.is_dir() and 
                not any(ignore in dir_path.parts for ignore in self.ignore_dirs)):
                
                try:
                    # Проверяем, есть ли файлы в папке (рекурсивно)
                    has_files = any(p.is_file() for p in dir_path.rglob('*'))
                    if not has_files:
                        empty_dirs.append(str(dir_path.relative_to(self.project_root)))
                except OSError:
                    continue
        
        self.results['empty_dirs'] = empty_dirs
        print(f"   📂 Найдено пустых папок: {len(empty_dirs)}")
    
    def find_duplicate_files(self):
        """Поиск дублирующих файлов по содержимому"""
        file_hashes = defaultdict(list)
        duplicates = []
        
        for file_path in self.project_root.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in self.code_extensions and
                not any(ignore in file_path.parts for ignore in self.ignore_dirs)):
                
                try:
                    content = file_path.read_bytes()
                    if len(content) > 0:  # Пропускаем пустые файлы
                        file_hash = hashlib.md5(content).hexdigest()
                        file_hashes[file_hash].append(str(file_path.relative_to(self.project_root)))
                except (OSError, UnicodeDecodeError):
                    continue
        
        # Находим дубликаты
        for hash_value, files in file_hashes.items():
            if len(files) > 1:
                duplicates.append(files)
        
        self.results['duplicate_files'] = duplicates
        print(f"   🔍 Найдено групп дубликатов: {len(duplicates)}")
    
    def analyze_dead_code(self):
        """Анализ мёртвого кода"""
        dead_code_files = []
        
        # Простой анализ: файлы, которые не импортируются
        all_python_files = set()
        imported_modules = set()
        
        for file_path in self.project_root.rglob('*.py'):
            if not any(ignore in file_path.parts for ignore in self.ignore_dirs):
                all_python_files.add(str(file_path.relative_to(self.project_root)))
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    # Ищем импорты
                    import_patterns = [
                        r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                        r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                    ]
                    
                    for pattern in import_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if '.' in match:
                                # Модульный импорт
                                parts = match.split('.')
                                for i in range(len(parts)):
                                    module_path = '/'.join(parts[:i+1]) + '.py'
                                    imported_modules.add(module_path)
                            else:
                                imported_modules.add(f"{match}.py")
                
                except (OSError, UnicodeDecodeError):
                    continue
        
        # Файлы, которые не импортируются (возможно мёртвый код)
        potentially_dead = all_python_files - imported_modules
        
        # Исключаем основные файлы
        main_files = {'main.py', '__main__.py', 'setup.py', 'run.py'}
        for file_path in potentially_dead:
            if (Path(file_path).name not in main_files and 
                not file_path.endswith('__init__.py') and
                'test' not in file_path.lower()):
                dead_code_files.append(file_path)
        
        self.results['dead_code'] = dead_code_files
        print(f"   💀 Потенциально мёртвый код: {len(dead_code_files)} файлов")
    
    def check_imports(self):
        """Проверка проблем с импортами"""
        import_issues = []
        
        for file_path in self.project_root.rglob('*.py'):
            if not any(ignore in file_path.parts for ignore in self.ignore_dirs):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        
                        # Проверяем на проблемные импорты
                        if line.startswith('import ') or line.startswith('from '):
                            # Проверяем на звёздочки
                            if 'import *' in line:
                                import_issues.append({
                                    'file': str(file_path.relative_to(self.project_root)),
                                    'line': line_num,
                                    'issue': 'star_import',
                                    'content': line
                                })
                            
                            # Проверяем на длинные строки импорта
                            if len(line) > 100:
                                import_issues.append({
                                    'file': str(file_path.relative_to(self.project_root)),
                                    'line': line_num,
                                    'issue': 'long_import',
                                    'content': line[:100] + '...'
                                })
                
                except (OSError, UnicodeDecodeError):
                    continue
        
        self.results['import_issues'] = import_issues
        print(f"   🔗 Найдено проблем с импортами: {len(import_issues)}")
    
    def find_large_files(self):
        """Поиск больших файлов"""
        large_files = []
        max_size = 1024 * 1024  # 1MB
        
        for file_path in self.project_root.rglob('*'):
            if (file_path.is_file() and 
                not any(ignore in file_path.parts for ignore in self.ignore_dirs)):
                
                try:
                    size = file_path.stat().st_size
                    if size > max_size:
                        large_files.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'size': size,
                            'size_mb': round(size / (1024 * 1024), 2)
                        })
                except OSError:
                    continue
        
        # Сортируем по размеру
        large_files.sort(key=lambda x: x['size'], reverse=True)
        
        self.results['large_files'] = large_files
        print(f"   📏 Найдено больших файлов (>1MB): {len(large_files)}")
    
    def find_suspicious_files(self):
        """Поиск подозрительных файлов"""
        suspicious = []
        
        # Паттерны подозрительных файлов
        suspicious_patterns = [
            r'.*\.bak$', r'.*\.tmp$', r'.*\.temp$', r'.*~$',
            r'.*\.orig$', r'.*\.old$', r'.*_backup.*',
            r'.*_copy.*', r'.*_test_.*', r'.*\.pyc$',
            r'.*\.log$', r'.*\.cache$'
        ]
        
        for file_path in self.project_root.rglob('*'):
            if (file_path.is_file() and 
                not any(ignore in file_path.parts for ignore in self.ignore_dirs)):
                
                file_str = str(file_path.relative_to(self.project_root))
                
                for pattern in suspicious_patterns:
                    if re.match(pattern, file_str, re.IGNORECASE):
                        suspicious.append({
                            'file': file_str,
                            'reason': f'Matches pattern: {pattern}'
                        })
                        break
        
        self.results['suspicious_files'] = suspicious
        print(f"   ⚠️  Найдено подозрительных файлов: {len(suspicious)}")
    
    def normalize_filenames(self):
        """Нормализация имён файлов"""
        problematic_files = []
        
        for file_path in self.project_root.rglob('*'):
            if not any(ignore in file_path.parts for ignore in self.ignore_dirs):
                name = file_path.name
                
                # Проверяем на проблемные символы
                if re.search(r'[^\w\-_.]', name):
                    problematic_files.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'issue': 'special_characters'
                    })
                
                # Проверяем на пробелы
                if ' ' in name:
                    problematic_files.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'issue': 'spaces_in_name'
                    })
        
        self.results['problematic_filenames'] = problematic_files
        print(f"   📝 Найдено файлов с проблемными именами: {len(problematic_files)}")
    
    def generate_report(self):
        """Генерация подробного отчёта"""
        timestamp = datetime.now().isoformat()
        
        report = {
            'timestamp': timestamp,
            'project_root': str(self.project_root),
            'summary': {
                'empty_files': len(self.results['empty_files']),
                'empty_dirs': len(self.results['empty_dirs']),
                'duplicate_groups': len(self.results['duplicate_files']),
                'dead_code_files': len(self.results['dead_code']),
                'import_issues': len(self.results['import_issues']),
                'large_files': len(self.results['large_files']),
                'suspicious_files': len(self.results['suspicious_files'])
            },
            'details': self.results
        }
        
        # Сохраняем JSON отчёт
        report_file = self.reports_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Создаём читаемый отчёт
        readable_report = self.reports_dir / f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.create_readable_report(readable_report, report)
        
        print(f"\n📊 Отчёт сохранён:")
        print(f"   📄 JSON: {report_file}")
        print(f"   📝 Markdown: {readable_report}")
    
    def create_readable_report(self, file_path: Path, report: Dict):
        """Создание читаемого отчёта в Markdown"""
        content = f"""# GopiAI Project Health Report

**Дата:** {report['timestamp']}  
**Проект:** {report['project_root']}

## 📊 Сводка

| Категория | Количество |
|-----------|------------|
| 🗑️ Пустые файлы | {report['summary']['empty_files']} |
| 📂 Пустые папки | {report['summary']['empty_dirs']} |
| 🔍 Группы дубликатов | {report['summary']['duplicate_groups']} |
| 💀 Потенциально мёртвый код | {report['summary']['dead_code_files']} |
| 🔗 Проблемы с импортами | {report['summary']['import_issues']} |
| 📏 Большие файлы (>1MB) | {report['summary']['large_files']} |
| ⚠️ Подозрительные файлы | {report['summary']['suspicious_files']} |

## 🗑️ Пустые файлы

"""
        
        if report['details']['empty_files']:
            for file in report['details']['empty_files']:
                content += f"- `{file}`\n"
        else:
            content += "Пустые файлы не найдены ✅\n"
        
        content += "\n## 📂 Пустые папки\n\n"
        if report['details']['empty_dirs']:
            for dir in report['details']['empty_dirs']:
                content += f"- `{dir}/`\n"
        else:
            content += "Пустые папки не найдены ✅\n"
        
        content += "\n## 🔍 Дублирующие файлы\n\n"
        if report['details']['duplicate_files']:
            for i, group in enumerate(report['details']['duplicate_files'], 1):
                content += f"### Группа {i}\n"
                for file in group:
                    content += f"- `{file}`\n"
                content += "\n"
        else:
            content += "Дубликаты не найдены ✅\n"
        
        content += "\n## 💀 Потенциально мёртвый код\n\n"
        if report['details']['dead_code']:
            for file in report['details']['dead_code']:
                content += f"- `{file}`\n"
        else:
            content += "Мёртвый код не найден ✅\n"
        
        content += "\n## 📏 Большие файлы\n\n"
        if report['details']['large_files']:
            for file_info in report['details']['large_files']:
                content += f"- `{file_info['file']}` - {file_info['size_mb']} MB\n"
        else:
            content += "Больших файлов не найдено ✅\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def suggest_cleanup(self):
        """Предложение автоматической очистки"""
        total_issues = (
            len(self.results['empty_files']) +
            len(self.results['empty_dirs']) +
            len(self.results['suspicious_files'])
        )
        
        if total_issues > 0:
            print(f"\n🧹 Найдено {total_issues} проблем, которые можно исправить автоматически")
            print("Хотите запустить автоматическую очистку? (y/N): ", end="")
            
            try:
                response = input().strip().lower()
                if response in ['y', 'yes', 'да']:
                    self.auto_cleanup()
            except (EOFError, KeyboardInterrupt):
                print("\nОтмена.")
    
    def auto_cleanup(self):
        """Автоматическая очистка"""
        print("\n🧹 Запуск автоматической очистки...")
        
        cleaned_files = 0
        cleaned_dirs = 0
        
        # Удаление пустых файлов
        for file_path in self.results['empty_files']:
            full_path = self.project_root / file_path
            try:
                full_path.unlink()
                cleaned_files += 1
                print(f"   🗑️ Удалён пустой файл: {file_path}")
            except OSError as e:
                logger.error(f"Ошибка удаления {file_path}: {e}")
        
        # Удаление пустых папок
        for dir_path in sorted(self.results['empty_dirs'], reverse=True):  # Сначала вложенные
            full_path = self.project_root / dir_path
            try:
                full_path.rmdir()
                cleaned_dirs += 1
                print(f"   📂 Удалена пустая папка: {dir_path}")
            except OSError as e:
                logger.error(f"Ошибка удаления папки {dir_path}: {e}")
        
        # Удаление подозрительных файлов
        for file_info in self.results['suspicious_files']:
            file_path = file_info['file']
            full_path = self.project_root / file_path
            try:
                full_path.unlink()
                cleaned_files += 1
                print(f"   ⚠️ Удалён подозрительный файл: {file_path}")
            except OSError as e:
                logger.error(f"Ошибка удаления {file_path}: {e}")
        
        print(f"\n✅ Очистка завершена!")
        print(f"   🗑️ Удалено файлов: {cleaned_files}")
        print(f"   📂 Удалено папок: {cleaned_dirs}")
        
        # Обновляем карту проекта
        print("\n🔄 Обновление карты проекта...")
        try:
            subprocess.run([
                sys.executable, 
                str(self.project_root / "update_project_map.py")
            ], cwd=self.project_root)
        except Exception as e:
            logger.error(f"Ошибка обновления карты проекта: {e}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="GopiAI Project Health Checker")
    parser.add_argument('--project-root', type=Path, help='Путь к корню проекта')
    parser.add_argument('--auto-clean', action='store_true', help='Автоматическая очистка без запроса')
    parser.add_argument('--report-only', action='store_true', help='Только генерация отчёта')
    
    args = parser.parse_args()
    
    # Создаём экземпляр checker'а
    checker = ProjectHealthChecker(args.project_root)
    
    try:
        # Запускаем проверку
        results = checker.run_full_check()
        
        # Автоматическая очистка если запрошена
        if args.auto_clean and not args.report_only:
            checker.auto_cleanup()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Прервано пользователем")
        return 1
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
