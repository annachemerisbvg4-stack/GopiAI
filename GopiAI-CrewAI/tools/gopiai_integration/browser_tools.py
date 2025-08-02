"""
🌐 GopiAI Browser Tool для CrewAI
Интеграция CrewAI агентов с браузер-системой GopiAI
"""

import os
import sys
import time
import logging
from typing import Type, Any, Optional, Dict, List
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
import base64
from pathlib import Path

# Попытка импорта Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Попытка импорта Playwright
try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Импортируем базовый класс
from .base import GopiAIBaseTool
# Импортируем BaseTool из crewai
from crewai.tools.base_tool import BaseTool

class BrowserInput(BaseModel):
    """Расширенная схема входных данных для браузер-инструмента"""
    action: str = Field(description="Действие: navigate, click, type, extract, screenshot, wait, scroll, select, execute_js, get_cookies, set_cookie")
    target: str = Field(description="URL, CSS селектор, XPath или другой идентификатор")
    data: str = Field(default="", description="Данные для ввода, JavaScript код, текст или значение")
    wait_seconds: int = Field(default=3, description="Время ожидания после действия")
    browser_type: str = Field(default="auto", description="Тип браузера: auto, selenium, playwright, requests")
    headless: bool = Field(default=True, description="Запуск в headless режиме")

