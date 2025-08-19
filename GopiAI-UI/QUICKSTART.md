# 🚀 Быстрый запуск GopiAI

## Мгновенный старт (демо-режим)

```bash
# 1. Установите зависимости
pip install flask flask-cors google-generativeai python-dotenv

# 2. Запустите демо
python demo_app.py

# 3. Откройте браузер
# http://localhost:12000
```

## Полная настройка (с Gemini API)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте API ключ
cp .env.example .env
# Отредактируйте .env и добавьте ваш GEMINI_API_KEY

# 3. Запустите приложение
python run.py

# 4. Откройте браузер
# http://localhost:12001
```

## Получение API ключа

1. Перейдите на https://makersuite.google.com/app/apikey
2. Создайте новый API ключ
3. Скопируйте ключ в файл `.env`

## Готово! 🎉

Ваш веб-интерфейс для Gemini AI готов к использованию!