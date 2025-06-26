#!/bin/bash

echo "======================================================"
echo "   Тестирование интеграции CrewAI с чатом"
echo "======================================================"
echo ""

# Проверяем наличие окружения
if [ ! -d "crewai_env" ]; then
    echo "[ОШИБКА] Окружение CrewAI не найдено!"
    echo "Сначала запустите run_crewai_api_server.sh для создания окружения."
    exit 1
fi

# Активируем окружение CrewAI
echo "[1/2] Активация окружения CrewAI..."
source crewai_env/bin/activate
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось активировать окружение CrewAI!"
    exit 1
fi

# Запускаем тестирование
echo "[2/2] Запуск тестирования интеграции..."
echo ""

python test_chat_integration.py

# В случае ошибки
if [ $? -ne 0 ]; then
    echo ""
    echo "[ОШИБКА] Не удалось выполнить тестирование!"
    echo "Проверьте, запущен ли API сервер (run_crewai_api_server.sh)."
fi

echo "Нажмите Enter для завершения..."
read