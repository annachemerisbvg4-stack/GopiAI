# Тест Flask с системным Python
from flask import Flask
import os

app = Flask(__name__)

@app.route('/test')
def test():
    return "Test OK"

if __name__ == '__main__':
    # Создаем файл для проверки работоспособности
    with open("flask_system_test.txt", "w", encoding="utf-8") as f:
        f.write("Тест Flask с системным Python\n")
        f.write(f"Текущая директория: {os.getcwd()}\n")
    
    print("Запуск Flask на порту 5052...")
    app.run(host="127.0.0.1", port=5052, debug=True)
