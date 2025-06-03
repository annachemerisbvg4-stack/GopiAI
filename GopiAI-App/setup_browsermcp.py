#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для настройки BrowserMCP.

Устанавливает и запускает MCP сервер, а также предоставляет инструкции
по установке расширения для браузера.
"""

import subprocess
import sys
import os
import time
import webbrowser

def check_npm():
    """Проверяет, установлен ли npm."""
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_node():
    """Проверяет, установлен ли Node.js."""
    try:
        subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_mcp():
    """Устанавливает MCP сервер."""
    print("Установка MCP сервера...")
    try:
        subprocess.run(["npm", "install", "-g", "@browsermcp/mcp"], check=True)
        print("MCP сервер успешно установлен.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке MCP сервера: {e}")
        return False

def start_mcp_server():
    """Запускает MCP сервер."""
    print("Запуск MCP сервера...")
    
    # Создаем скрипт для запуска сервера
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_mcp_server.js")
    
    # Проверяем, существует ли скрипт
    if not os.path.exists(script_path):
        # Создаем скрипт
        with open(script_path, "w") as f:
            f.write("""// Скрипт для запуска MCP сервера
const { spawn } = require('child_process');
const path = require('path');

console.log('Starting BrowserMCP server...');

// Запускаем MCP сервер
const mcp = spawn('npx', ['@browsermcp/mcp'], {
  stdio: 'inherit',
  shell: true
});

// Обрабатываем события
mcp.on('error', (err) => {
  console.error('Failed to start MCP server:', err);
});

mcp.on('close', (code) => {
  console.log(`MCP server exited with code ${code}`);
});

// Обрабатываем сигналы завершения
process.on('SIGINT', () => {
  console.log('Stopping MCP server...');
  mcp.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('Stopping MCP server...');
  mcp.kill('SIGTERM');
});""")
    
    # Запускаем скрипт
    if sys.platform == "win32":
        # На Windows используем start /b
        subprocess.Popen(
            ["start", "/b", "node", script_path],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    else:
        # На Unix-подобных системах используем nohup
        subprocess.Popen(
            ["nohup", "node", script_path, "&"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    print("MCP сервер запущен в фоновом режиме.")
    
    # Ждем запуска сервера
    print("Ожидание запуска сервера...")
    for _ in range(10):
        try:
            if sys.platform == "win32":
                # На Windows используем curl
                result = subprocess.run(
                    ["curl", "http://localhost:9009/health"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    print("MCP сервер успешно запущен.")
                    return True
            else:
                # На Unix-подобных системах используем curl
                result = subprocess.run(
                    ["curl", "http://localhost:9009/health"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    print("MCP сервер успешно запущен.")
                    return True
        except:
            pass
            
        time.sleep(1)
    
    print("Не удалось проверить запуск MCP сервера. Возможно, он запущен, но не отвечает на порту 9009.")
    return False

def open_extension_page():
    """Открывает страницу расширения в Chrome Web Store."""
    print("Открытие страницы расширения в Chrome Web Store...")
    webbrowser.open("https://chrome.google.com/webstore/detail/browser-mcp/jjnpjkojbmjmlkdbiojmklkdnkjdjnlh")
    print("Пожалуйста, установите расширение и подключитесь к серверу.")

def main():
    """Основная функция."""
    print("Настройка BrowserMCP...")
    
    # Проверяем, установлены ли npm и Node.js
    if not check_npm():
        print("Ошибка: npm не установлен. Пожалуйста, установите Node.js и npm.")
        return
        
    if not check_node():
        print("Ошибка: Node.js не установлен. Пожалуйста, установите Node.js.")
        return
        
    # Устанавливаем MCP сервер
    if not install_mcp():
        print("Не удалось установить MCP сервер. Пожалуйста, установите его вручную с помощью команды: npm install -g @browsermcp/mcp")
        return
        
    # Запускаем MCP сервер
    start_mcp_server()
    
    # Открываем страницу расширения
    open_extension_page()
    
    print("\nИнструкции по установке расширения:")
    print("1. Нажмите кнопку 'Установить' на странице расширения")
    print("2. Подтвердите установку")
    print("3. Нажмите на иконку расширения в панели инструментов браузера")
    print("4. Нажмите кнопку 'Connect' для подключения к MCP серверу")
    
    print("\nНастройка BrowserMCP завершена.")

if __name__ == "__main__":
    main()