class GopiAIBrowserTool(BaseTool):
    """
    Мощный инструмент для управления браузером с поддержкой Selenium, Playwright и requests
    
    Возможности:
    - Навигация по веб-сайтам
    - Клики по элементам и ввод текста
    - Извлечение данных и скриншоты
    - Выполнение JavaScript
    - Работа с cookies
    - Прокрутка и выбор элементов
    - Автоматический выбор лучшего браузерного движка
    """
    
    name: str = Field(default="gopiai_browser_advanced", description="Расширенный браузерный инструмент")
    description: str = Field(default="""Мощный браузерный инструмент с поддержкой Selenium, Playwright и requests.
    Поддерживает: навигацию, клики, ввод текста, скриншоты, JavaScript, cookies, прокрутку.
    Автоматически выбирает лучший доступный браузерный движок.""", description="Описание инструмента")
    args_schema: Type[BaseModel] = BrowserInput
    
    def __init__(self):
        """Инициализация браузерного инструмента"""
        super().__init__()
        
        # Состояние браузера
        self._driver = None
        self._page = None
        self._browser_type = None
        self._last_html = None
        
        # Логгер для отладки (используем модульный логгер)
        # Не добавляем как атрибут экземпляра из-за Pydantic
        pass
    
    @property
    def logger(self):
        """Получение логгера для инструмента"""
        return logging.getLogger(__name__)
    
    def _run(self, action: str, target: str, data: str = "", wait_seconds: int = 3, 
             browser_type: str = "auto", headless: bool = True) -> str:
        """
        Выполнение браузерного действия с автоматическим выбором движка
        """
        try:
            # Определяем лучший доступный браузерный движок
            if browser_type == "auto":
                if PLAYWRIGHT_AVAILABLE:
                    browser_type = "playwright"
                elif SELENIUM_AVAILABLE:
                    browser_type = "selenium"
                else:
                    browser_type = "requests"
            
            # Выполняем действие в зависимости от выбранного движка
            if browser_type == "playwright" and PLAYWRIGHT_AVAILABLE:
                return self._run_playwright(action, target, data, wait_seconds, headless)
            elif browser_type == "selenium" and SELENIUM_AVAILABLE:
                return self._run_selenium(action, target, data, wait_seconds, headless)
            else:
                return self._run_requests(action, target, data, wait_seconds)
                
        except Exception as e:
            self.logger.error(f"Ошибка браузерного действия: {e}")
            return f"❌ Ошибка браузерного действия: {str(e)}"
    
    def _run_playwright(self, action: str, target: str, data: str, wait_seconds: int, headless: bool) -> str:
        """Выполнение действий через Playwright"""
        try:
            # Инициализируем Playwright если нужно
            if not self._playwright_browser:
                self._init_playwright(headless)
            
            page = self._playwright_page
            
            if action == "open" or action == "navigate":
                # Если target не указан, открываем Google
                if not target or target == "":
                    target = "https://www.google.com"
                # Если target не содержит протокол, добавляем https://
                elif not target.startswith(('http://', 'https://')):
                    target = f"https://{target}"
                
                page.goto(target, wait_until="networkidle")
                self._last_url = target
                return f"✅ Браузер открыт на {target} (Playwright)"
            
            elif action == "click":
                page.click(target)
                page.wait_for_timeout(wait_seconds * 1000)
                return f"✅ Клик по элементу '{target}' выполнен (Playwright)"
            
            elif action == "type":
                page.fill(target, data)
                page.wait_for_timeout(wait_seconds * 1000)
                return f"✅ Ввод '{data}' в элемент '{target}' выполнен (Playwright)"
            
            elif action == "extract":
                if target.lower() == "page":
                    text = page.inner_text("body")
                    return f"✅ Извлечен текст страницы ({len(text)} символов):\n{text[:2000]}..."
                else:
                    elements = page.query_selector_all(target)
                    if not elements:
                        return f"❌ Элементы '{target}' не найдены"
                    texts = [elem.inner_text() for elem in elements[:10]]
                    return f"✅ Извлечено {len(texts)} элементов:\n" + "\n".join(texts)
            
            elif action == "screenshot":
                screenshot_path = Path(target) if target else Path("screenshot.png")
                page.screenshot(path=str(screenshot_path))
                return f"✅ Скриншот сохранен: {screenshot_path} (Playwright)"
            
            elif action == "scroll":
                if target.lower() == "down":
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                elif target.lower() == "up":
                    page.evaluate("window.scrollBy(0, -window.innerHeight)")
                elif target.lower() == "top":
                    page.evaluate("window.scrollTo(0, 0)")
                elif target.lower() == "bottom":
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                else:
                    page.locator(target).scroll_into_view_if_needed()
                return f"✅ Прокрутка выполнена: {target} (Playwright)"
            
            elif action == "execute_js":
                result = page.evaluate(data)
                return f"✅ JavaScript выполнен. Результат: {result} (Playwright)"
            
            elif action == "get_cookies":
                cookies = page.context.cookies()
                return f"✅ Получено {len(cookies)} cookies: {cookies} (Playwright)"
            
            elif action == "wait":
                page.wait_for_timeout(wait_seconds * 1000)
                return f"✅ Ожидание {wait_seconds} секунд выполнено (Playwright)"
            
            else:
                return f"❌ Неизвестное действие для Playwright: {action}"
                
        except Exception as e:
            return f"❌ Ошибка Playwright: {str(e)}"
    
    def _run_selenium(self, action: str, target: str, data: str, wait_seconds: int, headless: bool) -> str:
        """Выполнение действий через Selenium"""
        try:
            # Инициализируем Selenium если нужно
            if not self._selenium_driver:
                self._init_selenium(headless)
            
            driver = self._selenium_driver
            wait = WebDriverWait(driver, 10)
            
            if action == "open" or action == "navigate":
                # Если target не указан, открываем Google
                if not target or target == "":
                    target = "https://www.google.com"
                # Если target не содержит протокол, добавляем https://
                elif not target.startswith(('http://', 'https://')):
                    target = f"https://{target}"
                
                driver.get(target)
                self._last_url = target
                return f"✅ Браузер открыт на {target} (Selenium)"
            
            elif action == "click":
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, target)))
                element.click()
                time.sleep(wait_seconds)
                return f"✅ Клик по элементу '{target}' выполнен (Selenium)"
            
            elif action == "type":
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target)))
                element.clear()
                element.send_keys(data)
                time.sleep(wait_seconds)
                return f"✅ Ввод '{data}' в элемент '{target}' выполнен (Selenium)"
            
            elif action == "extract":
                if target.lower() == "page":
                    text = driver.find_element(By.TAG_NAME, "body").text
                    return f"✅ Извлечен текст страницы ({len(text)} символов):\n{text[:2000]}..."
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, target)
                    if not elements:
                        return f"❌ Элементы '{target}' не найдены"
                    texts = [elem.text for elem in elements[:10]]
                    return f"✅ Извлечено {len(texts)} элементов:\n" + "\n".join(texts)
            
            elif action == "screenshot":
                screenshot_path = target if target else "screenshot.png"
                driver.save_screenshot(screenshot_path)
                return f"✅ Скриншот сохранен: {screenshot_path} (Selenium)"
            
            elif action == "scroll":
                if target.lower() == "down":
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                elif target.lower() == "up":
                    driver.execute_script("window.scrollBy(0, -window.innerHeight);")
                elif target.lower() == "top":
                    driver.execute_script("window.scrollTo(0, 0);")
                elif target.lower() == "bottom":
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                else:
                    element = driver.find_element(By.CSS_SELECTOR, target)
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                return f"✅ Прокрутка выполнена: {target} (Selenium)"
            
            elif action == "execute_js":
                result = driver.execute_script(data)
                return f"✅ JavaScript выполнен. Результат: {result} (Selenium)"
            
            elif action == "get_cookies":
                cookies = driver.get_cookies()
                return f"✅ Получено {len(cookies)} cookies: {cookies} (Selenium)"
            
            elif action == "wait":
                time.sleep(wait_seconds)
                return f"✅ Ожидание {wait_seconds} секунд выполнено (Selenium)"
            
            else:
                return f"❌ Неизвестное действие для Selenium: {action}"
                
        except TimeoutException:
            return f"❌ Таймаут при поиске элемента '{target}' (Selenium)"
        except NoSuchElementException:
            return f"❌ Элемент '{target}' не найден (Selenium)"
        except Exception as e:
            return f"❌ Ошибка Selenium: {str(e)}"
    
    def _run_requests(self, action: str, target: str, data: str, wait_seconds: int) -> str:
        """Выполнение действий через requests (ограниченная функциональность)"""
        try:
            if action == "open" or action == "navigate":
                # Если target не указан, открываем Google
                if not target or target == "":
                    target = "https://www.google.com"
                # Если target не содержит протокол, добавляем https://
                elif not target.startswith(('http://', 'https://')):
                    target = f"https://{target}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                resp = requests.get(target, headers=headers, timeout=10)
                self._last_html = resp.text
                self._last_url = target
                return f"✅ Браузер открыт на {target} (код {resp.status_code}) (requests)"
            
            elif action == "extract":
                if not self._last_html:
                    return "❌ Нет загруженной страницы. Сначала используйте 'navigate'."
                soup = BeautifulSoup(self._last_html, 'html.parser')
                if target.lower() == "page":
                    text = soup.get_text(separator='\n')
                    return f"✅ Извлечен текст страницы ({len(text)} символов):\n{text[:2000]}..."
                else:
                    elements = soup.select(target)
                    if not elements:
                        return f"❌ Элементы '{target}' не найдены"
                    texts = [el.get_text(strip=True) for el in elements[:10]]
                    return f"✅ Извлечено {len(texts)} элементов:\n" + "\n".join(texts)
            
            elif action == "wait":
                time.sleep(wait_seconds)
                return f"✅ Ожидание {wait_seconds} секунд выполнено (requests)"
            
            else:
                return f"⚠️ Действие '{action}' не поддерживается в режиме requests. Установите Selenium или Playwright для полной функциональности."
                
        except Exception as e:
            return f"❌ Ошибка requests: {str(e)}"
    
    def _init_playwright(self, headless: bool = True):
        """Инициализация Playwright"""
        try:
            self._playwright_context = sync_playwright().start()
            self._playwright_browser = self._playwright_context.chromium.launch(headless=headless)
            self._playwright_page = self._playwright_browser.new_page()
            self.logger.info("Playwright инициализирован успешно")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Playwright: {e}")
            raise
    
    def _init_selenium(self, headless: bool = True):
        """Инициализация Selenium"""
        try:
            options = ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self._selenium_driver = webdriver.Chrome(options=options)
            self.logger.info("Selenium инициализирован успешно")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Selenium: {e}")
            # Попробуем Firefox как fallback
            try:
                firefox_options = FirefoxOptions()
                if headless:
                    firefox_options.add_argument('--headless')
                self._selenium_driver = webdriver.Firefox(options=firefox_options)
                self.logger.info("Selenium (Firefox) инициализирован успешно")
            except Exception as e2:
                self.logger.error(f"Ошибка инициализации Firefox: {e2}")
                raise Exception(f"Не удалось инициализировать ни Chrome, ни Firefox: {e}, {e2}")
    
    def cleanup(self):
        """Очистка ресурсов браузера"""
        try:
            if self._selenium_driver:
                self._selenium_driver.quit()
                self._selenium_driver = None
            
            if self._playwright_browser:
                self._playwright_browser.close()
                self._playwright_browser = None
            
            if self._playwright_context:
                self._playwright_context.stop()
                self._playwright_context = None
                
            self.logger.info("Ресурсы браузера очищены")
        except Exception as e:
            self.logger.error(f"Ошибка при очистке ресурсов: {e}")
    
    def __del__(self):
        """Деструктор для автоматической очистки"""
        self.cleanup()
    
    def _execute_browser_action(self, action: str, target: str, data: str, wait_seconds: int) -> str:
        return "[DEPRECATED] Используйте _run с requests/BeautifulSoup."
    
    def _simulate_browser_action(self, action: str, target: str, data: str) -> str:
        """
        Эмуляция браузерных действий для тестирования
        """
        if action == "navigate":
            return f"🌐 Переход на {target}"
        elif action == "click":
            return f"👆 Клик по элементу {target}"
        elif action == "type":
            return f"⌨️ Ввод '{data}' в {target}"
        elif action == "extract":
            if target.lower() == "page":
                return "📄 Текст всей страницы извлечен"
            else:
                return f"📝 Текст из {target}: [извлеченный текст]"
        elif action == "screenshot":
            return f"📸 Скриншот сохранен как {target}"
        elif action == "wait":
            return f"⏱️ Ожидание элемента {target}"
        else:
            return f"❌ Неизвестное действие: {action}"


