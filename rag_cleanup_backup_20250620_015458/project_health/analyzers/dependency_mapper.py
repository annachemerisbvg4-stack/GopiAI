from datetime import datetime
import os
import re
import json


def analyze_project(
    directory,
    output_file=None,  # Будет установлен автоматически в project_health/reports/
    extensions=[".py", ".js", ".ts", ".jsx", ".tsx"],
    ignore_dirs={"__pycache__", ".git", "node_modules", "venv", "env", ".venv", 
                 "rag_memory_env", "project_health", "rag_memory_system", "tests", ".pytest_cache", "dist", "build", ".egg-info",
                 "logs", ".mypy_cache", ".tox"},
):    # Создаем словарь для хранения зависимостей
    dependencies = {}
    all_files = []
    
    # Устанавливаем путь для выходного файла
    if output_file is None:
        reports_dir = os.path.join(directory, "project_health", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        output_file = os.path.join(reports_dir, "project_map.json")

    def normalize_path(path):
        """Нормализуем пути для краткости и удобства"""
        # Убираем расширение для основных путей
        if path.endswith('.py'):
            path = path[:-3]
        # Заменяем разделители на точки для модулей
        path = path.replace(os.sep, '.')
        # Убираем двойные точки
        path = path.replace('..', '.')
        # Убираем лидирующие и завершающие точки
        return path.strip('.')

    # Создаем словарь модулей для группировки
    modules = {}
    
    def get_module_group(file_path):
        """Определяем к какому модулю относится файл"""
        parts = file_path.split(os.sep)
        if len(parts) > 0:
            if parts[0].startswith('GopiAI-'):
                return parts[0]
            elif parts[0] == 'UI':
                return 'UI'
            elif parts[0] == 'gopiai':
                return 'gopiai'
            elif parts[0] in ['project_health', 'rag_memory_system']:
                return parts[0]
        return 'root'    # Анализируем импорты в файлах
    for root, dirs, files in os.walk(directory):
        # Исключаем ненужные директории
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.endswith('.egg-info')]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                all_files.append(rel_path)
                
                # Определяем модуль и нормализованный путь
                module_group = get_module_group(rel_path)
                normalized_path = normalize_path(rel_path)
                
                # Инициализируем модуль, если его ещё нет
                if module_group not in modules:
                    modules[module_group] = {
                        'files': [],
                        'dependencies': {},
                        'file_count': 0
                    }

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Ищем Python импорты
                    imports = []
                    if file.endswith('.py'):
                        # Различные паттерны импортов
                        imports += re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import', content)
                        imports += re.findall(r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
                        imports += re.findall(r'from\s+\.([a-zA-Z0-9_.]*)\s+import', content)
                        imports += re.findall(r'from\s+\.\.([a-zA-Z0-9_.]*)\s+import', content)
                    else:
                        # Для JS/TS файлов - оригинальный паттерн
                        imports = re.findall(r'import\s+.*?from\s+[\'"](.+?)[\'"]', content)
                      # Обрабатываем импорты
                    processed_imports = []
                    dependencies[rel_path] = []
                    
                    for imp in imports:
                        # Нормализуем импорт для краткости
                        normalized_import = normalize_path(imp) if '.' in imp else imp
                        processed_imports.append(normalized_import)
                        
                        # Преобразование относительных импортов в абсолютные пути (упрощенно)
                        if imp.startswith("."):
                            base_dir = os.path.dirname(rel_path)
                            if imp.startswith("./"):
                                imp_path = os.path.normpath(
                                    os.path.join(base_dir, imp[2:])
                                )
                            elif imp.startswith("../"):
                                imp_path = os.path.normpath(os.path.join(base_dir, imp))
                            else:
                                imp_path = os.path.normpath(
                                    os.path.join(base_dir, imp[1:])
                                )

                            # Добавляем расширение, если его нет
                            if not any(imp_path.endswith(ext) for ext in extensions):
                                for ext in extensions:
                                    if os.path.exists(
                                        os.path.join(directory, imp_path + ext)
                                    ):
                                        imp_path += ext
                                        break

                            if os.path.exists(os.path.join(directory, imp_path)):
                                dependencies[rel_path].append(normalize_path(imp_path))
                        else:
                            # Внешние библиотеки и абсолютные импорты
                            dependencies[rel_path].append(normalized_import)
                    
                    # Добавляем файл в модуль
                    modules[module_group]['files'].append(normalized_path)
                    modules[module_group]['dependencies'][normalized_path] = processed_imports
                    modules[module_group]['file_count'] += 1
                    
                except Exception as e:
                    print(f"Error processing {rel_path}: {e}")

    # Создаем улучшенную структуру данных
    result = {
        "generated_at": datetime.now().isoformat(),
        "project_name": "GopiAI",
        "version": "1.0",
        "summary": {
            "total_files": len(all_files),
            "total_modules": len(modules),
            "total_dependencies": sum(len(deps) for deps in dependencies.values()),
            "modules_overview": {name: mod['file_count'] for name, mod in modules.items()}
        },
        "modules": modules,
        "raw_dependencies": dependencies,  # Оставляем для совместимости
        "output_path": output_file
    }    # Сохраняем результат
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Project map saved to: {output_file}")
    print(f"📊 Analysis summary:")
    print(f"   - Total files: {result['summary']['total_files']}")
    print(f"   - Total modules: {result['summary']['total_modules']}")
    print(f"   - Total dependencies: {result['summary']['total_dependencies']}")
    print(f"   - Generated at: {result['generated_at']}")
    
    return result


if __name__ == "__main__":
    # Получаем родительскую директорию (GOPI_AI_MODULES)
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"🔍 Analyzing project directory: {project_dir}")
    analyze_project(project_dir)
