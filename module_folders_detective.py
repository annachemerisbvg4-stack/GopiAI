#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 MODULE FOLDERS DETECTIVE 
📊 Анализ содержимого папок модулей GopiAI для выявления устаревших файлов
🎯 ЦЕЛЬ: Найти файлы, которые больше не нужны после создания модульного интерфейса
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ModuleFoldersDetective:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.analysis_report = {
            'analysis_date': datetime.now().isoformat(),
            'base_path': str(self.base_path),
            'modules_analyzed': {},
            'deprecated_files': [],
            'stub_files': [],
            'conflicting_files': [],
            'unused_widgets': [],
            'recommendations': []
        }
        
        # Паттерны для поиска устаревших файлов
        self.stub_patterns = [
            r'stub',
            r'TODO_STUB',
            r'заглушка',
            r'ЗАГЛУШКА',
            r'STUB:',
            r'STUB_CREATED'
        ]
        
        self.deprecated_patterns = [
            r'deprecated',
            r'устарел',
            r'old_',
            r'legacy',
            r'temp_',
            r'временный'
        ]
        
        # Модули для анализа
        self.module_folders = [
            'GopiAI-Core',
            'GopiAI-Widgets', 
            'GopiAI-Extensions',
            'GopiAI-App',
            'GopiAI-Assets'
        ]
        
    def analyze_all_modules(self):
        """Анализирует все модульные папки"""
        print("🔍 Начинаем анализ модульных папок...")
        
        for module_name in self.module_folders:
            module_path = self.base_path / module_name
            if module_path.exists():
                print(f"\n📁 Анализируем {module_name}...")
                self.analyze_module(module_name, module_path)
            else:
                print(f"⚠️ Папка {module_name} не найдена")
                
        self.generate_recommendations()
        return self.analysis_report
    
    def analyze_module(self, module_name, module_path):
        """Анализирует конкретный модуль"""
        module_info = {
            'path': str(module_path),
            'files_analyzed': 0,
            'python_files': [],
            'stub_files': [],
            'deprecated_files': [],
            'widget_files': [],
            'potential_conflicts': []
        }
        
        # Анализируем все Python файлы в модуле
        for py_file in module_path.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
                
            module_info['files_analyzed'] += 1
            file_info = self.analyze_file(py_file)
            
            if file_info['is_stub']:
                module_info['stub_files'].append(file_info)
                self.analysis_report['stub_files'].append(file_info)
                
            if file_info['is_deprecated']:
                module_info['deprecated_files'].append(file_info)
                self.analysis_report['deprecated_files'].append(file_info)
                
            if file_info['is_widget']:
                module_info['widget_files'].append(file_info)
                
            # Проверяем на конфликты с новыми модулями
            if self._check_conflict_with_new_modules(py_file):
                conflict_info = {
                    'file': str(py_file),
                    'module': module_name,
                    'reason': 'Возможный конфликт с новым модульным интерфейсом'
                }
                module_info['potential_conflicts'].append(conflict_info)
                self.analysis_report['conflicting_files'].append(conflict_info)
                
            module_info['python_files'].append(file_info)
            
        self.analysis_report['modules_analyzed'][module_name] = module_info
        
    def analyze_file(self, file_path):
        """Анализирует отдельный файл"""
        file_info = {
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'is_stub': False,
            'is_deprecated': False,
            'is_widget': False,
            'is_empty': False,
            'content_analysis': {},
            'imports': [],
            'classes': [],
            'functions': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем, пустой ли файл
            if len(content.strip()) == 0:
                file_info['is_empty'] = True
                
            # Анализируем содержимое
            file_info['content_analysis'] = self._analyze_content(content)
            
            # Проверяем на stub-файлы
            for pattern in self.stub_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    file_info['is_stub'] = True
                    break
                    
            # Проверяем на deprecated файлы
            for pattern in self.deprecated_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    file_info['is_deprecated'] = True
                    break
                    
            # Проверяем, является ли файл виджетом
            if 'widget' in file_path.name.lower() or 'Widget' in content:
                file_info['is_widget'] = True
                
            # Извлекаем импорты, классы и функции
            file_info['imports'] = self._extract_imports(content)
            file_info['classes'] = self._extract_classes(content)
            file_info['functions'] = self._extract_functions(content)
            
        except Exception as e:
            file_info['error'] = str(e)
            
        return file_info
    
    def _analyze_content(self, content):
        """Анализирует содержимое файла"""
        lines = content.split('\n')
        return {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'empty_lines': len([l for l in lines if not l.strip()]),
            'has_main': '__main__' in content,
            'has_qt_imports': 'PySide6' in content or 'PyQt' in content,
            'has_tkinter_imports': 'tkinter' in content,
            'has_test_code': 'test_' in content or 'unittest' in content or 'pytest' in content
        }
    
    def _extract_imports(self, content):
        """Извлекает импорты из файла"""
        imports = []
        import_pattern = r'^(?:from\s+(.+?)\s+import\s+(.+)|import\s+(.+))$'
        
        for line in content.split('\n'):
            match = re.match(import_pattern, line.strip())
            if match:
                imports.append(line.strip())
        
        return imports
    
    def _extract_classes(self, content):
        """Извлекает классы из файла"""
        classes = []
        class_pattern = r'^class\s+(\w+)(?:\([^)]*\))?:'
        
        for line in content.split('\n'):
            match = re.match(class_pattern, line.strip())
            if match:
                classes.append(match.group(1))
                
        return classes
    
    def _extract_functions(self, content):
        """Извлекает функции из файла"""
        functions = []
        func_pattern = r'^def\s+(\w+)\s*\('
        
        for line in content.split('\n'):
            match = re.match(func_pattern, line.strip())
            if match:
                functions.append(match.group(1))
                
        return functions
    
    def _should_skip_file(self, file_path):
        """Проверяет, нужно ли пропустить файл"""
        skip_patterns = [
            '__pycache__',
            '.egg-info',
            'venv',
            '.pytest_cache',
            '.idea',
            '.git'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _check_conflict_with_new_modules(self, file_path):
        """Проверяет конфликт с новыми модулями"""
        # Проверяем, есть ли файлы с похожими именами в новой структуре
        new_module_files = [
            'menu_bar.py',
            'titlebar.py', 
            'file_explorer.py',
            'tab_widget.py',
            'chat_widget.py',
            'terminal_widget.py'
        ]
        
        file_name = file_path.name.lower()
        for new_file in new_module_files:
            if new_file.lower() in file_name or file_name in new_file.lower():
                return True
                
        return False
    
    def generate_recommendations(self):
        """Генерирует рекомендации по очистке"""
        recommendations = []
        
        # Рекомендации по stub-файлам
        if self.analysis_report['stub_files']:
            recommendations.append({
                'category': 'Stub Files',
                'priority': 'HIGH',
                'action': 'REMOVE',
                'description': f"Найдено {len(self.analysis_report['stub_files'])} stub-файлов, которые можно удалить",
                'files': [f['path'] for f in self.analysis_report['stub_files']],
                'reason': 'Заглушки больше не нужны после создания полноценного модульного интерфейса'
            })
        
        # Рекомендации по устаревшим файлам
        if self.analysis_report['deprecated_files']:
            recommendations.append({
                'category': 'Deprecated Files',
                'priority': 'HIGH', 
                'action': 'ARCHIVE',
                'description': f"Найдено {len(self.analysis_report['deprecated_files'])} устаревших файлов",
                'files': [f['path'] for f in self.analysis_report['deprecated_files']],
                'reason': 'Устаревшие файлы можно архивировать'
            })
        
        # Рекомендации по конфликтующим файлам
        if self.analysis_report['conflicting_files']:
            recommendations.append({
                'category': 'Conflicting Files',
                'priority': 'MEDIUM',
                'action': 'REVIEW',
                'description': f"Найдено {len(self.analysis_report['conflicting_files'])} потенциально конфликтующих файлов",
                'files': [f['file'] for f in self.analysis_report['conflicting_files']],
                'reason': 'Необходимо проверить на дублирование функциональности с новыми модулями'
            })
        
        # Анализ дублирующих виджетов
        widget_files = []
        for module_data in self.analysis_report['modules_analyzed'].values():
            widget_files.extend(module_data['widget_files'])
            
        if len(widget_files) > 5:  # Если слишком много виджетов
            recommendations.append({
                'category': 'Widget Duplication',
                'priority': 'MEDIUM',
                'action': 'CONSOLIDATE',
                'description': f"Найдено {len(widget_files)} файлов виджетов, возможно дублирование",
                'files': [f['path'] for f in widget_files],
                'reason': 'Необходимо проверить на дублирование виджетов'
            })
        
        self.analysis_report['recommendations'] = recommendations
    
    def save_report(self, output_file='MODULE_FOLDERS_ANALYSIS.json'):
        """Сохраняет отчет в файл"""
        output_path = self.base_path / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_report, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Отчет сохранен в {output_path}")
        return output_path
    
    def print_summary(self):
        """Выводит краткий отчет"""
        print("\n" + "="*60)
        print("📊 СВОДКА АНАЛИЗА МОДУЛЬНЫХ ПАПОК")
        print("="*60)
        
        for module_name, module_data in self.analysis_report['modules_analyzed'].items():
            print(f"\n📁 {module_name}:")
            print(f"   • Файлов проанализировано: {module_data['files_analyzed']}")
            print(f"   • Stub-файлов: {len(module_data['stub_files'])}")
            print(f"   • Устаревших файлов: {len(module_data['deprecated_files'])}")
            print(f"   • Файлов виджетов: {len(module_data['widget_files'])}")
            print(f"   • Потенциальных конфликтов: {len(module_data['potential_conflicts'])}")
        
        print(f"\n🔍 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего stub-файлов: {len(self.analysis_report['stub_files'])}")
        print(f"   • Всего устаревших файлов: {len(self.analysis_report['deprecated_files'])}")
        print(f"   • Всего конфликтующих файлов: {len(self.analysis_report['conflicting_files'])}")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        for rec in self.analysis_report['recommendations']:
            print(f"   • {rec['category']}: {rec['action']} ({rec['priority']} приоритет)")
            print(f"     {rec['description']}")

def main():
    """Главная функция"""
    base_path = Path(__file__).parent
    detective = ModuleFoldersDetective(base_path)
    
    # Анализируем модули
    report = detective.analyze_all_modules()
    
    # Сохраняем отчет
    detective.save_report()
    
    # Выводим краткую сводку
    detective.print_summary()
    
    print(f"\n✅ Анализ завершен. Полный отчет сохранен в MODULE_FOLDERS_ANALYSIS.json")

if __name__ == "__main__":
    main()