# Дополнительные специализированные инструменты

class GopiAIWebSearchTool(BaseTool):
    """Улучшенный инструмент для веб-поиска с поддержкой многих поисковых систем"""
    
    name: str = Field(default="gopiai_web_search_advanced", description="Улучшенный веб-поиск")
    description: str = Field(default="Выполняет поиск в Google, Bing, DuckDuckGo и возвращает структурированные результаты", description="Описание инструмента")
    args_schema: Type[BaseModel] = BrowserInput
    
    def _run(self, action: str = "search", target: str = "google", data: str = "", **kwargs) -> str:
        """
        Улучшенный поиск с поддержкой разных поисковых систем
        action: search, quick_search
        target: google, bing, duckduckgo, yandex
        data: поисковый запрос
        """
        try:
            if not data:
                return "❌ Поисковый запрос не указан"
            
            browser_tool = GopiAIBrowserTool()
            
            # Определяем URL поисковой системы
            search_urls = {
                "google": "https://www.google.com",
                "bing": "https://www.bing.com",
                "duckduckgo": "https://duckduckgo.com",
                "yandex": "https://yandex.ru"
            }
            
            search_inputs = {
                "google": "input[name='q']",
                "bing": "input[name='q']",
                "duckduckgo": "input[name='q']",
                "yandex": "input[name='text']"
            }
            
            search_buttons = {
                "google": "input[name='btnK']",
                "bing": "input[type='submit']",
                "duckduckgo": "input[type='submit']",
                "yandex": "button[type='submit']"
            }
            
            result_selectors = {
                "google": ".g h3, .g .VwiC3b",
                "bing": ".b_algo h2, .b_algo .b_caption p",
                "duckduckgo": ".result__title, .result__snippet",
                "yandex": ".serp-item .organic__title, .serp-item .organic__text"
            }
            
            if target not in search_urls:
                target = "google"  # По умолчанию
            
            if action == "quick_search":
                # Быстрый поиск через requests
                search_url = f"{search_urls[target]}/search?q={data.replace(' ', '+')}"
                result = browser_tool._run("navigate", search_url, browser_type="requests")
                extract_result = browser_tool._run("extract", result_selectors[target], browser_type="requests")
                return f"🔍 Быстрый поиск '{data}' в {target}:\n{extract_result}"
            
            else:
                # Полный поиск через браузер
                # Переходим на поисковую систему
                nav_result = browser_tool._run("navigate", search_urls[target])
                
                # Вводим поисковый запрос
                type_result = browser_tool._run("type", search_inputs[target], data)
                
                # Отправляем запрос
                if target == "google":
                    # Для Google используем Enter
                    browser_tool._run("execute_js", "", "document.querySelector('input[name=\"q\"]').form.submit()")
                else:
                    browser_tool._run("click", search_buttons[target])
                
                # Ожидаем загрузку результатов
                browser_tool._run("wait", "", "", 3)
                
                # Извлекаем результаты
                results = browser_tool._run("extract", result_selectors[target])
                
                # Очищаем ресурсы
                browser_tool.cleanup()
                
                return f"🔍 Результаты поиска '{data}' в {target}:\n{results}"
                
        except Exception as e:
            return f"❌ Ошибка поиска: {str(e)}"


