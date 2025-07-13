"""
Скрипт для завершения всех процессов, слушающих порт 5051
"""

import os
import subprocess
import re
import sys

def find_processes_on_port(port):
    """Находит все процессы, слушающие указанный порт"""
    try:
        # Запускаем netstat для получения списка процессов
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode('utf-8')
        
        # Извлекаем PID из вывода netstat
        pids = set()
        for line in output.splitlines():
            if "LISTENING" in line:
                match = re.search(r'\s+(\d+)$', line)
                if match:
                    pids.add(match.group(1))
        
        return list(pids)
    except subprocess.CalledProcessError:
        # Если порт не найден, возвращаем пустой список
        return []

def kill_processes(pids):
    """Завершает процессы по их PID"""
    for pid in pids:
        try:
            print(f"Завершение процесса с PID {pid}...")
            subprocess.call(f"taskkill /F /PID {pid}", shell=True)
        except Exception as e:
            print(f"Ошибка при завершении процесса {pid}: {e}")

if __name__ == "__main__":
    port = 5051
    print(f"Поиск процессов на порту {port}...")
    pids = find_processes_on_port(port)
    
    if not pids:
        print(f"Процессы на порту {port} не найдены.")
        sys.exit(0)
    
    print(f"Найдены процессы на порту {port}: {', '.join(pids)}")
    kill_processes(pids)
    
    # Проверяем, что все процессы завершены
    remaining_pids = find_processes_on_port(port)
    if remaining_pids:
        print(f"ВНИМАНИЕ: Не удалось завершить все процессы. Остались: {', '.join(remaining_pids)}")
    else:
        print(f"Все процессы на порту {port} успешно завершены.")
