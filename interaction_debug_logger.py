#!/usr/bin/env python3
"""
Детальный логгер взаимодействий для отслеживания проблем с putter.js и WebChannel
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Настройка логирования
def setup_interaction_logger():
    """Настройка детального логгера для взаимодействий"""
    
    # Создаем директорию для логов
    logs_dir = Path("logs/interaction_debug")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем уникальный файл лога
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"interaction_debug_{timestamp}.log"
    
    # Настройка форматтера
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(levelname)8s | %(name)25s | %(funcName)20s:%(lineno)4d | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Создаем файловый handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Создаем консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Создаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    print(f"🔍 Interaction debug logger initialized")
    print(f"📝 Log file: {log_file}")
    print(f"📊 Logging level: DEBUG")
    
    return log_file

# Декоратор для отслеживания методов
def trace_method(logger_name="TRACE"):
    """Декоратор для отслеживания вызовов методов"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            
            # Логируем вход в метод
            logger.debug(f"▶️ ENTER {func.__name__}")
            logger.debug(f"📥 ARGS: {args[1:] if args else []}")  # Пропускаем self
            logger.debug(f"📥 KWARGS: {kwargs}")
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                logger.debug(f"✅ SUCCESS {func.__name__} ({execution_time:.2f}ms)")
                logger.debug(f"📤 RESULT: {str(result)[:500]}")  # Ограничиваем вывод
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(f"❌ ERROR {func.__name__} ({execution_time:.2f}ms)")
                logger.error(f"💥 EXCEPTION: {type(e).__name__}: {str(e)}")
                logger.error(f"📍 TRACEBACK:", exc_info=True)
                
                raise
            
            finally:
                logger.debug(f"◀️ EXIT {func.__name__}")
        
        return wrapper
    return decorator

# Патчи для отслеживания key components
def patch_webview_bridge():
    """Патчим WebView bridge для отслеживания"""
    
    try:
        # Попробуем найти и импортировать bridge
        from GopiAI.GopiAI-WebView.gopiai.webview.webview_bridge import WebViewBridge
        
        logger = logging.getLogger("WEBVIEW_BRIDGE")
        
        # Сохраняем оригинальные методы
        original_execute_claude_tool = WebViewBridge.execute_claude_tool
        original_get_claude_tools_list = WebViewBridge.get_claude_tools_list
        
        # Патчим execute_claude_tool
        @trace_method("WEBVIEW_BRIDGE")
        def patched_execute_claude_tool(self, tool_name, parameters):
            logger.info(f"🔧 CLAUDE_TOOL_EXECUTE: {tool_name}")
            logger.info(f"📊 TOOL_PARAMETERS: {json.dumps(parameters, indent=2, ensure_ascii=False)}")
            
            result = original_execute_claude_tool(self, tool_name, parameters)
            
            logger.info(f"🎯 CLAUDE_TOOL_RESULT: {json.dumps(result, indent=2, ensure_ascii=False)[:1000]}")
            
            return result
        
        # Патчим get_claude_tools_list
        @trace_method("WEBVIEW_BRIDGE")
        def patched_get_claude_tools_list(self):
            logger.info("📋 GETTING_CLAUDE_TOOLS_LIST")
            
            result = original_get_claude_tools_list(self)
            
            logger.info(f"📋 CLAUDE_TOOLS_LIST: {json.dumps(result, indent=2, ensure_ascii=False)[:1000]}")
            
            return result
        
        # Применяем патчи
        WebViewBridge.execute_claude_tool = patched_execute_claude_tool
        WebViewBridge.get_claude_tools_list = patched_get_claude_tools_list
        
        logger.info("✅ WebView bridge patched successfully")
        
    except ImportError as e:
        logger = logging.getLogger("PATCH")
        logger.warning(f"⚠️ Could not patch WebView bridge: {e}")

