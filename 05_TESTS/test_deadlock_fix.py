#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('C:/Users/crazy/GOPI_AI_MODULES/GopiAI-CrewAI')

from llm_rotation_config import LLM_MODELS_CONFIG, select_llm_model_safe, rate_limit_monitor

def test_deadlock_fix():
    print('[TEST] ТЕСТ ИСПРАВЛЕНИЯ DEADLOCK:')
    print(f'Всего моделей в конфигурации: {len(LLM_MODELS_CONFIG)}')
    print()

    # Тестируем выбор модели для dialog с 150 токенами (как в оригинальной проблеме)
    print('Тест выбора модели gemini/gemini-1.5-flash для dialog с 150 токенами:')
    try:
        # Проверяем доступность модели
        can_use = rate_limit_monitor.can_use('gemini/gemini-1.5-flash', tokens=150)
        print(f'  can_use результат: {can_use}')
        
        # Выбираем модель для задачи dialog
        model = select_llm_model_safe('dialog', tokens=150)
        print(f'  Выбранная модель: {model}')
        
        print('[OK] Тест прошел успешно - deadlock исправлен!')
        
    except Exception as e:
        print(f'[ERROR] Ошибка в тесте: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deadlock_fix()