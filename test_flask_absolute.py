# Тест Flask с системным Python и абсолютными путями
from flask import Flask
import os
import sys

app = Flask(__name__)

@app.route('/test')
def test():
    return "Test OK"

if __name__ == '__main__':
    # Абсолютный путь к файлу
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flask_absolute_test.txt")
    
    # Создаем файл для проверки работоспособности
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Тест Flask с системным Python и абсолютными путями\n")
        f.write(f"Python версия: {sys.version}\n")
        f.write(f"Текущая директория: {os.getcwd()}\n")
        f.write(f"Путь к файлу: {file_path}\n")
    
    print(f"Файл создан по пути: {file_path}")
    print("Запуск Flask на порту 5053...")
    
    # Запускаем Flask
    app.run(host="127.0.0.1", port=5053, debug=True)
