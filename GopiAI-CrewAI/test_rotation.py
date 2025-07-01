#!/usr/bin/env python3
"""
Простой тест ротации моделей
"""
import os
from dotenv import load_dotenv
from llm_rotation_config import select_llm_model_safe, rate_limit_monitor

# Загружаем переменные окружения
load_dotenv('.env')

print('🚀 ТЕСТИРУЕМ РОТАЦИЮ С МАЛЕНЬКИМИ ЛИМИТАМИ!')
print()

# Делаем несколько запросов подряд, чтобы увидеть ротацию
for i in range(8):
    print(f'--- Запрос #{i+1} ---')
    model = select_llm_model_safe('dialog', tokens=50)
    if model:
        rate_limit_monitor.register_use(model, tokens=50)
        print(f'Выбранная модель: {model}')
        
        # Показываем статистику
        usage = rate_limit_monitor.usage[model]
        config = rate_limit_monitor.models[model]
        print(f'Использование: {usage["rpm"]}/{config["rpm"]} RPM, {usage["tpm"]}/{config["tpm"]} TPM')
    else:
        print('❌ Нет доступных моделей!')
    print()

print('✅ Тест ротации завершен!')
