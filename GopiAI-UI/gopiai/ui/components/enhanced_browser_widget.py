"""
Улучшенный виджет браузера с поддержкой асинхронной об        # Создаем основной браузерный виджет
        self.browser = QWebEngineView(self)
        self.browser.setMinimumSize(400, 300)  # Увеличили минимальные размеры
        
        # Принудительно устанавливаем стиль для браузера
        self.browser.setStyleSheet("""
            QWebEngineView {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)
        
        # Настройка браузера для предотвращения графических ошибок
        settings = self.browser.settings()
        settings.setAttribute(settings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(settings.WebAttribute.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(settings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(settings.WebAttribute.JavascriptCanOpenWindows, False)
        
        # Принудительно устанавливаем размер браузера
        self.browser.resize(640, 480)
        
        # ВАЖНО: Принудительно показываем браузер
        self.browser.show()
        self.browser.setVisible(True)
        
        # Создаем индикатор загрузки
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: none; background-color: #f0f0f0; } "
            "QProgressBar::chunk { background-color: #4a86e8; }"
        )
        self.progress_bar.hide()
          # Добавляем компоненты в лейаут
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.browser)
        
        logger.debug(f"Browser widget added to layout. Size: {self.browser.size()}")
        
        # Устанавливаем пустую страницу
        self.browser.setUrl(QUrl("about:blank"))
        
        # Подключаем сигналы
        self.browser.loadProgress.connect(self._update_progress)
        self.browser.loadStarted.connect(lambda: self.progress_bar.show())
        self.browser.loadFinished.connect(self._on_load_finished)
        
        # Создаем асинхронные обработчики
        self.page_processor = AsyncPagePreProcessor(max_cache_size=50)
        self.content_optimizer = ContentOptimizer()
        self.action_predictor = ActionPredictor(self.browser, self.page_processor)
        
        # Текущее состояние
        self.current_url = ""
        self.current_title = ""
        
        # Очередь для обработки страницы после загрузки
        self.processing_queue = asyncio.Queue()
        
        # Запускаем обработчик очереди
        self._start_queue_processor()
        
        logger.info("EnhancedBrowserWidget initialized")
    
    def load_url(self, url: str) -> None:
        """
        Загружает указанный URL.
        
        Args:
            url: URL для загрузки
        """
        if not url:
            return
            
        # Нормализуем URL
        if not url.startswith(("http://", "https://", "file://", "about:")):
            url = "https://" + url
              logger.info(f"Loading URL: {url}")
        
        # Принудительно показываем браузер
        self.browser.show()
        self.browser.setVisible(True)
        self.show()
        self.setVisible(True)
        
        # Загружаем URL
        self.browser.load(QUrl(url))
        
        # Принудительно обновляем виджет
        self.browser.update()
        self.update()
    
    def get_current_url(self) -> str:
        """
        Возвращает текущий URL.
        
        Returns:
            str: Текущий URL
        """
        return self.current_url
    
    def get_current_title(self) -> str:
        """
        Возвращает заголовок текущей страницы.
        
        Returns:
            str: Заголовок страницы
        """
        return self.current_title
    
    @Slot(int)
    def _update_progress(self, progress: int) -> None:
        """
        Обновляет индикатор загрузки.
        
        Args:
            progress: Прогресс загрузки (0-100)
        """
        self.progress_bar.setValue(progress)
        
        # Показываем прогресс-бар, если загрузка не завершена
        if progress < 100:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()
    
    @Slot(bool)
    def _on_load_finished(self, success: bool) -> None:
        """
        Обрабатывает завершение загрузки страницы.
        
        Args:
            success: Флаг успешной загрузки
        """
        # Скрываем прогресс-бар
        self.progress_bar.hide()
        
        if not success:
            logger.warning("Page load failed")
            return
            
        # Обновляем текущий URL и заголовок
        self.current_url = self.browser.url().toString()
        self.current_title = self.browser.page().title()
        
        # Эмитируем сигнал о загрузке страницы
        self.page_loaded.emit(self.current_url, self.current_title)
        
        # Добавляем задачу обработки страницы в очередь
        asyncio.run_coroutine_threadsafe(
            self.processing_queue.put({
                "type": "process_page",
                "url": self.current_url
            }),
            asyncio.get_event_loop()
        )
        
        logger.info(f"Page loaded: {self.current_title} ({self.current_url})")
    
    def _start_queue_processor(self) -> None:
        """Запускает обработчик очереди задач."""
        asyncio.run_coroutine_threadsafe(
            self._process_queue(),
            asyncio.get_event_loop()
        )
        logger.debug("Queue processor started")
    
    async def _process_queue(self) -> None:
        """Обрабатывает очередь задач."""
        while True:
            try:
                # Извлекаем задачу из очереди
                task = await self.processing_queue.get()
                
                # Обрабатываем задачу в зависимости от типа
                if task["type"] == "process_page":
                    await self._process_page(task["url"])
                elif task["type"] == "analyze_page":
                    await self._analyze_page(task["url"], task.get("goal"))
                elif task["type"] == "extract_content":
                    await self._extract_content(task["url"], task.get("goal"))
                elif task["type"] == "predict_actions":
                    await self._predict_actions(task["url"], task.get("goal"))
                
                # Отмечаем задачу как выполненную
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
            
            # Небольшая пауза, чтобы не нагружать процессор
            await asyncio.sleep(0.1)
    
    async def _process_page(self, url: str) -> None:
        """
        Обрабатывает загруженную страницу.
        
        Args:
            url: URL страницы
        """
        logger.info(f"Processing page: {url}")
        
        try:
            # Запускаем предварительную обработку страницы
            await self.page_processor.preprocess_page(url, self.browser)
            
            # Предсказываем следующие действия
            prediction_results = await self.action_predictor.predict_next_actions(url)
            
            # Эмитируем сигнал о завершении анализа
            page_data = await self.page_processor.get_page_data(url)
            if page_data:
                self.page_analyzed.emit(url, {
                    "content_analysis": page_data.get("content_analysis", {}),
                    "links": page_data.get("links", []),
                    "predictions": prediction_results
                })
            
            logger.info(f"Page {url} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing page {url}: {str(e)}")
    
    async def _analyze_page(self, url: str, goal: Optional[str] = None) -> None:
        """
        Анализирует страницу с учетом цели.
        
        Args:
            url: URL страницы
            goal: Цель анализа
        """
        logger.info(f"Analyzing page {url} with goal: {goal}")
        
        try:
            # Получаем данные страницы из кэша
            page_data = await self.page_processor.get_page_data(url)
            
            if not page_data:
                # Если страницы нет в кэше, запускаем обработку
                await self.page_processor.preprocess_page(url, self.browser)
                page_data = await self.page_processor.get_page_data(url)
            
            if not page_data:
                logger.warning(f"Failed to get page data for {url}")
                return
            
            # Оптимизируем контент с учетом цели
            raw_content = page_data.get("raw_content", "")
            if raw_content:
                optimized_content = await self.content_optimizer.optimize_content(raw_content, goal)
                
                # Объединяем результаты анализа
                analysis_results = {
                    "content_analysis": page_data.get("content_analysis", {}),
                    "links": page_data.get("links", []),
                    "structure": page_data.get("structure", {}),
                    "optimized_content": optimized_content
                }
                
                # Эмитируем сигнал с результатами анализа
                self.page_analyzed.emit(url, analysis_results)
                
                logger.info(f"Page {url} analyzed successfully")
            else:
                logger.warning(f"No raw content available for {url}")
        
        except Exception as e:
            logger.error(f"Error analyzing page {url}: {str(e)}")
    
    async def _extract_content(self, url: str, goal: Optional[str] = None) -> None:
        """
        Извлекает содержимое страницы с учетом цели.
        
        Args:
            url: URL страницы
            goal: Цель извлечения
        """
        logger.info(f"Extracting content from {url} with goal: {goal}")
        
        try:
            # Получаем данные страницы из кэша
            page_data = await self.page_processor.get_page_data(url)
            
            if not page_data:
                # Если страницы нет в кэше, запускаем обработку
                await self.page_processor.preprocess_page(url, self.browser)
                page_data = await self.page_processor.get_page_data(url)
            
            if not page_data:
                logger.warning(f"Failed to get page data for {url}")
                return
            
            # Формируем результаты извлечения
            extracted_content = {
                "title": page_data.get("content_analysis", {}).get("title", ""),
                "meta": page_data.get("content_analysis", {}).get("meta", {}),
                "main_content": page_data.get("content_analysis", {}).get("main_content", ""),
                "headings": page_data.get("content_analysis", {}).get("headings", []),
                "links": page_data.get("links", []),
                "goal": goal
            }
            
            # Эмитируем сигнал с результатами извлечения
            self.content_extracted.emit(url, extracted_content)
            
            logger.info(f"Content extracted from {url} successfully")
        
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
    
    async def _predict_actions(self, url: str, goal: Optional[str] = None) -> None:
        """
        Предсказывает следующие действия пользователя.
        
        Args:
            url: URL страницы
            goal: Цель пользователя
        """
        logger.info(f"Predicting actions for {url} with goal: {goal}")
        
        try:
            # Запускаем предсказание действий
            prediction_results = await self.action_predictor.predict_next_actions(url, goal)
            
            # Эмитируем сигнал с результатами предсказания
            self.page_analyzed.emit(url, {
                "predictions": prediction_results
            })
            
            logger.info(f"Actions predicted for {url} successfully")
        
        except Exception as e:
            logger.error(f"Error predicting actions for {url}: {str(e)}")
    
    def analyze_current_page(self, goal: Optional[str] = None) -> None:
        """
        Анализирует текущую страницу.
        
        Args:
            goal: Цель анализа
        """
        if not self.current_url:
            logger.warning("No current page to analyze")
            return
            
        # Добавляем задачу анализа страницы в очередь
        asyncio.run_coroutine_threadsafe(
            self.processing_queue.put({
                "type": "analyze_page",
                "url": self.current_url,
                "goal": goal
            }),
            asyncio.get_event_loop()
        )
        
        logger.info(f"Requested analysis of {self.current_url} with goal: {goal}")
    
    def extract_content(self, goal: Optional[str] = None) -> None:
        """
        Извлекает содержимое текущей страницы.
        
        Args:
            goal: Цель извлечения
        """
        if not self.current_url:
            logger.warning("No current page to extract content from")
            return
            
        # Добавляем задачу извлечения содержимого в очередь
        asyncio.run_coroutine_threadsafe(
            self.processing_queue.put({
                "type": "extract_content",
                "url": self.current_url,
                "goal": goal
            }),
            asyncio.get_event_loop()
        )
        
        logger.info(f"Requested content extraction from {self.current_url} with goal: {goal}")
    
    def predict_actions(self, goal: Optional[str] = None) -> None:
        """
        Предсказывает следующие действия пользователя.
        
        Args:
            goal: Цель пользователя
        """
        if not self.current_url:
            logger.warning("No current page to predict actions for")
            return
            
        # Добавляем задачу предсказания действий в очередь
        asyncio.run_coroutine_threadsafe(
            self.processing_queue.put({
                "type": "predict_actions",
                "url": self.current_url,
                "goal": goal
            }),
            asyncio.get_event_loop()
        )
        
        logger.info(f"Requested action prediction for {self.current_url} with goal: {goal}")
    
    def clear_cache(self) -> None:
        """Очищает кэш страниц."""
        asyncio.run_coroutine_threadsafe(
            self.page_processor.clear_cache(),
            asyncio.get_event_loop()
        )
        self.action_predictor.clear_preloaded()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику браузера.
        
        Returns:
            Dict: Статистика браузера
        """
        return {
            "processor_stats": self.page_processor.get_cache_stats(),
            "predictor_stats": self.action_predictor.get_prediction_stats(),
            "current_url": self.current_url,
            "current_title": self.current_title
        }


def get_enhanced_browser_widget(parent=None) -> Optional[EnhancedBrowserWidget]:
    """
    Создает и возвращает экземпляр улучшенного виджета браузера.
    
    Args:
        parent: Родительский виджет
        
    Returns:
        Optional[EnhancedBrowserWidget]: Экземпляр улучшенного виджета браузера или None в случае ошибки
    """
    try:
        return EnhancedBrowserWidget(parent)
    except Exception as e:
        logger.error(f"Error creating enhanced browser widget: {str(e)}")
        return None
