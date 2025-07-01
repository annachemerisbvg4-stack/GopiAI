#!/usr/bin/env python3
"""
Симуляция исчерпания RPD лимита для демонстрации ротации
"""
import os
from dotenv import load_dotenv
from llm_rotation_config import select_llm_model_safe, rate_limit_monitor

# Загружаем переменные окружения
load_dotenv('.env')

print('🚀 СИМУЛИРУЕМ ИСЧЕРПАНИЕ RPD ЛИМИТА!')
print()

# Симулируем, что у gemini-1.5-flash уже потрачено 50 запросов в день
flash_model = "gemini/gemini-1.5-flash"
print(f"📊 Симулируем исчерпание дневного лимита для {flash_model}")
rate_limit_monitor.usage[flash_model]["rpd"] = 50  # Исчерпываем лимит

print(f"   RPD использовано: {rate_limit_monitor.usage[flash_model]['rpd']}/50")
print()

# Теперь попробуем сделать запросы - система должна переключиться на другую модель
for i in range(5):
    print(f'--- Запрос #{i+1} (Flash исчерпан) ---')
    model = select_llm_model_safe('dialog', tokens=50)
    if model:
        rate_limit_monitor.register_use(model, tokens=50)
        print(f'Выбранная модель: {model}')
        
        # Показываем статистику
        usage = rate_limit_monitor.usage[model]
        config = rate_limit_monitor.models[model]
        print(f'Использование: {usage["rpm"]}/{config["rpm"]} RPM, {usage["tpm"]}/{config["tpm"]} TPM, {usage["rpd"]}/{config["rpd"]} RPD')
    else:
        print('❌ Нет доступных моделей!')
    print()

print('✅ Симуляция завершена!')
