# Отладочный запуск CrewAI API сервера
import os
import sys
import traceback

# Путь к файлу для записи отладочной информации
debug_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crewai_debug.txt")

try:
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(f"Python версия: {sys.version}\n")
        f.write(f"Путь к Python: {sys.executable}\n")
        f.write(f"Текущая директория: {os.getcwd()}\n\n")
        f.write("Начало импорта модулей...\n")
        
        # Пробуем импортировать необходимые модули
        f.write("Импорт Flask...\n")
        import flask
        f.write(f"Flask версия: {flask.__version__}\n")
        
        f.write("Импорт CORS...\n")
        from flask_cors import CORS
        f.write("CORS импортирован успешно\n")
        
        f.write("Импорт локальных модулей...\n")
        f.write("Импорт rag_system...\n")
        import rag_system
        f.write("rag_system импортирован успешно\n")
        
        f.write("Импорт smart_delegator...\n")
        import smart_delegator
        f.write("smart_delegator импортирован успешно\n")
        
        f.write("Импорт chat_async_handler...\n")
        import chat_async_handler
        f.write("chat_async_handler импортирован успешно\n")
        
        f.write("Создание экземпляра Flask...\n")
        app = flask.Flask(__name__)
        CORS(app)
        f.write("Экземпляр Flask создан успешно\n")
        
        f.write("Инициализация RAG системы...\n")
        rag = rag_system.get_rag_system()
        f.write("RAG система инициализирована успешно\n")
        
        f.write("Инициализация SmartDelegator...\n")
        delegator = smart_delegator.SmartDelegator(rag)
        f.write("SmartDelegator инициализирован успешно\n")
        
        f.write("Определение маршрутов Flask...\n")
        
        @app.route('/api/health', methods=['GET'])
        def health_check():
            return flask.jsonify({"status": "ok"})
        
        f.write("Маршруты определены успешно\n")
        
        f.write("Запуск сервера на порту 5051...\n")
        f.flush()  # Принудительная запись в файл
        
        # Запуск сервера
        app.run(host="127.0.0.1", port=5051, debug=False)
        
        f.write("Сервер запущен успешно (это сообщение не должно появиться)\n")
        
except Exception as e:
    with open(debug_file, "a", encoding="utf-8") as f:
        f.write(f"\n\nПроизошла ошибка: {e}\n")
        f.write("Трассировка стека:\n")
        f.write(traceback.format_exc())
        
print(f"Отладочная информация записана в {debug_file}")
