import os
import signal
import subprocess
import sys
import time

def get_python_processes():
    """Получает список всех процессов Python"""
    try:
        # Для Windows
        if sys.platform == 'win32':
            output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV']).decode('cp866')
            lines = output.strip().split('\n')[1:]  # Пропускаем заголовок
            processes = []
            for line in lines:
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    pid = int(parts[1])
                    processes.append(pid)
            return processes
        # Для Unix-подобных систем
        else:
            output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
            lines = output.strip().split('\n')
            processes = []
            for line in lines:
                if 'python' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            processes.append(pid)
                        except ValueError:
                            pass
            return processes
    except Exception as e:
        print(f"Ошибка при получении списка процессов: {e}")
        return []

def kill_process(pid):
    """Завершает процесс по его PID"""
    try:
        # Для Windows
        if sys.platform == 'win32':
            subprocess.call(['taskkill', '/F', '/PID', str(pid)])
        # Для Unix-подобных систем
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"Процесс с PID {pid} успешно завершен")
        return True
    except Exception as e:
        print(f"Ошибка при завершении процесса {pid}: {e}")
        return False

def main():
    """Основная функция для завершения всех процессов Python"""
    print("Поиск процессов Python...")
    processes = get_python_processes()
    
    if not processes:
        print("Процессы Python не найдены")
        return
    
    print(f"Найдено {len(processes)} процессов Python: {processes}")
    
    # Получаем PID текущего процесса
    current_pid = os.getpid()
    print(f"Текущий процесс имеет PID: {current_pid}")
    
    # Завершаем все процессы Python, кроме текущего
    for pid in processes:
        if pid != current_pid:
            kill_process(pid)
    
    print("Все процессы Python (кроме текущего) завершены")
    
    # Проверяем, что файлы памяти доступны
    memory_path = r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory\vectors\documents"
    try:
        # Проверяем, существует ли файл
        if os.path.exists(memory_path):
            # Пробуем открыть файл для записи
            with open(memory_path, 'a') as f:
                pass
            print(f"Файл {memory_path} доступен для записи")
        else:
            print(f"Файл {memory_path} не существует")
    except Exception as e:
        print(f"Ошибка при проверке доступа к файлу {memory_path}: {e}")

if __name__ == "__main__":
    main()
