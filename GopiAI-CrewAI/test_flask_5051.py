# Простой тест Flask-сервера на другом порту
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Запуск тестового Flask-сервера на 127.0.0.1:5051")
    app.run(host="127.0.0.1", port=5051, debug=True)
    print("После app.run() - это сообщение не должно появиться")
