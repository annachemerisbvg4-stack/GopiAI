#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('C:/Users/crazy/GOPI_AI_MODULES/GopiAI-CrewAI')

from llm_rotation_config import LLM_MODELS_CONFIG, select_llm_model_safe, rate_limit_monitor

def test_rotation():
    print('🔍 ПРОВЕРКА РОТАЦИИ МОДЕЛЕЙ:')
    print(f'Всего моделей в конфигурации: {len(LLM_MODELS_CONFIG)}')
    print()

    # Проверяем API ключи
    google_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if google_key:
        print('Google API Key: ✅ Найден')
    else:
        print('Google API Key: ❌ Отсутствует')
    print()

    # Проверяем какие модели поддерживают dialog
    dialog_models = [m for m in LLM_MODELS_CONFIG if 'dialog' in m['type']]
    print(f'Модели для dialog: {len(dialog_models)}')
    for model in dialog_models:
        name = model["name"]
        model_id = model["id"]
        priority = model["priority"]
        print(f'  - {name} (id: {model_id}, priority: {priority})')
    print()

    # Проверяем текущее использование
    print('Текущее использование:')
    for model_id in rate_limit_monitor.usage:
        usage = rate_limit_monitor.usage[model_id]
        model_config = rate_limit_monitor.models[model_id]
        rpm_used = usage["rpm"]
        rpm_limit = model_config["rpm"]
        tpm_used = usage["tpm"]
        tpm_limit = model_config["tpm"]
        print(f'  {model_id}: RPM {rpm_used}/{rpm_limit}, TPM {tpm_used}/{tpm_limit}')
    print()

    # Тестируем выбор модели
    print('Тест выбора модели:')
    for i in range(10):
        model = select_llm_model_safe('dialog', tokens=1000)
        print(f'  Попытка {i+1}: {model}')
        if model:
            rate_limit_monitor.register_use(model, tokens=1000)
            # Проверяем, можем ли еще использовать эту модель
            can_use = rate_limit_monitor.can_use(model, tokens=1000)
            print(f'    -> Можем еще использовать: {can_use}')
        print()

if __name__ == "__main__":
    test_rotation()
