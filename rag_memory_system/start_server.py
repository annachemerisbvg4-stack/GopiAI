#!/usr/bin/env python3
"""
Скрипт для запуска RAG Memory API сервера
"""
import uvicorn
from api import app

if __name__ == "__main__":
    print("🚀 Запуск RAG Memory API сервера...")
    print("📍 Веб-интерфейс будет доступен по адресу: http://localhost:8001")
    print("📍 API документация: http://localhost:8001/docs")
    print("📍 Для остановки сервера нажмите Ctrl+C")    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
