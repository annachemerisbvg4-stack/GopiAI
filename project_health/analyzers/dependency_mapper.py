from datetime import datetime
import os
import re
import json


def analyze_project(
    directory,
    output_file="project_map.json",
    extensions=[".py", ".js", ".ts", ".jsx", ".tsx"],
    ignore_dirs={"__pycache__", ".git", "node_modules", "venv", "env", ".venv", 
                 "rag_memory_env", "project_health", "rag_memory_system", "tests", ".pytest_cache", "dist", "build", ".egg-info",
                 "logs", ".mypy_cache", ".tox"},
):
    # Создаем словарь для хранения зависимостей
    dependencies = {}
    all_files = []

    # Анализируем импорты в файлах
    for root, dirs, files in os.walk(directory):
        # Исключаем ненужные директории
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.endswith('.egg-info')]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                all_files.append(rel_path)

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
                    dependencies[rel_path] = []

                    for imp in imports:
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
                                dependencies[rel_path].append(imp_path)
                except Exception as e:
                    print(f"Error processing {rel_path}: {e}")

    # Добавляем метаданные
    result = {
        "generated_at": datetime.now().isoformat(),
        "dependencies": dependencies,
        "files_count": len(all_files),
        "relationships_count": sum(len(deps) for deps in dependencies.values()),
    }

    # Сохраняем результат
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Project map updated at {result['generated_at']}")
    return result


if __name__ == "__main__":
    # Получаем родительскую директорию (GOPI_AI_MODULES)
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"Analyzing project directory: {project_dir}")
    analyze_project(project_dir)
