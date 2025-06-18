#!/usr/bin/env python3
"""
Windows Server Diagnostics
==========================
Диагностика проблем с серверами в Windows
"""
import socket
import subprocess
import sys
import os
from pathlib import Path

def check_port_available(port, host='127.0.0.1'):
    """Проверяет доступность порта"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def check_listening_ports():
    """Проверяет какие порты слушают"""
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        listening = [line for line in result.stdout.split('\n') if 'LISTENING' in line]
        return listening[:10]  # Первые 10
    except Exception as e:
        return [f"Ошибка: {e}"]

def check_firewall_rules():
    """Проверяет правила брандмауэра для Python"""
    try:
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
            'name=Python', 'dir=in'
        ], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Ошибка проверки брандмауэра: {e}"

def test_simple_server():
    """Тестирует простой HTTP сервер"""
    ports_to_test = [8080, 8000, 9999, 3000, 5000]
    
    for port in ports_to_test:
        if check_port_available(port):
            print(f"✅ Порт {port} доступен")
            try:
                # Пробуем запустить простой сервер
                import http.server
                import socketserver
                import threading
                import time
                
                class TestHandler(http.server.SimpleHTTPRequestHandler):
                    def do_GET(self):
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'Test server works!')
                
                httpd = socketserver.TCPServer(("", port), TestHandler)
                
                # Запускаем в отдельном потоке
                server_thread = threading.Thread(target=httpd.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                
                time.sleep(1)
                
                # Проверяем что сервер отвечает
                import urllib.request
                try:
                    response = urllib.request.urlopen(f'http://localhost:{port}')
                    if response.status == 200:
                        print(f"🎉 Тестовый сервер на порту {port} работает!")
                        httpd.shutdown()
                        return port
                except Exception as e:
                    print(f"❌ Сервер запустился, но не отвечает: {e}")
                
                httpd.shutdown()
                
            except Exception as e:
                print(f"❌ Ошибка запуска сервера на порту {port}: {e}")
        else:
            print(f"❌ Порт {port} занят или недоступен")
    
    return None

def check_windows_specific():
    """Проверяет Windows-специфичные проблемы"""
    issues = []
    
    # Проверяем UAC
    try:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin():
            issues.append("✅ Права администратора есть")
        else:
            issues.append("⚠️  Нет прав администратора - попробуйте запустить как админ")
    except:
        issues.append("❓ Не удалось проверить права администратора")
    
    # Проверяем Windows Defender
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            'Get-MpPreference | Select-Object -ExpandProperty DisableRealtimeMonitoring'
        ], capture_output=True, text=True)
        
        if 'False' in result.stdout:
            issues.append("⚠️  Windows Defender включен - может блокировать серверы")
        else:
            issues.append("✅ Windows Defender не блокирует")
    except:
        issues.append("❓ Не удалось проверить Windows Defender")
    
    # Проверяем переменные окружения
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        if os.environ.get(var):
            issues.append(f"⚠️  Найден прокси: {var}={os.environ[var]}")
    
    return issues

def main():
    print("🔍 Windows Server Diagnostics")
    print("=" * 50)
    
    print("\n1. Проверка доступности портов:")
    working_port = test_simple_server()
    
    print("\n2. Активные соединения:")
    listening = check_listening_ports()
    for line in listening:
        print(f"  {line}")
    
    print("\n3. Правила брандмауэра:")
    firewall = check_firewall_rules()
    print(firewall[:500] + "..." if len(firewall) > 500 else firewall)
    
    print("\n4. Windows-специфичные проблемы:")
    issues = check_windows_specific()
    for issue in issues:
        print(f"  {issue}")
    
    print("\n🎯 РЕКОМЕНДАЦИИ:")
    
    if working_port:
        print(f"✅ Можно использовать порт {working_port} для RAG сервера")
    else:
        print("❌ Все тестовые порты недоступны - серьезная проблема с сетью")
        print("   Попробуйте:")
        print("   - Запустить как администратор") 
        print("   - Отключить антивирус временно")
        print("   - Проверить корпоративные ограничения")
    
    print("\nДля RAG сервера:")
    print(f"1. Отредактируйте config.py или run_server.py")
    print(f"2. Измените порт на {working_port or '9999'}")
    print("3. Запустите сервер как администратор")

if __name__ == "__main__":
    main()