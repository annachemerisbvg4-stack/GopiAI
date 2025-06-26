#!/usr/bin/env python3
"""
🐞 Debug Wrapper для CrewAI API Server
Запускает сервер в отказоустойчивом режиме с перехватом всех ошибок
"""

import os
import sys
import traceback
import time
import subprocess
from pathlib import Path

def run_server_with_retry():
    """Запускает сервер с автоматическим перезапуском при сбое"""
    
    max_retries = 3
    retry_count = 0
    retry_delay = 5  # секунд
    
    print("=" * 60)
    print("🐞 DEBUG WRAPPER для CrewAI API Server")
    print("=" * 60)
    print("Этот скрипт запускает сервер с автоматическим перезапуском при сбое")
    print()
    
    while retry_count < max_retries:
        try:
            print(f"Попытка запуска сервера ({retry_count + 1}/{max_retries})...")
            
            # Используем subprocess для запуска сервера в отдельном процессе
            process = subprocess.Popen([sys.executable, "crewai_api_server.py"])
            
            # Ждем завершения процесса
            process.wait()
            
            # Если процесс завершился с ошибкой
            if process.returncode != 0:
                print(f"❌ Сервер завершился с кодом {process.returncode}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"⏳ Повторная попытка через {retry_delay} секунд...")
                    time.sleep(retry_delay)
                else:
                    print("❌ Превышено максимальное количество попыток")
            else:
                # Нормальное завершение
                print("✅ Сервер завершил работу без ошибок")
                break
                
        except KeyboardInterrupt:
            print("\n⛔ Работа прервана пользователем")
            break
        except Exception as e:
            print(f"❌ Ошибка при запуске сервера: {e}")
            traceback.print_exc()
            retry_count += 1
            if retry_count < max_retries:
                print(f"⏳ Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                print("❌ Превышено максимальное количество попыток")
    
    print("\n✋ Завершение работы debug wrapper")

if __name__ == "__main__":
    run_server_with_retry()