def patch_claude_tools_handler():
    """Патчим Claude Tools Handler для отслеживания"""
    
    try:
        from GopiAI.GopiAI-Extensions.claude_tools.claude_tools_handler import ClaudeToolsHandler
        
        logger = logging.getLogger("CLAUDE_TOOLS")
        
        # Сохраняем оригинальные методы
        original_execute_tool = ClaudeToolsHandler.execute_tool
        original_list_tools = ClaudeToolsHandler.list_tools
        
        # Патчим execute_tool
        @trace_method("CLAUDE_TOOLS")
        def patched_execute_tool(self, tool_name, parameters):
            logger.info(f"⚙️ EXECUTING_TOOL: {tool_name}")
            logger.info(f"📊 TOOL_PARAMS: {json.dumps(parameters, indent=2, ensure_ascii=False)}")
            
            result = original_execute_tool(self, tool_name, parameters)
            
            logger.info(f"🎯 TOOL_RESULT: {json.dumps(result, indent=2, ensure_ascii=False)[:1000]}")
            
            return result
        
        # Патчим list_tools
        @trace_method("CLAUDE_TOOLS")
        def patched_list_tools(self):
            logger.info("📋 LISTING_TOOLS")
            
            result = original_list_tools(self)
            
            logger.info(f"📋 TOOLS_LIST: {json.dumps(result, indent=2, ensure_ascii=False)[:1000]}")
            
            return result
        
        # Применяем патчи
        ClaudeToolsHandler.execute_tool = patched_execute_tool
        ClaudeToolsHandler.list_tools = patched_list_tools
        
        logger.info("✅ Claude Tools Handler patched successfully")
        
    except ImportError as e:
        logger = logging.getLogger("PATCH")
        logger.warning(f"⚠️ Could not patch Claude Tools Handler: {e}")

def patch_puter_integration():
    """Патчим интеграцию с puter.js для отслеживания"""
    
    try:
        # Попробуем найти puter integration
        import importlib.util
        
        # Ищем файлы с puter интеграцией
        possible_paths = [
            "GopiAI/GopiAI-WebView/gopiai/webview/puter_integration.py",
            "GopiAI-WebView/gopiai/webview/puter_integration.py",
            "gopiai/webview/puter_integration.py"
        ]
        
        logger = logging.getLogger("PUTER_INTEGRATION")
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"🔍 Found puter integration at: {path}")
                
                spec = importlib.util.spec_from_file_location("puter_integration", path)
                puter_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(puter_module)
                
                # Патчим все функции, которые есть в модуле
                for attr_name in dir(puter_module):
                    attr = getattr(puter_module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        setattr(puter_module, attr_name, trace_method("PUTER")(attr))
                
                logger.info("✅ Puter integration patched successfully")
                break
        else:
            logger.warning("⚠️ Puter integration not found")
            
    except Exception as e:
        logger = logging.getLogger("PATCH")
        logger.warning(f"⚠️ Could not patch puter integration: {e}")

def create_javascript_logger():
    """Создаем JavaScript код для логирования в браузере"""
    
    js_logger_code = """
// Детальный логгер для JavaScript стороны
(function() {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    
    function formatMessage(level, args) {
        const timestamp = new Date().toISOString();
        const message = Array.from(args).map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        
        return `${timestamp} | ${level.padEnd(8)} | JS | ${message}`;
    }
    
    console.log = function(...args) {
        originalLog(formatMessage('INFO', args));
        originalLog.apply(console, args);
    };
    
    console.error = function(...args) {
        originalError(formatMessage('ERROR', args));
        originalError.apply(console, args);
    };
    
    console.warn = function(...args) {
        originalWarn(formatMessage('WARN', args));
        originalWarn.apply(console, args);
    };
    
    // Отслеживание puter.js вызовов
    if (typeof puter !== 'undefined' && puter.ai && puter.ai.chat) {
        const originalChat = puter.ai.chat;
        
        puter.ai.chat = async function(messages, options) {
            console.log('🤖 PUTER.AI.CHAT CALLED');
            console.log('📨 MESSAGES:', messages);
            console.log('⚙️ OPTIONS:', options);
            
            try {
                const result = await originalChat.call(this, messages, options);
                console.log('✅ PUTER.AI.CHAT SUCCESS');
                console.log('📤 RESULT:', result);
                return result;
            } catch (error) {
                console.error('❌ PUTER.AI.CHAT ERROR:', error);
                throw error;
            }
        };
    }
    
    // Отслеживание WebChannel вызовов
    if (typeof QWebChannel !== 'undefined') {
        console.log('🌉 QWebChannel is available');
        
        // Перехватываем WebChannel transport
        if (qt && qt.webChannelTransport) {
            console.log('🚀 WebChannel transport is available');
        }
    }
    
    // Отслеживание bridge вызовов
    window.addEventListener('load', function() {
        if (window.gopiaiChat && window.gopiaiChat.bridge) {
            const bridge = window.gopiaiChat.bridge;
            
            // Патчим execute_claude_tool
            if (bridge.execute_claude_tool) {
                const originalExecute = bridge.execute_claude_tool;
                bridge.execute_claude_tool = async function(toolName, parameters) {
                    console.log('🔧 BRIDGE.EXECUTE_CLAUDE_TOOL CALLED');
                    console.log('🛠️ TOOL_NAME:', toolName);
                    console.log('📊 PARAMETERS:', parameters);
                    
                    try {
                        const result = await originalExecute.call(this, toolName, parameters);
                        console.log('✅ BRIDGE.EXECUTE_CLAUDE_TOOL SUCCESS');
                        console.log('📤 RESULT:', result);
                        return result;
                    } catch (error) {
                        console.error('❌ BRIDGE.EXECUTE_CLAUDE_TOOL ERROR:', error);
                        throw error;
                    }
                };
            }
            
            // Патчим get_claude_tools_list
            if (bridge.get_claude_tools_list) {
                const originalGetTools = bridge.get_claude_tools_list;
                bridge.get_claude_tools_list = async function() {
                    console.log('📋 BRIDGE.GET_CLAUDE_TOOLS_LIST CALLED');
                    
                    try {
                        const result = await originalGetTools.call(this);
                        console.log('✅ BRIDGE.GET_CLAUDE_TOOLS_LIST SUCCESS');
                        console.log('📋 TOOLS_LIST:', result);
                        return result;
                    } catch (error) {
                        console.error('❌ BRIDGE.GET_CLAUDE_TOOLS_LIST ERROR:', error);
                        throw error;
                    }
                };
            }
        }
    });
    
    console.log('🔍 JavaScript interaction logger initialized');
})();
"""
    
    # Сохраняем JavaScript код в файл
    js_file = Path("logs/interaction_debug/js_logger.js")
    js_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_logger_code)
    
    print(f"📝 JavaScript logger created: {js_file}")
    return js_file

