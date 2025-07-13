# Скрипт для записи отладочной информации в файл
import sys
import os
import time

# Открываем файл для записи
with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write(f"Скрипт запущен в {time.ctime()}\n")
    f.write(f"Python версия: {sys.version}\n")
    f.write(f"Текущая директория: {os.getcwd()}\n")
    
    try:
        # Пытаемся импортировать Flask
        import flask
        f.write(f"Flask версия: {flask.__version__}\n")
        
        # Пытаемся создать приложение Flask
        from flask import Flask
        app = Flask(__name__)
        f.write("Объект Flask создан успешно.\n")
        
        # Пытаемся запустить сервер на порту 5052
        f.write("Пытаемся запустить Flask на порту 5052...\n")
        f.flush()  # Принудительно записываем в файл
        
        @app.route('/test')
        def test():
            return "Test OK"
        
        # Запускаем сервер в отдельном потоке, чтобы он не блокировал выполнение
        import threading
        def run_server():
            app.run(host="127.0.0.1", port=5052, debug=False)
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        f.write("Сервер запущен в фоновом режиме.\n")
        f.flush()
        
        # Ждем 5 секунд
        time.sleep(5)
        
        # Проверяем, запущен ли сервер
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 5052))
            if result == 0:
                f.write("Порт 5052 открыт и доступен!\n")
            else:
                f.write(f"Порт 5052 недоступен, код ошибки: {result}\n")
            sock.close()
        except Exception as e:
            f.write(f"Ошибка при проверке порта: {e}\n")
        
    except Exception as e:
        f.write(f"Произошла ошибка: {e}\n")
    
    f.write("Скрипт завершен.\n")
