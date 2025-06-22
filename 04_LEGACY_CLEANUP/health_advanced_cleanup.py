#!/usr/bin/env python3
"""
GopiAI Advanced Project Cleanup 🧹
===================================

Расширенная очистка проекта от дубликатов и ненужных файлов.
Умно определяет, какие файлы нужно оставить, а какие удалить.

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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedProjectCleaner:
    """Продвинутый очиститель проекта"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.reports_dir = self.project_root / "project_health" / "reports"
        
        # Папки, которые нужно игнорировать
        self.ignore_dirs = {
            '__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv',
            'rag_memory_env', '.pytest_cache', 'dist', 'build', '.egg-info',
            '.mypy_cache', '.tox', 'logs'
        }
        
        # Правила приоритета для дубликатов
        self.priority_rules = [
            # Основные модули имеют приоритет над дублями в GopiAI/
            (r'^GopiAI-', r'^GopiAI\\GopiAI-'),  # GopiAI-Core vs GopiAI/GopiAI-Core
            (r'^UI\\', r'^GopiAI-UI\\ui\\'),     # UI/ vs GopiAI-UI/ui/
            (r'^(?!rag_memory_system)', r'^rag_memory_system\\project_sync\\'),  # Оригинал vs синхронизированная копия
        ]
        
        # Файлы для безусловного удаления
        self.unsafe_patterns = [
            '*.tmp', '*.temp', '*.bak', '*.old', '*.backup',
            '*~', '*.pyc', '*.pyo', '*.pyd',
            'Thumbs.db', '.DS_Store', 'desktop.ini'
        ]
        
        self.removed_files = []
        self.removed_dirs = []
    
    def load_health_report(self) -> Dict:
        """Загрузка последнего отчёта health checker'а"""
        reports = list(self.reports_dir.glob("health_check_*.json"))
        if not reports:
            raise FileNotFoundError("Не найден отчёт health checker'а. Запустите сначала health_checker.py")
        
        latest_report = max(reports, key=lambda x: x.stat().st_mtime)
        with open(latest_report, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_duplicates(self, duplicate_groups: List[List[str]]) -> List[Tuple[str, List[str]]]:
        """Анализ дубликатов и определение, какие файлы удалить"""
        files_to_remove = []
        
        for group in duplicate_groups:
            if len(group) < 2:
                continue
            
            # Применяем правила приоритета
            keep_file = None
            remove_files = []
            
            for priority_pattern, remove_pattern in self.priority_rules:
                keep_candidates = [f for f in group if self._matches_pattern(f, priority_pattern)]
                remove_candidates = [f for f in group if self._matches_pattern(f, remove_pattern)]
                
                if keep_candidates and remove_candidates:
                    keep_file = keep_candidates[0]  # Берём первый подходящий
                    remove_files.extend(remove_candidates)
                    break
            
            # Если правила не сработали, оставляем самый короткий путь
            if not keep_file:
                group.sort(key=len)
                keep_file = group[0]
                remove_files = group[1:]
            
            # Убираем уже выбранный файл из списка на удаление
            remove_files = [f for f in remove_files if f != keep_file]
            
            if remove_files:
                files_to_remove.append((keep_file, remove_files))
        
        return files_to_remove
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Проверка соответствия пути паттерну (простая regex-подобная проверка)"""
        import re
        try:
            return bool(re.search(pattern, path.replace('/', '\\')))
        except:
            return False
    
    def remove_duplicate_files(self, duplicate_analysis: List[Tuple[str, List[str]]]) -> int:
        """Удаление дублирующих файлов"""
        removed_count = 0
        
        print("🔍 Анализ дубликатов...")
        
        for keep_file, remove_files in duplicate_analysis:
            print(f"\n📁 Группа дубликатов:")
            print(f"   ✅ Оставляем: {keep_file}")
            
            for file_path in remove_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    try:
                        full_path.unlink()
                        self.removed_files.append(file_path)
                        removed_count += 1
                        print(f"   🗑️ Удалён: {file_path}")
                    except OSError as e:
                        logger.error(f"Ошибка удаления {file_path}: {e}")
                else:
                    print(f"   ⚠️ Уже удалён: {file_path}")
        
        return removed_count
    
    def remove_empty_directories(self) -> int:
        """Удаление пустых папок (рекурсивно)"""
        removed_count = 0
        
        # Повторяем несколько раз, чтобы удалить вложенные пустые папки
        for _ in range(3):
            empty_dirs = []
            
            for dir_path in self.project_root.rglob('*'):
                if (dir_path.is_dir() and 
                    not any(ignore in dir_path.parts for ignore in self.ignore_dirs)):
                    
                    try:
                        # Проверяем, есть ли файлы в папке
                        has_files = any(p.is_file() for p in dir_path.rglob('*'))
                        if not has_files:
                            empty_dirs.append(dir_path)
                    except OSError:
                        continue
            
            # Удаляем пустые папки (сначала самые глубокие)
            empty_dirs.sort(key=lambda x: len(x.parts), reverse=True)
            
            for dir_path in empty_dirs:
                try:
                    dir_path.rmdir()
                    rel_path = str(dir_path.relative_to(self.project_root))
                    self.removed_dirs.append(rel_path)
                    removed_count += 1
                    print(f"   📂 Удалена пустая папка: {rel_path}")
                except OSError:
                    # Папка не пустая или уже удалена
                    pass
        
        return removed_count
    
    def clean_unsafe_files(self) -> int:
        """Удаление файлов по небезопасным паттернам"""
        removed_count = 0
        
        print("\n🚨 Удаление небезопасных файлов...")
        
        for pattern in self.unsafe_patterns:
            for file_path in self.project_root.rglob(pattern):
                if (file_path.is_file() and 
                    not any(ignore in file_path.parts for ignore in self.ignore_dirs)):
                    
                    try:
                        file_path.unlink()
                        rel_path = str(file_path.relative_to(self.project_root))
                        self.removed_files.append(rel_path)
                        removed_count += 1
                        print(f"   🗑️ Удалён: {rel_path}")
                    except OSError as e:
                        logger.error(f"Ошибка удаления {file_path}: {e}")
        
        return removed_count
    
    def run_advanced_cleanup(self, auto_confirm: bool = False) -> Dict:
        """Запуск расширенной очистки"""
        print("🧹 GopiAI Advanced Project Cleanup")
        print("=" * 50)
        print(f"📁 Проект: {self.project_root}")
        print()
        
        # Загружаем отчёт health checker'а
        try:
            report = self.load_health_report()
            print(f"📊 Загружен отчёт health checker'а")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return {}
        
        # Анализируем дубликаты
        duplicate_groups = report['details']['duplicate_files']
        duplicate_analysis = self.analyze_duplicates(duplicate_groups)
        
        total_files_to_remove = sum(len(remove_files) for _, remove_files in duplicate_analysis)
        
        print(f"\n📊 Найдено для очистки:")
        print(f"   🔍 Групп дубликатов: {len(duplicate_analysis)}")
        print(f"   🗑️ Файлов к удалению: {total_files_to_remove}")
        
        # Запрашиваем подтверждение
        if not auto_confirm:
            print(f"\nПродолжить очистку? (y/N): ", end="")
            try:
                response = input().strip().lower()
                if response not in ['y', 'yes', 'да']:
                    print("Отмена.")
                    return {}
            except (EOFError, KeyboardInterrupt):
                print("\nОтмена.")
                return {}
        
        # Выполняем очистку
        print("\n🧹 Запуск расширенной очистки...")
        
        removed_duplicates = self.remove_duplicate_files(duplicate_analysis)
        removed_unsafe = self.clean_unsafe_files()
        removed_empty_dirs = self.remove_empty_directories()
        
        # Сводка
        total_removed_files = removed_duplicates + removed_unsafe + len(self.removed_files)
        total_removed_dirs = removed_empty_dirs + len(self.removed_dirs)
        
        print(f"\n✅ Расширенная очистка завершена!")
        print(f"   🗑️ Удалено файлов: {total_removed_files}")
        print(f"   📂 Удалено папок: {total_removed_dirs}")
        
        # Сохраняем отчёт
        cleanup_report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'removed_files': self.removed_files,
            'removed_dirs': self.removed_dirs,
            'summary': {
                'removed_duplicates': removed_duplicates,
                'removed_unsafe': removed_unsafe,
                'removed_empty_dirs': removed_empty_dirs,
                'total_files': total_removed_files,
                'total_dirs': total_removed_dirs
            }
        }
        
        report_file = self.reports_dir / f"advanced_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(cleanup_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Отчёт сохранён: {report_file}")
        
        # Обновляем карту проекта
        print("\n🔄 Обновление карты проекта...")
        try:
            import subprocess
            subprocess.run([
                sys.executable, 
                str(self.project_root / "update_project_map.py")
            ], cwd=self.project_root)
        except Exception as e:
            logger.error(f"Ошибка обновления карты проекта: {e}")
        
        return cleanup_report


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="GopiAI Advanced Project Cleanup")
    parser.add_argument('--project-root', type=Path, help='Путь к корню проекта')
    parser.add_argument('--auto-confirm', action='store_true', help='Автоматическое подтверждение без запроса')
    
    args = parser.parse_args()
    
    # Создаём экземпляр cleaner'а
    cleaner = AdvancedProjectCleaner(args.project_root)
    
    try:
        # Запускаем расширенную очистку
        results = cleaner.run_advanced_cleanup(args.auto_confirm)
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Прервано пользователем")
        return 1
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
