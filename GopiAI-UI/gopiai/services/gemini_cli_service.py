"""
Асинхронный сервис для работы с Gemini API через CLI с поддержкой OAuth.
"""

import os
import subprocess
import threading
import queue
import logging
import re

logger = logging.getLogger(__name__)

class GeminiCliService:
    def __init__(self, output_queue: queue.Queue):
        """
        Инициализация сервиса Gemini CLI.

        Args:
            output_queue: Очередь для отправки результатов и URL для OAuth в основной поток UI.
        """
        self.output_queue = output_queue
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        logger.info("Асинхронный Gemini CLI Service инициализирован.")

    def _run_in_thread(self, command: list):
        """
        Запускает команду gemini в отдельном потоке и читает ее вывод в реальном времени.
        """
        try:
            env = os.environ.copy()
            if self.api_key:
                env['GEMINI_API_KEY'] = self.api_key

            logger.info(f"Запуск в потоке: {' '.join(command)}")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                bufsize=1 # Line-buffered
            )

            # Паттерн для поиска URL-адреса OAuth
            oauth_url_pattern = re.compile(r'https?://accounts\.google\.com/o/oauth2/v2/auth\S+')

            full_response = []

            # Читаем stdout в реальном времени
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    line_stripped = line.strip()
                    logger.debug(f"CLI stdout: {line_stripped}")

                    # Ищем URL для OAuth
                    match = oauth_url_pattern.search(line_stripped)
                    if match:
                        url = match.group(0)
                        logger.info(f"Найден URL для OAuth: {url}")
                        self.output_queue.put({'type': 'oauth_url', 'url': url})
                    else:
                        full_response.append(line_stripped)

                process.stdout.close()

            # Дожидаемся завершения процесса и получаем код возврата
            return_code = process.wait()
            logger.info(f"Процесс gemini завершился с кодом {return_code}")

            if return_code == 0:
                final_text = "\n".join(full_response).strip()
                logger.info(f"Успешный ответ от CLI: {final_text[:200]}...")
                self.output_queue.put({'type': 'response', 'data': final_text})
            else:
                stderr_output = process.stderr.read() if process.stderr else ""
                logger.error(f"Ошибка выполнения Gemini CLI (stderr): {stderr_output}")
                self.output_queue.put({'type': 'error', 'message': f"Ошибка CLI: {stderr_output}"})

        except FileNotFoundError:
            error_msg = "Команда 'gemini' не найдена."
            logger.error(error_msg)
            self.output_queue.put({'type': 'error', 'message': error_msg})
        except Exception as e:
            error_msg = f"Неожиданная ошибка в потоке Gemini: {str(e)}"
            logger.exception(error_msg)
            self.output_queue.put({'type': 'error', 'message': error_msg})
        finally:
            # Сигнал о завершении работы
            self.output_queue.put({'type': 'done'})


    def _start_threaded_run(self, command: list):
        """
        Создает и запускает поток для выполнения команды.
        """
        thread = threading.Thread(target=self._run_in_thread, args=(command,))
        thread.daemon = True
        thread.start()
        logger.info("Фоновый поток для Gemini CLI запущен.")

    def generate_text(self, prompt: str, model: str = "gemini-pro", **kwargs):
        """
        Асинхронная генерация текста.
        """
        command = ["gemini", "-p", prompt, "-m", model]
        self._start_threaded_run(command)

    def chat(self, messages: list, model: str = "gemini-pro", **kwargs):
        """
        Асинхронный чат.
        """
        # Для CLI чат - это просто большой промпт
        full_prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            full_prompt += f"{role.capitalize()}: {content}\n\n"
        full_prompt += "Assistant:"

        command = ["gemini", "-p", full_prompt, "-m", model]
        self._start_threaded_run(command)

    def get_models(self) -> dict:
        """
        Возвращает жестко закодированный список моделей.
        Это синхронная операция, так как не требует вызова CLI.
        """
        models = [
            {"name": "models/gemini-pro", "display_name": "Gemini Pro", "description": "The best model for scaling across a wide range of tasks."},
            {"name": "models/gemini-1.5-pro", "display_name": "Gemini 1.5 Pro", "description": "The most capable model for a variety of tasks."},
            {"name": "models/gemini-1.5-flash", "display_name": "Gemini 1.5 Flash", "description": "A lighter-weight, faster model for more agile tasks."},
        ]
        return {"status": "success", "data": models}

    def get_model_info(self, model_id: str) -> dict:
        """
        Возвращает базовую информацию о модели.
        """
        models_data = self.get_models().get("data", [])
        for model in models_data:
            if model["name"] == model_id or model["name"].split('/')[-1] == model_id:
                return {"status": "success", "data": model}

        return {"status": "error", "message": f"Модель {model_id} не найдена"}
