import sys
import os
sys.path.append('.')

from llm_rotation_config import rate_limit_monitor, LLM_MODELS_CONFIG

print("=== СТАТУС ВСЕХ МОДЕЛЕЙ ===\n")

print("🔍 Blacklist статус:")
blacklist = rate_limit_monitor.get_blacklist_status()
if blacklist:
    for model_id, remaining_time in blacklist.items():
        print(f"  🚫 {model_id}: заблокирована еще {remaining_time} секунд")
else:
    print("  ✅ Нет заблокированных моделей")

print("\n📊 Детальная статистика по моделям:")
for model in LLM_MODELS_CONFIG:
    model_id = model['id']
    usage = rate_limit_monitor.usage[model_id]
    
    is_blocked = rate_limit_monitor.is_model_blocked(model_id)
    can_use = rate_limit_monitor.can_use(model_id)
    
    print(f"\n🎯 {model['name']} ({model_id}):")
    print(f"   Приоритет: {model['priority']}")
    print(f"   Лимиты: RPM={model['rpm']}, TPM={model['tpm']}, RPD={model['rpd']}")
    print(f"   Использовано: RPM={usage['rpm']}, TPM={usage['tpm']}, RPD={usage['rpd']}")
    print(f"   Статус: {'🚫 ЗАБЛОКИРОВАНА' if is_blocked else '✅ Доступна' if can_use else '⚠️ Лимиты исчерпаны'}")

print(f"\n📈 Общая статистика:")
available_count = sum(1 for m in LLM_MODELS_CONFIG if not rate_limit_monitor.is_model_blocked(m['id']) and rate_limit_monitor.can_use(m['id']))
blocked_count = len(blacklist)
limit_exceeded_count = sum(1 for m in LLM_MODELS_CONFIG if not rate_limit_monitor.is_model_blocked(m['id']) and not rate_limit_monitor.can_use(m['id']))

print(f"   ✅ Доступно моделей: {available_count}")
print(f"   🚫 Заблокировано: {blocked_count}")
print(f"   ⚠️ Лимиты исчерпаны: {limit_exceeded_count}")
print(f"   📊 Всего моделей: {len(LLM_MODELS_CONFIG)}")