class GopiAIPageAnalyzerTool(BaseTool):
    """Мощный анализатор веб-страниц с расширенными возможностями"""
    
    name: str = Field(default="gopiai_page_analyzer_advanced", description="Расширенный анализатор страниц")
    description: str = Field(default="Анализирует содержимое веб-страницы: ссылки, формы, изображения, метаданные, SEO, производительность", description="Описание инструмента")
    args_schema: Type[BaseModel] = BrowserInput
    
    def _run(self, action: str = "summary", target: str = "", data: str = "", **kwargs) -> str:
        """
        Расширенный анализ страницы
        action: summary, links, forms, images, metadata, seo, performance, accessibility, security
        target: URL для анализа
        data: дополнительные параметры
        """
        try:
            if not target:
                return "❌ URL для анализа не указан"
            
            browser_tool = GopiAIBrowserTool()
            
            # Переходим на страницу
            nav_result = browser_tool._run("navigate", target)
            
            if action == "summary":
                # Общий анализ страницы
                title = browser_tool._run("extract", "title")
                headers = browser_tool._run("extract", "h1, h2, h3")
                meta_desc = browser_tool._run("extract", "meta[name='description']")
                links_count = browser_tool._run("execute_js", "", "return document.querySelectorAll('a').length")
                images_count = browser_tool._run("execute_js", "", "return document.querySelectorAll('img').length")
                
                browser_tool.cleanup()
                return f"""📊 Общий анализ {target}:
• Заголовок: {title}
• Описание: {meta_desc}
• Основные заголовки: {headers}
• Количество ссылок: {links_count}
• Количество изображений: {images_count}"""
            
            elif action == "links":
                # Анализ ссылок
                internal_links = browser_tool._run("execute_js", "", f"return Array.from(document.querySelectorAll('a[href]')).filter(a => a.href.includes('{target.split('/')[2]}')).map(a => a.href + ' - ' + a.textContent.trim()).slice(0, 10)")
                external_links = browser_tool._run("execute_js", "", f"return Array.from(document.querySelectorAll('a[href]')).filter(a => !a.href.includes('{target.split('/')[2]}') && a.href.startsWith('http')).map(a => a.href + ' - ' + a.textContent.trim()).slice(0, 10)")
                
                browser_tool.cleanup()
                return f"""🔗 Анализ ссылок {target}:

🏠 Внутренние ссылки:
{internal_links}

🌐 Внешние ссылки:
{external_links}"""
            
            elif action == "forms":
                # Анализ форм
                forms_info = browser_tool._run("execute_js", "", "return Array.from(document.querySelectorAll('form')).map(form => ({ action: form.action, method: form.method, inputs: Array.from(form.querySelectorAll('input')).map(input => input.type + ':' + input.name) }))")
                
                browser_tool.cleanup()
                return f"📋 Анализ форм {target}:\n{forms_info}"
            
            elif action == "images":
                # Анализ изображений
                images_info = browser_tool._run("execute_js", "", "return Array.from(document.querySelectorAll('img')).map(img => ({ src: img.src, alt: img.alt, width: img.width, height: img.height })).slice(0, 20)")
                
                browser_tool.cleanup()
                return f"🖼️ Анализ изображений {target}:\n{images_info}"
            
            elif action == "metadata":
                # Анализ метаданных
                meta_tags = browser_tool._run("execute_js", "", "return Array.from(document.querySelectorAll('meta')).map(meta => meta.name + ':' + meta.content || meta.property + ':' + meta.content).filter(Boolean)")
                
                browser_tool.cleanup()
                return f"🏷️ Метаданные {target}:\n{meta_tags}"
            
            elif action == "seo":
                # SEO анализ
                title = browser_tool._run("extract", "title")
                h1_count = browser_tool._run("execute_js", "", "return document.querySelectorAll('h1').length")
                meta_desc = browser_tool._run("extract", "meta[name='description']")
                alt_missing = browser_tool._run("execute_js", "", "return document.querySelectorAll('img:not([alt])').length")
                
                browser_tool.cleanup()
                return f"""📊 SEO анализ {target}:
• Заголовок: {title} (длина: {len(str(title))} символов)
• Количество H1: {h1_count}
• Meta description: {meta_desc}
• Изображений без alt: {alt_missing}"""
            
            elif action == "performance":
                # Анализ производительности
                load_time = browser_tool._run("execute_js", "", "return performance.timing.loadEventEnd - performance.timing.navigationStart")
                resources_count = browser_tool._run("execute_js", "", "return performance.getEntriesByType('resource').length")
                dom_elements = browser_tool._run("execute_js", "", "return document.querySelectorAll('*').length")
                
                browser_tool.cleanup()
                return f"""⚡ Анализ производительности {target}:
• Время загрузки: {load_time} мс
• Количество ресурсов: {resources_count}
• DOM элементов: {dom_elements}"""
            
            elif action == "accessibility":
                # Анализ доступности
                missing_alt = browser_tool._run("execute_js", "", "return document.querySelectorAll('img:not([alt])').length")
                missing_labels = browser_tool._run("execute_js", "", "return document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])').length")
                headings_structure = browser_tool._run("execute_js", "", "return Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => h.tagName).join(', ')")
                
                browser_tool.cleanup()
                return f"""♿ Анализ доступности {target}:
• Изображений без alt: {missing_alt}
• Полей без меток: {missing_labels}
• Структура заголовков: {headings_structure}"""
            
            elif action == "security":
                # Базовый анализ безопасности
                https_check = "HTTPS" if target.startswith("https://") else "HTTP"
                forms_without_csrf = browser_tool._run("execute_js", "", "return document.querySelectorAll('form:not([data-csrf]):not([csrf-token])').length")
                external_scripts = browser_tool._run("execute_js", "", f"return Array.from(document.querySelectorAll('script[src]')).filter(s => !s.src.includes('{target.split('/')[2]}')).length")
                
                browser_tool.cleanup()
                return f"""🔒 Анализ безопасности {target}:
• Протокол: {https_check}
• Форм без CSRF защиты: {forms_without_csrf}
• Внешних скриптов: {external_scripts}"""
            
            elif action == "extract":
                # Полное извлечение текста
                if data:
                    # Извлечение по селектору
                    text = browser_tool._run("extract", data)
                else:
                    # Полный текст страницы
                    text = browser_tool._run("extract", "page")
                
                browser_tool.cleanup()
                return f"📄 Извлеченный текст с {target}:\n{text}"
            
            else:
                browser_tool.cleanup()
                return f"❌ Неизвестный тип анализа: {action}. Доступные: summary, links, forms, images, metadata, seo, performance, accessibility, security, extract"
                
        except Exception as e:
            return f"❌ Ошибка анализа: {str(e)}"


