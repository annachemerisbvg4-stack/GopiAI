# Проверка версии Flask и его работоспособности
import sys
import flask

print(f"Python версия: {sys.version}")
print(f"Flask версия: {flask.__version__}")
print("Flask импортирован успешно.")

try:
    from flask import Flask
    app = Flask(__name__)
    print("Объект Flask создан успешно.")
except Exception as e:
    print(f"Ошибка при создании Flask: {e}")

print("Скрипт выполнен успешно.")
