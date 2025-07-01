#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('C:/Users/crazy/GOPI_AI_MODULES/GopiAI-CrewAI')

from llm_rotation_config import LLM_MODELS_CONFIG, select_llm_model_safe, rate_limit_monitor

def test_real_rotation():
    print('🔥 ТЕСТ РЕАЛЬНОЙ РОТАЦИИ ПРИ ВЫСОКОЙ НАГРУЗКЕ:')
    print()
    
    # Симулируем РЕАЛЬНУЮ нагрузку - много больших запросов
    for round_num in range(1, 6):
        print(f"\n🎯 === РАУНД {round_num} ===")
        
        # В каждом раунде делаем 40 запросов по 3000 токенов
        # Это быстро исчерпает лимиты первой модели
        for i in range(40):
            model = select_llm_model_safe('dialog', tokens=3000)
            if model:
                rate_limit_monitor.register_use(model, tokens=3000)
                
                # Проверяем статус после каждого запроса
                usage = rate_limit_monitor.usage[model]
                model_config = rate_limit_monitor.models[model]
                rpm_percent = (usage["rpm"] / model_config["rpm"]) * 100
                tpm_percent = (usage["tpm"] / model_config["tpm"]) * 100
                
                print(f"  Запрос {i+1}: {model} -> RPM: {usage['rpm']}/{model_config['rpm']} ({rpm_percent:.1f}%), TPM: {usage['tpm']}/{model_config['tpm']} ({tpm_percent:.1f}%)")
                
                # Если лимиты близки к исчерпанию, сообщаем об этом
                if rpm_percent > 80 or tpm_percent > 80:
                    print(f"    ⚠️ ВНИМАНИЕ: Модель {model} близка к лимиту!")
            else:
                print(f"  Запрос {i+1}: ❌ Нет доступных моделей!")
        
        print(f"\n📊 Статистика после раунда {round_num}:")
        total_requests = 0
        for model_id in rate_limit_monitor.usage:
            usage = rate_limit_monitor.usage[model_id]
            model_config = rate_limit_monitor.models[model_id]
            if usage["rpm"] > 0:
                rpm_percent = (usage["rpm"] / model_config["rpm"]) * 100
                tpm_percent = (usage["tpm"] / model_config["tpm"]) * 100
                total_requests += usage["rpm"]
                print(f"  {model_id}: {usage['rpm']} запросов, {usage['tpm']} токенов (RPM: {rpm_percent:.1f}%, TPM: {tpm_percent:.1f}%)")
        
        print(f"  ИТОГО запросов в этом раунде: {total_requests}")
        
        # Маленькая пауза между раундами
        import time
        time.sleep(2)

if __name__ == "__main__":
    test_real_rotation()