# Экспорт инструментов
__all__ = [
    "GopiAIBrowserTool",
    "GopiAIWebSearchTool", 
    "GopiAIPageAnalyzerTool",
    "BrowserInput",
    "SELENIUM_AVAILABLE",
    "PLAYWRIGHT_AVAILABLE"
]

# Информация о доступности браузерных движков
def get_browser_capabilities() -> Dict[str, bool]:
    """Возвращает информацию о доступных браузерных движках"""
    return {
        "selenium": SELENIUM_AVAILABLE,
        "playwright": PLAYWRIGHT_AVAILABLE,
        "requests": True  # Всегда доступен
    }

def get_recommended_browser_engine() -> str:
    """Возвращает рекомендуемый браузерный движок"""
    if PLAYWRIGHT_AVAILABLE:
        return "playwright"
    elif SELENIUM_AVAILABLE:
        return "selenium"
    else:
        return "requests"

def install_browser_dependencies() -> str:
    """Возвращает инструкции по установке зависимостей браузера"""
    return """
🔧 Для полной функциональности браузерных инструментов установите:

📦 Selenium:
    pip install selenium
    # Также нужен ChromeDriver или GeckoDriver

📦 Playwright (рекомендуется):
    pip install playwright
    playwright install

📦 Базовые зависимости (уже установлены):
    pip install requests beautifulsoup4

⚡ Playwright обеспечивает лучшую производительность и стабильность.
"""

if __name__ == "__main__":
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Тестирование GopiAI Browser Tools...")
    print(f"📊 Доступные движки: {get_browser_capabilities()}")
    print(f"🎯 Рекомендуемый движок: {get_recommended_browser_engine()}")
    
    if not SELENIUM_AVAILABLE and not PLAYWRIGHT_AVAILABLE:
        print("⚠️ Браузерные движки не установлены. Работает только requests.")
        print(install_browser_dependencies())
    
    # Тест основного браузер-инструмента
    try:
        browser = GopiAIBrowserTool()
        result = browser._run("navigate", "https://httpbin.org/get", browser_type="requests")
        print(f"✅ Browser test: {result[:100]}...")
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
    
    # Тест поиска
    try:
        search = GopiAIWebSearchTool()
        result = search._run("quick_search", "google", "test query")
        print(f"✅ Search test: {result[:100]}...")
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    # Тест анализатора
    try:
        analyzer = GopiAIPageAnalyzerTool()
        result = analyzer._run("summary", "https://httpbin.org/get")
        print(f"✅ Analyzer test: {result[:100]}...")
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
    
    print("🎉 Все инструменты готовы к работе!")