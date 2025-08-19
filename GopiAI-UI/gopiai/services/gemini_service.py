"""
Сервис для работы с Gemini CLI.
Обеспечивает взаимодействие с Gemini CLI через subprocess.
"""

import subprocess
import json
import os
from typing import Dict, List, Optional, Union
from pathlib import Path
import shlex
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, gemini_path: str = None):
        """
        Инициализация сервиса Gemini.
        
        Args:
            gemini_path: Путь к исполняемому файлу gemini-cli. Если None, будет использован gemini из PATH.
        """
        self.gemini_path = gemini_path or "gemini"
        self._check_gemini_installed()
    
    def _run_command(self, command: str, input_data: str = None, cwd: str = None) -> Dict:
        """
        Выполняет команду Gemini CLI и возвращает результат.
        
        Args:
            command: Команда для выполнения
            input_data: Входные данные для команды
            cwd: Рабочая директория
            
        Returns:
            Словарь с результатом выполнения команды
        """
        try:
            if not command.startswith(self.gemini_path):
                command = f"{self.gemini_path} {command}"
                
            logger.debug(f"Выполнение команды: {command}")
            
            process = subprocess.Popen(
                shlex.split(command),
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd or os.getcwd()
            )
            
            stdout, stderr = process.communicate(input=input_data)
            
            if process.returncode != 0:
                error_msg = f"Ошибка выполнения команды: {stderr}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
                
            try:
                # Пытаемся распарсить JSON ответ
                return {"status": "success", "data": json.loads(stdout)}
            except json.JSONDecodeError:
                # Если ответ не JSON, возвращаем как есть
                return {"status": "success", "data": stdout.strip()}
                
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.exception(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _check_gemini_installed(self) -> bool:
        """Проверяет, установлен ли Gemini CLI."""
        try:
            result = subprocess.run(
                [self.gemini_path, "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"Gemini CLI найден: {result.stdout.strip()}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке установки Gemini CLI: {e}")
            return False
    
    def generate_text(self, prompt: str, model: str = "gemini-pro", **kwargs) -> Dict:
        """
        Генерация текста с помощью Gemini.
        
        Args:
            prompt: Текст запроса
            model: Модель для генерации (по умолчанию: gemini-pro)
            **kwargs: Дополнительные параметры (temperature, max_tokens и т.д.)
            
        Returns:
            Словарь с результатом генерации
        """
        # Собираем аргументы команды
        args = [f"--model={model}"]
        
        for key, value in kwargs.items():
            if value is not None:
                args.append(f"--{key.replace('_', '-')}={value}")
        
        command = f"generate {' '.join(args)}"
        return self._run_command(command, input_data=prompt)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "gemini-pro", **kwargs) -> Dict:
        """
        Чат с сохранением контекста.
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
            model: Модель для чата (по умолчанию: gemini-pro)
            **kwargs: Дополнительные параметры
            
        Returns:
            Словарь с ответом модели
        """
        # Преобразуем историю сообщений в формат, понятный Gemini CLI
        chat_history = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "human"] else "model"
            chat_history.append(f"{role}: {msg['content']}")
        
        prompt = "\n".join(chat_history)
        return self.generate_text(prompt, model=model, **kwargs)
    
    def get_models(self) -> Dict:
        """Получает список доступных моделей."""
        return self._run_command("models list")
    
    def get_model_info(self, model_id: str) -> Dict:
        """Получает информацию о конкретной модели."""
        return self._run_command(f"models describe {model_id}")

# Сиглтон экземпляр сервиса
gemini_service = GeminiService()