def main():
    """Основная функция для запуска отладки"""
    
    print("🚀 Starting GopiAI Interaction Debug Logger")
    print("=" * 60)
    
    # Настраиваем логирование
    log_file = setup_interaction_logger()
    
    # Создаем JavaScript логгер
    js_file = create_javascript_logger()
    
    # Применяем патчи
    print("🔧 Applying patches...")
    patch_webview_bridge()
    patch_claude_tools_handler()
    patch_puter_integration()
    
    logger = logging.getLogger("MAIN")
    logger.info("🚀 GopiAI Interaction Debug Logger started")
    logger.info(f"📝 Log file: {log_file}")
    logger.info(f"📄 JS logger: {js_file}")
    
    print("=" * 60)
    print("📋 ИНСТРУКЦИИ:")
    print("1. Запустите приложение GopiAI")
    print("2. Откройте DevTools в WebView (F12)")
    print("3. Вставьте содержимое js_logger.js в консоль")
    print("4. Попробуйте отправить сообщение")
    print("5. Проверьте логи в консоли и файле")
    print("=" * 60)
    
    # Запускаем основное приложение
    try:
        # Импортируем и запускаем главный модуль
        sys.path.insert(0, os.getcwd())
        
        # Попробуем разные пути к main.py
        possible_main_paths = [
            "GopiAI-UI/gopiai/ui/main.py",
            "GopiAI/GopiAI-UI/gopiai/ui/main.py",
            "main.py"
        ]
        
        for main_path in possible_main_paths:
            if os.path.exists(main_path):
                logger.info(f"🎯 Found main.py at: {main_path}")
                
                # Запускаем main.py
                spec = importlib.util.spec_from_file_location("main", main_path)
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                break
        else:
            print("❌ Не найден main.py файл")
            print("Запустите приложение вручную с примененными патчами")
            
    except KeyboardInterrupt:
        logger.info("👋 Debug session interrupted by user")
    except Exception as e:
        logger.error(f"💥 Error running main: {e}", exc_info=True)
    
    print("🏁 Debug session completed")

if __name__ == "__main__":
    main()