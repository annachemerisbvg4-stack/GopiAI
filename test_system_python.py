# Тест системного Python
import os
import sys

# Путь к файлу для записи
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_python_test.txt")

# Записываем в файл
with open(file_path, "w", encoding="utf-8") as f:
    f.write(f"Тест системного Python\n")
    f.write(f"Python версия: {sys.version}\n")
    f.write(f"Путь к Python: {sys.executable}\n")
    f.write(f"Текущая директория: {os.getcwd()}\n")
    
print(f"Файл создан по пути: {file_path}")
