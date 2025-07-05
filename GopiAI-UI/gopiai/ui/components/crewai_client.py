import urllib.parse

"""
🔌 CrewAI API Client
Клиент для интеграции с CrewAI через REST API
"""

import requests
import requests.exceptions
import threading
import time
import json
import os


# DEBUG LOGGING PATCH - Added for hang diagnosis
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
print("🔧 DEBUG logging enabled for crewai_client.py")


# --- NLP (spaCy) ---
try:
    import spacy
    # Загружаем обе модели (русскую и английскую)
    nlp_ru = spacy.load("ru_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy и языковые модели успешно загружены")
except Exception as e:
    logger.warning(f"⚠️ Не удалось загрузить spaCy или языковые модели: {e}")
    nlp_ru = None
    nlp_en = None

class CrewAIClient:
    """
    Клиент для взаимодействия с CrewAI API сервером

    Позволяет UI приложению использовать функциональность CrewAI,
    запущенного в отдельном окружении через REST API.
    """

    def __init__(self, base_url="http://127.0.0.1:5050"):
        self.base_url = base_url
        self.timeout = 30  # Таймаут для API запросов (в секундах)
        self._server_available = None  # Кеш статуса сервера
        self._last_check = 0  # Время последней проверки

    def brave_search_site(self, query):
        """
        Ищет сайт по запросу через Brave Search API и возвращает первый найденный url.
        """
        api_key = os.environ.get("BRAVE_API_KEY")
        if not api_key:
            logger.warning("BRAVE_API_KEY не найден в окружении!")
            return None
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 3}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Ищем первый внешний сайт (не brave.com)
                for item in data.get("web", {}).get("results", []):
                    link = item.get("url")
                    if link and not link.startswith("https://search.brave.com"):
                        return link
            else:
                logger.warning(f"Brave API error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Ошибка Brave Search: {e}")
        return None

    def is_available(self, force_check=False):
        """Проверяет доступность CrewAI API сервера"""
        # Используем кеш, если проверка была недавно
        current_time = time.time()
        if not force_check and self._server_available is not None and (current_time - self._last_check) < 30:
            return self._server_available

        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
            self._server_available = response.status_code == 200
            self._last_check = current_time
            return self._server_available
        except requests.RequestException:
            self._server_available = False
            self._last_check = current_time
            return False
    
    def process_request(self, message, force_crewai=False, timeout=None):
        """
        Обрабатывает запрос через CrewAI API
        Теперь с поддержкой NLP-парсинга (spaCy) и разбором составных команд
        """
        if not self.is_available():
            return {
                "response": f"CrewAI API сервер недоступен. Запустите его с помощью 'run_crewai_api_server.bat'.\n\nВаш запрос: {message}",
                "error": "server_unavailable",
                "processed_with_crewai": False
            }
        try:
            nlp_result = self.nlp_parse_command(message)
            logger.info(f"[NLP] Результат парсинга: {nlp_result}")
            # --- Разделение на подкоманды (простое, по запятым и союзам) ---
            import re
            subcommands = re.split(r'[,.!?;\n]|\bи\b|\bзатем\b|\bthen\b', message, flags=re.IGNORECASE)
            subcommands = [cmd.strip() for cmd in subcommands if cmd.strip()]
            logger.info(f"[NLP] Найдено подкоманд: {len(subcommands)} -> {subcommands}")
            results = []
            context = {}
            for idx, subcmd in enumerate(subcommands):
                logger.info(f"[NLP] Обработка подкоманды {idx+1}: {subcmd}")
                # 1. Поиск сайта (если есть слова 'найди сайт', 'find site', 'найди сервис', 'find service')
                if re.search(r'найди сайт|find site|найди сервис|find service|найди страницу|find page', subcmd, re.IGNORECASE):
                    found_url = self.brave_search_site(subcmd)
                    if found_url:
                        context['site_url'] = found_url
                        results.append({
                            "step": "site_search",
                            "query": subcmd,
                            "url": found_url,
                            "success": True
                        })
                    else:
                        results.append({
                            "step": "site_search",
                            "query": subcmd,
                            "url": None,
                            "success": False,
                            "error": "Не удалось найти сайт через Brave Search"
                        })
                    continue
                # 2. Переход на сайт (если есть 'зайди', 'перейди', 'открой', 'go to', 'open')
                if re.search(r'зайди|перейди|открой|go to|open', subcmd, re.IGNORECASE):
                    url = context.get('site_url')
                    if not url:
                        # Пробуем найти url в тексте
                        url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', subcmd)
                        url = url_match.group(0) if url_match else None
                    if url:
                        results.append({
                            "step": "go_to_url",
                            "url": url,
                            "success": True
                        })
                        context['current_url'] = url
                        continue
                    else:
                        results.append({"step": "go_to_url", "error": "URL не найден", "success": False})
                        continue
                # 3. Генерация/действие на сайте (если есть 'сгенерируй', 'generate', 'создай', 'create', 'draw', 'нарисуй')
                if re.search(r'сгенерируй|создай|generate|create|draw|нарисуй', subcmd, re.IGNORECASE):
                    url = context.get('current_url') or context.get('site_url')
                    results.append({
                        "step": "generate",
                        "action": subcmd,
                        "on_url": url,
                        "success": bool(url)
                    })
                    continue
                # 4. Fallback: обычная обработка browseruse/старый парсер
                # ...existing code for browseruse and fallback...
                # (оставляем как есть, если не составная команда)
            if results:
                # Формируем человечный ответ
                if len(results) == 1:
                    step = results[0]
                    if step["step"] == "site_search" and step.get("success") and step.get("url"):
                        resp = f"Нашёл сайт: {step['url']} — открываю!"
                    elif step["step"] == "go_to_url" and step.get("success") and step.get("url"):
                        resp = f"Переход на сайт: {step['url']}"
                    elif step["step"] == "generate" and step.get("success"):
                        resp = f"Генерирую: {step['action']} на {step.get('on_url','[неизвестно где]')}"
                    else:
                        resp = step.get("error") or "Не удалось выполнить действие."
                else:
                    # Кратко опишем каждый шаг
                    desc = []
                    for step in results:
                        if step["step"] == "site_search" and step.get("success") and step.get("url"):
                            desc.append(f"Нашёл сайт: {step['url']}")
                        elif step["step"] == "go_to_url" and step.get("success") and step.get("url"):
                            desc.append(f"Перехожу: {step['url']}")
                        elif step["step"] == "generate" and step.get("success"):
                            desc.append(f"Генерирую: {step['action']} на {step.get('on_url','[неизвестно где]')}")
                        elif step.get("error"):
                            desc.append(f"Ошибка: {step['error']}")
                    resp = " → ".join(desc) if desc else "Выполнено несколько действий."
                return {
                    "response": resp,
                    "steps": results,
                    "nlp": nlp_result,
                    "processed_with_crewai": False
                }
            # Если не составная — старый парсер (browseruse и т.д.)
            # ...existing code for browseruse/fallback (оставить как есть)...
            # (скопировать из предыдущей версии process_request)
            # ---
            # Расширенный список браузерных команд с популярными сайтами
            browser_commands = [
                "открой сайт", "открой страницу", "перейди на сайт", "зайди на сайт",
                "загрузи сайт", "иди на сайт", "переходи на", "открыть сайт",
                "открой github", "открой гитхаб", "открой google", "открой гугл",
                "открой youtube", "открой ютуб", "открой stackoverflow",
                "открой вконтакте", "открой вк", "открой telegram", "открой телеграм",
                "github.com", "google.com", "youtube.com", "stackoverflow.com",
                "vk.com", "telegram.org", "habr.com", "yandex.ru",
                "найди в google", "поиск в google", "google поиск",
                "найди в гугле", "поищи в google", "погугли"
            ]
            message_lower = message.lower()
            logger.info(f"🔍 [CREWAI] Анализ сообщения на браузерные команды: '{message}'")
            logger.info(f"🔍 [CREWAI] Сообщение в нижнем регистре: '{message_lower}'")
            is_browser_command = False
            matched_command = None
            for cmd in browser_commands:
                if cmd in message_lower:
                    is_browser_command = True
                    matched_command = cmd
                    logger.info(f"🔍 [CREWAI] ✅ Найдена команда браузера: '{cmd}'")
                    break
            if not is_browser_command:
                logger.info(f"🔍 [CREWAI] Команды браузера в тексте не найдены")
            url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
            url_match = re.search(url_pattern, message)
            if url_match:
                is_browser_command = True
                matched_url = url_match.group(0)
                logger.info(f"🔍 [CREWAI] ✅ Найден URL в сообщении: '{matched_url}'")
            else:
                logger.info(f"🔍 [CREWAI] URL в сообщении не найден")
            browseruse_command_map = {
                "открой": "go_to_url",
                "открыть": "go_to_url",
                "перейди": "go_to_url",
                "иди": "go_to_url",
                "назад": "go_back",
                "вкладка": "switch_tab",
                "закрой вкладку": "close_tab",
                "кликни": "click_element_by_index",
                "нажми": "click_element_by_index",
                "введи": "input_text",
                "напиши": "input_text",
                "загрузи файл": "upload_file",
                "прокрути": "scroll",
                "скролл": "scroll",
                "найди": "extract_structured_data",
                "поиск": "extract_structured_data",
                "выбери опцию": "select_dropdown_option",
                "опции": "get_dropdown_options",
                "подожди": "wait",
                "ждать": "wait",
                "скриншот": "screenshot",
                "отчёт": "extract_structured_data",
                "отправь клавиши": "send_keys",
                "сохрани": "write_file",
                "добавь в файл": "append_file",
                "прочитай файл": "read_file",
                "google sheets": "read_sheet_contents",
                "выдели ячейку": "select_cell_or_range",
                "очисти ячейку": "clear_cell_contents",
                "обнови ячейку": "update_cell_contents",
                "выбери текст": "scroll_to_text",
                "open": "go_to_url",
                "go": "go_to_url",
                "back": "go_back",
                "tab": "switch_tab",
                "close tab": "close_tab",
                "click": "click_element_by_index",
                "type": "input_text",
                "upload": "upload_file",
                "scroll": "scroll",
                "search": "extract_structured_data",
                "select option": "select_dropdown_option",
                "options": "get_dropdown_options",
                "wait": "wait",
                "screenshot": "screenshot",
                "report": "extract_structured_data",
                "send keys": "send_keys",
                "save": "write_file",
                "append": "append_file",
                "read file": "read_file",
                "sheet": "read_sheet_contents",
                "select cell": "select_cell_or_range",
                "clear cell": "clear_cell_contents",
                "update cell": "update_cell_contents",
                "scroll to text": "scroll_to_text",
            }
            found_browseruse = None
            for ru, cmd in browseruse_command_map.items():
                if ru in message_lower:
                    found_browseruse = cmd
                    break
            if found_browseruse:
                logger.info(f"🌐 [BROWSERUSE] Автоматически сопоставлено с browseruse-командой: {found_browseruse}")
                return {
                    "impl": "browser-use",
                    "command": f"{found_browseruse} | {message}",
                    "nlp": nlp_result,
                    "processed_with_crewai": False
                }
            logger.info(f"🔍 [CREWAI] Итоговый результат анализа: is_browser_command={is_browser_command}")
            if is_browser_command:
                logger.info(f"🌐 [CREWAI] Возвращаем браузерную команду для обработки")
                user_command = message
                if "User:" in message:
                    user_command = message.split("User:")[-1].strip()
                    if "Предыдущие сообщения:" in user_command:
                        user_command = user_command.split("Предыдущие сообщения:")[0].strip()
                    logger.info(f"🌐 [CREWAI] Извлечена пользовательская команда: '{user_command}'")
                result = {
                    "impl": "browser-use",
                    "command": user_command,
                    "nlp": nlp_result,
                    "processed_with_crewai": False
                }
                logger.info(f"🌐 [CREWAI] Результат браузерной команды: {result}")
                return result
            logger.warning(f"🤖 Не удалось распознать команду или выполнить действие: '{message}'")
            return {
                "response": "Извини, я не смог понять, что ты хочешь сделать в браузере. Можешь переформулировать или уточнить команду? Если нужна помощь — просто напиши, что ты хочешь увидеть или получить!",
                "error": "unrecognized_browser_command",
                "nlp": nlp_result,
                "processed_with_crewai": False
            }
        except Exception as e:
            logger.error(f"Ошибка в process_request: {e}")
            return {
                "response": f"Произошла ошибка при обработке запроса: {e}",
                "error": "internal_error",
                "processed_with_crewai": False
            }
            
    def index_documentation(self):
        """Запускает индексацию документации CrewAI"""
        if not self.is_available():
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/api/index_docs",
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {"error_message": str(e), "processed_with_crewai": False}

    def nlp_parse_command(self, message, lang_hint=None):
        """
        Пример базового NLP-парсинга команды с помощью spaCy.
        Возвращает список сущностей и ключевых слов.
        lang_hint: 'ru' или 'en' — если явно известно, иначе autodetect.
        """
        if nlp_ru is None or nlp_en is None:
            logger.warning("spaCy не инициализирован — NLP-парсинг недоступен")
            return None
        # Определяем язык (очень просто)
        lang = lang_hint
        if not lang:
            if any(ord(c) > 127 for c in message):
                lang = 'ru'
            else:
                lang = 'en'
        nlp = nlp_ru if lang == 'ru' else nlp_en
        doc = nlp(message)
        # Извлекаем сущности и ключевые слова
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        logger.info(f"[NLP] entities: {entities}, tokens: {tokens}")
        return {"entities": entities, "tokens": tokens, "lang": lang}

# Глобальный экземпляр клиента
crewai_client = CrewAIClient()