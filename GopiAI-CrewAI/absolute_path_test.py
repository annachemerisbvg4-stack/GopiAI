# Тест записи в файл с абсолютным путем
import os

# Получаем абсолютный путь к текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))
# Формируем абсолютный путь к файлу
file_path = os.path.join(current_dir, "absolute_test.txt")

# Записываем в файл
with open(file_path, "w", encoding="utf-8") as f:
    f.write("Тест записи в файл с абсолютным путем")
    
print(f"Файл создан по пути: {file_path}")
