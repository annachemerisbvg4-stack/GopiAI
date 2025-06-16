// JavaScript для GopiAI WebView Chat

// Проверка загрузки puter.js
function waitForPuter() {
    return new Promise((resolve, reject) => {
        if (typeof puter !== 'undefined') {
            resolve();
        } else {
            let attempts = 0;
            const maxAttempts = 50; // 5 секунд
            const checkInterval = setInterval(() => {
                attempts++;
                if (typeof puter !== 'undefined') {
                    clearInterval(checkInterval);
                    resolve();
                } else if (attempts >= maxAttempts) {
                    clearInterval(checkInterval);
                    reject(new Error('puter.js failed to load'));
                }
            }, 100);
        }
    });
}

class GopiAIChatInterface {
    constructor() {
        this.bridge = null;
        this.currentModel = 'claude-sonnet-4';
        this.isStreaming = true;
        this.autoScroll = true;
        this.theme = 'dark';
        this.chatHistory = [];
        
        this.initializeElements();
        this.initializeWebChannel();
        this.setupEventListeners();
        this.loadSettings();
        this.initializePuter();
    }
    
    initializeElements() {
        // Основные элементы
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-btn');
        this.modelSelect = document.getElementById('model-select');
        this.typingIndicator = document.getElementById('typing-indicator');
        
        // Кнопки заголовка
        this.clearButton = document.getElementById('clear-btn');
        this.exportButton = document.getElementById('export-btn');
        this.settingsButton = document.getElementById('settings-btn');
        
        // Модальные окна
        this.settingsModal = document.getElementById('settings-modal');
        this.exportModal = document.getElementById('export-modal');
        this.closeSettingsBtn = document.getElementById('close-settings');
        this.closeExportBtn = document.getElementById('close-export');
        
        // Настройки
        this.streamToggle = document.getElementById('stream-toggle');
        this.autoScrollToggle = document.getElementById('auto-scroll-toggle');
        this.themeSelect = document.getElementById('theme-select');
        
        // Экспорт
        this.exportFormatSelect = document.getElementById('export-format');
        this.downloadBtn = document.getElementById('download-btn');
        this.copyBtn = document.getElementById('copy-btn');
        this.exportContent = document.getElementById('export-content');
    }
    
    async initializePuter() {
        try {
            await waitForPuter();
            console.log('puter.js loaded successfully');
            
            // Показываем приветственное сообщение
            this.addAIMessage('Welcome to GopiAI WebView Chat! I\'m powered by puter.js and ready to help you. You can switch between Claude Sonnet 4 and Claude Opus 4 models using the dropdown above.');
            
        } catch (error) {
            console.error('Failed to load puter.js:', error);
            this.addSystemMessage('⚠️ Error: Failed to load puter.js. Please check your internet connection and refresh the page.');
        }
    }
    
    initializeWebChannel() {
        // Инициализация QWebChannel для связи с Python
        if (typeof QWebChannel !== 'undefined') {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                this.bridge = channel.objects.bridge;
                console.log('WebChannel bridge connected');
            });
        } else {
            console.warn('QWebChannel not available, running in standalone mode');
        }
    }
    
    setupEventListeners() {
        // Отправка сообщений
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Автоматическое изменение размера textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Смена модели
        this.modelSelect.addEventListener('change', (e) => {
            this.changeModel(e.target.value);
        });
        
        // Кнопки заголовка
        this.clearButton.addEventListener('click', () => this.clearChat());
        this.exportButton.addEventListener('click', () => this.showExportModal());
        this.settingsButton.addEventListener('click', () => this.showSettingsModal());
        
        // Модальные окна
        if (this.closeSettingsBtn) {
            this.closeSettingsBtn.addEventListener('click', () => this.hideSettingsModal());
        }
        if (this.closeExportBtn) {
            this.closeExportBtn.addEventListener('click', () => this.hideExportModal());
        }
        
        // Настройки
        if (this.streamToggle) {
            this.streamToggle.addEventListener('change', (e) => {
                this.isStreaming = e.target.checked;
                this.saveSettings();
            });
        }
        
        if (this.autoScrollToggle) {
            this.autoScrollToggle.addEventListener('change', (e) => {
                this.autoScroll = e.target.checked;
                this.saveSettings();
            });
        }
        
        if (this.themeSelect) {
            this.themeSelect.addEventListener('change', (e) => {
                this.setTheme(e.target.value);
            });
        }
        
        // Экспорт
        if (this.exportFormatSelect) {
            this.exportFormatSelect.addEventListener('change', () => this.updateExportPreview());
        }
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadChat());
        }
        if (this.copyBtn) {
            this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        }
        
        // Закрытие модальных окон при клике вне их
        window.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.hideSettingsModal();
            }
            if (e.target === this.exportModal) {
                this.hideExportModal();
            }
        });
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Очистка поля ввода
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Добавление сообщения пользователя
        this.addUserMessage(message);
        
        // Проверка на browser automation команды
        if (message.startsWith('/')) {
            const parts = message.slice(1).split(' ');
            const command = parts[0];
            const args = parts.slice(1);
            
            // Диагностические команды
            if (command === 'bridge-debug') {
                this.debugBridge();
                return;
            }
            
            if (command === 'get-page-info') {
                await this.getPythonBrowserPageInfo();
                return;
            }
            
            if (command === 'capabilities') {
                await this.getPythonBrowserCapabilities();
                return;
            }
            
            if (command === 'test-python-bridge') {
                await this.testPythonBridgeAutomation();
                return;
            }
            

            
            // Команды для работы с текущей страницей
            if (command === 'search' && args[0]) {
                const searchQuery = args.join(' ');
                await this.executeClaudeTool('execute_javascript', { 
                    script: `
                        const searchBox = document.querySelector('input[name="q"], input[type="search"], textarea[name="q"]');
                        if (searchBox) {
                            searchBox.focus();
                            searchBox.value = '${searchQuery}';
                            searchBox.dispatchEvent(new Event('input', { bubbles: true }));
                            const form = searchBox.closest('form');
                            if (form) {
                                form.submit();
                            } else {
                                searchBox.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', bubbles: true }));
                            }
                            return 'Search executed: ${searchQuery}';
                        } else {
                            return 'Search box not found on this page';
                        }
                    `
                });
                return;
            }
            
            if (command === 'click' && args[0]) {
                await this.executeClaudeTool('execute_javascript', { 
                    script: `
                        const element = document.querySelector('${args[0]}');
                        if (element) {
                            element.click();
                            return 'Clicked element: ${args[0]}';
                        } else {
                            return 'Element not found: ${args[0]}';
                        }
                    `
                });
                return;
            }
            
            if (command === 'weather-ny') {
                // Полный цикл: открыть Google -> найти погоду -> извлечь результат
                this.addSystemMessage('🌤️ Checking New York weather...');
                
                // Шаг 1: Открыть Google если не на нем
                await this.executeClaudeTool('navigate_to_url', { url: 'https://www.google.com' });
                
                // Шаг 2: Подождать немного для загрузки
                setTimeout(async () => {
                    // Шаг 3: Поиск погоды
                    await this.executeClaudeTool('execute_javascript', { 
                        script: `
                            const searchBox = document.querySelector('input[name="q"], textarea[name="q"]');
                            if (searchBox) {
                                searchBox.focus();
                                searchBox.value = 'weather New York tomorrow';
                                searchBox.form.submit();
                                return 'Searching for New York weather...';
                            }
                            return 'Search box not found';
                        `
                    });
                    
                    // Шаг 4: Извлечь результаты через несколько секунд
                    setTimeout(async () => {
                        await this.executeClaudeTool('execute_javascript', { 
                            script: `
                                const weatherInfo = [];
                                
                                // Ищем виджет погоды Google
                                const weatherWidget = document.querySelector('[data-attrid="hw_date"], .wob_t, .wob_tm');
                                if (weatherWidget) {
                                    const temp = document.querySelector('.wob_t')?.textContent;
                                    const desc = document.querySelector('.wob_dcp')?.textContent;
                                    const location = document.querySelector('.wob_loc')?.textContent;
                                    weatherInfo.push(\`📍 \${location || 'New York'}: \${temp || 'N/A'}°, \${desc || 'N/A'}\`);
                                }
                                
                                // Ищем обычные результаты поиска
                                const results = document.querySelectorAll('.g h3, .BNeawe');
                                for (let i = 0; i < Math.min(3, results.length); i++) {
                                    const text = results[i].textContent;
                                    if (text.includes('°') || text.toLowerCase().includes('weather')) {
                                        weatherInfo.push(\`🔍 \${text}\`);
                                    }
                                }
                                
                                return weatherInfo.length > 0 ? 
                                    '🌤️ New York Weather:\n' + weatherInfo.join('\n') : 
                                    '❌ Weather information not found';
                            `
                        });
                    }, 3000);
                }, 2000);
                
                return;
            }
            
            if (command === 'get-weather-ny') {
                await this.executeClaudeTool('execute_javascript', { 
                    script: `
                        // Ищем информацию о погоде на странице
                        const weatherElements = [
                            ...document.querySelectorAll('*')
                        ].filter(el => {
                            const text = el.textContent.toLowerCase();
                            return text.includes('new york') && 
                                   (text.includes('weather') || text.includes('temperature') || text.includes('°'));
                        });
                        
                        if (weatherElements.length > 0) {
                            return weatherElements.slice(0, 3).map(el => el.textContent.trim()).join(' | ');
                        } else {
                            return 'Weather info for New York not found on current page';
                        }
                    `
                });
                return;
            }
            
            // Claude Tools команды
            if (command === 'claude-tools') {
                await this.getClaudeToolsList();
                return;
            }
            
            if (command === 'test-claude-tools') {
                await this.testClaudeTools();
                return;
            }
            
            // Исполнение Claude tools через команды
            if (command === 'claude-navigate') {
                if (args[0]) {
                    await this.executeClaudeTool('navigate_to_url', { url: args[0] });
                } else {
                    this.addSystemMessage('❌ Usage: /claude-navigate <url>');
                }
                return;
            }
            
            if (command === 'claude-script') {
                if (args.length > 0) {
                    const script = args.join(' ');
                    await this.executeClaudeTool('execute_javascript', { script: script });
                } else {
                    this.addSystemMessage('❌ Usage: /claude-script <javascript_code>');
                }
                return;
            }
            
            if (command === 'claude-read') {
                if (args[0]) {
                    await this.executeClaudeTool('read_file', { file_path: args[0] });
                } else {
                    this.addSystemMessage('❌ Usage: /claude-read <file_path>');
                }
                return;
            }
            
            if (command === 'claude-write') {
                if (args.length >= 2) {
                    const filePath = args[0];
                    const content = args.slice(1).join(' ');
                    await this.executeClaudeTool('write_file', { file_path: filePath, content: content });
                } else {
                    this.addSystemMessage('❌ Usage: /claude-write <file_path> <content>');
                }
                return;
            }
            
            const result = await this.processBrowserCommand(command, args);
            if (result !== null) {
                return; // Команда обработана, не отправляем в AI
            }
        }
        
        // Уведомление Python через bridge
        if (this.bridge) {
            this.bridge.send_message(message);
        }
        
        // Показ индикатора набора
        this.showTypingIndicator();
        
        try {
            if (this.isStreaming) {
                await this.sendStreamingMessage(message);
            } else {
                await this.sendRegularMessage(message);
            }
        } catch (error) {
            this.handleError(error);
        } finally {
            this.hideTypingIndicator();
        }
    }
    
    async sendStreamingMessage(message) {
        try {
            const response = await puter.ai.chat(message, {
                model: this.currentModel,
                stream: true
            });
            
            const messageElement = this.addAIMessage('', true); // Пустое сообщение для стриминга
            let fullResponse = '';
            
            for await (const part of response) {
                if (part?.text) {
                    fullResponse += part.text;
                    this.updateMessageContent(messageElement, fullResponse);
                    
                    if (this.autoScroll) {
                        this.scrollToBottom();
                    }
                }
            }
            
            // Уведомление Python о полном ответе
            if (this.bridge && fullResponse) {
                this.bridge.receive_ai_message(this.currentModel, fullResponse);
            }
            
        } catch (error) {
            throw new Error(`Streaming error: ${error.message}`);
        }
    }
    
    async sendRegularMessage(message) {
        try {
            const response = await puter.ai.chat(message, {
                model: this.currentModel,
                stream: false
            });
            
            const aiResponse = response.message?.content?.[0]?.text || response || 'No response received';
            this.addAIMessage(aiResponse);
            
            // Уведомление Python
            if (this.bridge) {
                this.bridge.receive_ai_message(this.currentModel, aiResponse);
            }
            
        } catch (error) {
            throw new Error(`Regular message error: ${error.message}`);
        }
    }
    
    addUserMessage(message) {
        const messageElement = this.createMessageElement('user', message);
        this.messagesContainer.appendChild(messageElement);
        
        if (this.autoScroll) {
            this.scrollToBottom();
        }
    }
    
    addAIMessage(message, isStreaming = false) {
        const messageElement = this.createMessageElement('ai', message, isStreaming);
        this.messagesContainer.appendChild(messageElement);
        
        if (this.autoScroll) {
            this.scrollToBottom();
        }
        
        return messageElement;
    }
    
    createMessageElement(type, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (type === 'ai') {
            const header = document.createElement('div');
            header.className = 'message-header';
            
            const sender = document.createElement('span');
            sender.className = 'sender';
            sender.textContent = '🤖 GopiAI Assistant';
            
            const modelBadge = document.createElement('span');
            modelBadge.className = 'model-badge';
            modelBadge.textContent = this.getModelDisplayName(this.currentModel);
            
            header.appendChild(sender);
            header.appendChild(modelBadge);
            bubble.appendChild(header);
        }
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        if (isStreaming) {
            messageContent.classList.add('streaming');
        }
        
        bubble.appendChild(messageContent);
        
        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = new Date().toLocaleTimeString();
        bubble.appendChild(timeElement);
        
        messageDiv.appendChild(bubble);
        return messageDiv;
    }
    
    addSystemMessage(message) {
        const messageElement = this.createSystemMessageElement(message);
        this.messagesContainer.appendChild(messageElement);
        
        if (this.autoScroll) {
            this.scrollToBottom();
        }
    }
    
    createSystemMessageElement(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = content;
        
        bubble.appendChild(messageContent);
        messageDiv.appendChild(bubble);
        return messageDiv;
    }
    
    updateMessageContent(messageElement, content) {
        const contentElement = messageElement.querySelector('.message-content');
        if (contentElement) {
            contentElement.innerHTML = this.formatMessage(content);
        }
    }
    
    formatMessage(content) {
        // Простое форматирование текста
        return content.replace(/\n/g, '<br>');
    }
    
    getModelDisplayName(modelId) {
        const models = {
            'claude-sonnet-4': 'Claude Sonnet 4',
            'claude-opus-4': 'Claude Opus 4'
        };
        return models[modelId] || modelId;
    }
    
    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
        }
    }
    
    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }
    
    handleError(error) {
        console.error('Chat error:', error);
        this.addSystemMessage(`❌ Error: ${error.message}`);
    }
    
    changeModel(modelId) {
        this.currentModel = modelId;
        this.addSystemMessage(`🔄 Switched to ${this.getModelDisplayName(modelId)}`);
    }
    
    clearChat() {
        this.messagesContainer.innerHTML = '';
        this.chatHistory = [];
        this.addSystemMessage('💬 Chat cleared');
    }
    
    // Настройки
    loadSettings() {
        const settings = localStorage.getItem('gopiai-chat-settings');
        if (settings) {
            try {
                const parsed = JSON.parse(settings);
                this.isStreaming = parsed.isStreaming !== undefined ? parsed.isStreaming : true;
                this.autoScroll = parsed.autoScroll !== undefined ? parsed.autoScroll : true;
                this.theme = parsed.theme || 'dark';
                
                // Применение настроек к UI
                if (this.streamToggle) this.streamToggle.checked = this.isStreaming;
                if (this.autoScrollToggle) this.autoScrollToggle.checked = this.autoScroll;
                if (this.themeSelect) this.themeSelect.value = this.theme;
                this.setTheme(this.theme);
            } catch (error) {
                console.error('Error loading settings:', error);
            }
        }
    }
    
    saveSettings() {
        const settings = {
            isStreaming: this.isStreaming,
            autoScroll: this.autoScroll,
            theme: this.theme
        };
        localStorage.setItem('gopiai-chat-settings', JSON.stringify(settings));
    }
    
    setTheme(theme) {
        this.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        this.saveSettings();
    }
    
    // Модальные окна
    showSettingsModal() {
        if (this.settingsModal) {
            this.settingsModal.style.display = 'flex';
        }
    }
    
    hideSettingsModal() {
        if (this.settingsModal) {
            this.settingsModal.style.display = 'none';
        }
    }
    
    showExportModal() {
        if (this.exportModal) {
            this.exportModal.style.display = 'flex';
            this.updateExportPreview();
        }
    }
    
    hideExportModal() {
        if (this.exportModal) {
            this.exportModal.style.display = 'none';
        }
    }
    
    // Экспорт
    updateExportPreview() {
        if (!this.exportContent) return;
        
        const format = this.exportFormatSelect ? this.exportFormatSelect.value : 'txt';
        const exportData = this.formatExportData(this.chatHistory, format);
        this.exportContent.textContent = exportData;
    }
    
    formatExportData(history, format) {
        switch (format) {
            case 'json':
                return JSON.stringify(history, null, 2);
            
            case 'txt':
                return history.map(msg => {
                    const role = msg.role === 'user' ? 'User' : `AI (${msg.model})`;
                    return `[${msg.timestamp}] ${role}: ${msg.content}`;
                }).join('\n');
            
            case 'md':
                let md = '# Chat History\n\n';
                history.forEach(msg => {
                    const role = msg.role === 'user' ? '**User**' : `**AI (${msg.model})**`;
                    md += `## ${role} - ${msg.timestamp}\n${msg.content}\n\n`;
                });
                return md;
            
            default:
                return JSON.stringify(history, null, 2);
        }
    }
    
    downloadChat() {
        if (!this.exportContent) return;
        
        const format = this.exportFormatSelect ? this.exportFormatSelect.value : 'txt';
        const content = this.exportContent.textContent;
        const filename = `gopiai-chat-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.${format}`;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    async copyToClipboard() {
        if (!this.exportContent) return;
        
        const content = this.exportContent.textContent;
        try {
            await navigator.clipboard.writeText(content);
            // Показать уведомление об успехе
            if (this.copyBtn) {
                const originalText = this.copyBtn.textContent;
                this.copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    this.copyBtn.textContent = originalText;
                }, 2000);
            }
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
        }
    }
    
    // Метод для обновления темы из Python
    onThemeUpdated() {
        console.log('Theme updated from Python');
        // Можно добавить дополнительную логику обновления темы здесь
        // например, пересчет контрастности или анимации
        this.applyThemeTransitions();
    }
    
    applyThemeTransitions() {
        // Добавляем плавные переходы при смене темы
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            if (!element.style.transition) {
                element.style.transition = 'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease';
            }
        });
        
        // Убираем переходы через некоторое время для обычной работы
        setTimeout(() => {
            allElements.forEach(element => {
                if (element.style.transition.includes('background-color 0.3s ease')) {
                    element.style.transition = '';
                }
            });
        }, 500);
    }
    
    // Обновление badge модели в соответствии с темой
    updateModelBadge() {
        const badges = document.querySelectorAll('.model-badge');
        badges.forEach(badge => {
            badge.textContent = this.currentModel === 'claude-sonnet-4' ? 'Claude Sonnet 4' : 'Claude Opus 4';
        });
    }
    
    // ==============================================
    // BROWSER AUTOMATION FUNCTIONS via Puter.js
    // ==============================================
    
    async testPuterDrivers() {
        try {
            console.log('Testing Puter.js drivers...');
            
            // Список доступных драйверов
            const drivers = await puter.drivers.list();
            console.log('Available drivers:', drivers);
            
            this.addSystemMessage(`🔍 Available Puter.js drivers: ${JSON.stringify(drivers, null, 2)}`);
            
            return drivers;
        } catch (error) {
            console.error('Error testing Puter drivers:', error);
            this.addSystemMessage(`❌ Error testing Puter drivers: ${error.message}`);
            return null;
        }
    }
    
    async testBrowserAutomation() {
        try {
            console.log('Testing browser automation capabilities...');
            
            // Тестируем базовые browser operations
            const tests = [];
            
            // Тест 1: Проверка доступных интерфейсов
            try {
                const result = await puter.drivers.call('browser', 'chrome', 'getCapabilities', {});
                tests.push({ test: 'Browser capabilities', success: true, result });
            } catch (error) {
                tests.push({ test: 'Browser capabilities', success: false, error: error.message });
            }
            
            // Тест 2: Проверка возможности навигации
            try {
                const result = await puter.drivers.call('browser', 'chrome', 'navigate', { url: 'about:blank' });
                tests.push({ test: 'Navigate to blank page', success: true, result });
            } catch (error) {
                tests.push({ test: 'Navigate to blank page', success: false, error: error.message });
            }
            
            // Тест 3: Проверка получения информации о странице
            try {
                const result = await puter.drivers.call('browser', 'chrome', 'getPageInfo', {});
                tests.push({ test: 'Get page info', success: true, result });
            } catch (error) {
                tests.push({ test: 'Get page info', success: false, error: error.message });
            }
            
            console.log('Browser automation test results:', tests);
            this.addSystemMessage(`🔧 Browser automation test results:
${JSON.stringify(tests, null, 2)}`);
            
            return tests;
        } catch (error) {
            console.error('Error testing browser automation:', error);
            this.addSystemMessage(`❌ Error testing browser automation: ${error.message}`);
            return null;
        }
    }
    
    async performBrowserAction(action, params = {}) {
        try {
            console.log(`Performing browser action: ${action}`, params);
            
            let result;
            
            switch (action) {
                case 'navigate':
                    result = await puter.drivers.call('browser', 'chrome', 'navigate', { url: params.url });
                    break;
                
                case 'click':
                    result = await puter.drivers.call('browser', 'chrome', 'click', { 
                        selector: params.selector,
                        x: params.x,
                        y: params.y
                    });
                    break;
                
                case 'type':
                    result = await puter.drivers.call('browser', 'chrome', 'type', {
                        selector: params.selector,
                        text: params.text
                    });
                    break;
                
                case 'getText':
                    result = await puter.drivers.call('browser', 'chrome', 'getText', {
                        selector: params.selector
                    });
                    break;
                
                case 'getPageSource':
                    result = await puter.drivers.call('browser', 'chrome', 'getPageSource', {});
                    break;
                
                case 'screenshot':
                    result = await puter.drivers.call('browser', 'chrome', 'screenshot', {});
                    break;
                
                default:
                    throw new Error(`Unknown browser action: ${action}`);
            }
            
            console.log(`Browser action ${action} result:`, result);
            this.addSystemMessage(`✅ Browser action "${action}" completed: ${JSON.stringify(result)}`);
            
            // Уведомление Python через bridge
            if (this.bridge) {
                this.bridge.browser_automation_result(action, result);
            }
            
            return result;
        } catch (error) {
            console.error(`Error performing browser action ${action}:`, error);
            this.addSystemMessage(`❌ Error performing browser action "${action}": ${error.message}`);
            return null;
        }
    }
    
    async getBrowserState() {
        try {
            const state = {
                url: await this.performBrowserAction('getPageInfo'),
                title: document.title,
                timestamp: new Date().toISOString()
            };
            
            console.log('Current browser state:', state);
            return state;
        } catch (error) {
            console.error('Error getting browser state:', error);
            return null;
        }
    }
    
    // Команды для тестирования из chat интерфейса
    async processBrowserCommand(command, args = []) {
        try {
            switch (command.toLowerCase()) {
                case 'test-drivers':
                    return await this.testPuterDrivers();
                
                case 'test-automation':
                    return await this.testBrowserAutomation();
                
                case 'test-python-bridge':
                    return await this.testPythonBridgeAutomation();
                
                case 'navigate':
                    if (args[0]) {
                        return await this.executePythonBrowserAction('navigate', { url: args[0] });
                    } else {
                        this.addSystemMessage('❌ Usage: /navigate <url>');
                        return null;
                    }
                
                case 'click':
                    if (args[0]) {
                        return await this.executePythonBrowserAction('click', { selector: args[0] });
                    } else {
                        this.addSystemMessage('❌ Usage: /click <selector>');
                        return null;
                    }
                
                case 'type':
                    if (args[0] && args[1]) {
                        return await this.executePythonBrowserAction('type', { 
                            selector: args[0], 
                            text: args.slice(1).join(' ') 
                        });
                    } else {
                        this.addSystemMessage('❌ Usage: /type <selector> <text>');
                        return null;
                    }
                
                case 'screenshot':
                    return await this.executePythonBrowserAction('screenshot');
                
                case 'get-text':
                    if (args[0]) {
                        return await this.executePythonBrowserAction('get_text', { selector: args[0] });
                    } else {
                        this.addSystemMessage('❌ Usage: /get-text <selector>');
                        return null;
                    }
                
                case 'get-source':
                    return await this.executePythonBrowserAction('get_source');
                
                case 'get-page-info':
                    return await this.getPythonBrowserPageInfo();
                
                case 'capabilities':
                    return await this.getPythonBrowserCapabilities();
                
                case 'bridge-debug':
                    return await this.debugBridge();
                
                case 'help':
                    this.addSystemMessage(`🔧 Available browser automation commands:
                    
/test-drivers - List available Puter.js drivers
/test-automation - Test browser automation capabilities
/test-python-bridge - Test Python bridge automation
/navigate <url> - Navigate to URL (via Python)
/click <selector> - Click element by CSS selector
/type <selector> <text> - Type text into element
/screenshot - Take page screenshot
/get-text <selector> - Get text from element
/get-source - Get page HTML source
/get-page-info - Get current page information
/capabilities - Show browser automation capabilities

/help - Show this help`);
                    return null;
                
                default:
                    this.addSystemMessage(`❌ Unknown browser command: ${command}. Type /help for available commands.`);
                    return null;
            }
        } catch (error) {
            console.error(`Error processing browser command ${command}:`, error);
            this.addSystemMessage(`❌ Error processing command "${command}": ${error.message}`);
            return null;
        }
    }
    
    // ==============================================
    // BRIDGE DEBUGGING
    // ==============================================
    
    async debugBridge() {
        try {
            console.log('Debugging bridge methods...');
            
            if (!this.bridge) {
                this.addSystemMessage('❌ Bridge not available');
                return null;
            }
            
            // Получаем все методы bridge
            const bridgeMethods = [];
            for (let prop in this.bridge) {
                if (typeof this.bridge[prop] === 'function') {
                    bridgeMethods.push(prop);
                }
            }
            
            console.log('Available bridge methods:', bridgeMethods);
            
            const methodsList = bridgeMethods.join(', ');
            this.addSystemMessage(`🔍 Bridge methods (${bridgeMethods.length}): ${methodsList}`);
            
            // Проверяем наличие наших новых методов
            const ourMethods = [
                'get_browser_automation_capabilities',
                'execute_browser_action', 
                'get_browser_page_info',
                'browser_automation_result'
            ];
            
            const missingMethods = ourMethods.filter(method => !bridgeMethods.includes(method));
            const availableMethods = ourMethods.filter(method => bridgeMethods.includes(method));
            
            if (availableMethods.length > 0) {
                this.addSystemMessage(`✅ Available automation methods: ${availableMethods.join(', ')}`);
            }
            
            if (missingMethods.length > 0) {
                this.addSystemMessage(`❌ Missing automation methods: ${missingMethods.join(', ')}`);
                this.addSystemMessage('💡 Tip: Restart the application to load new methods');
            }
            
            return {
                total_methods: bridgeMethods.length,
                available_automation: availableMethods,
                missing_automation: missingMethods,
                bridge_available: true
            };
            
        } catch (error) {
            console.error('Error debugging bridge:', error);
            this.addSystemMessage(`❌ Error debugging bridge: ${error.message}`);
            return null;
        }
    }
    
    // ==============================================
    // PYTHON BRIDGE BROWSER AUTOMATION
    // ==============================================
    
    async testPythonBridgeAutomation() {
        try {
            console.log('Testing Python bridge browser automation...');
            
            // Проверяем доступность bridge
            if (!this.bridge) {
                this.addSystemMessage('❌ Python bridge not available');
                return null;
            }
            
            // Тест 1: Получение capabilities
            let capabilities = null;
            try {
                const capResult = this.bridge.get_browser_automation_capabilities();
                // Проверяем, является ли результат Promise
                const capResultStr = (capResult && typeof capResult.then === 'function') ? 
                    await capResult : capResult;
                capabilities = JSON.parse(capResultStr);
                this.addSystemMessage(`✅ Browser capabilities available: ${capabilities.functions ? capabilities.functions.length : 'unknown'} actions`);
            } catch (error) {
                this.addSystemMessage(`❌ Error getting capabilities: ${error.message}`);
                console.error('Capabilities error:', error, 'Raw result:', this.bridge.get_browser_automation_capabilities());
            }
            
            // Тест 2: Получение информации о странице
            try {
                const pageResult = this.bridge.get_browser_page_info();
                const pageResultStr = (pageResult && typeof pageResult.then === 'function') ? 
                    await pageResult : pageResult;
                const pageInfo = JSON.parse(pageResultStr);
                this.addSystemMessage(`✅ Page info: ${pageInfo.url || 'unknown'}`);
            } catch (error) {
                this.addSystemMessage(`❌ Error getting page info: ${error.message}`);
                console.error('Page info error:', error, 'Raw result:', this.bridge.get_browser_page_info());
            }
            
            // Тест 3: Выполнение тестового действия
            try {
                const testResult = this.bridge.execute_browser_action('get_page_info', '{}');
                const testResultStr = (testResult && typeof testResult.then === 'function') ? 
                    await testResult : testResult;
                const result = JSON.parse(testResultStr);
                this.addSystemMessage(`✅ Test action result: ${result.success ? 'success' : result.status}`);
            } catch (error) {
                this.addSystemMessage(`❌ Error executing test action: ${error.message}`);
                console.error('Test action error:', error, 'Raw result:', this.bridge.execute_browser_action('get_page_info', '{}'));
            }
            
            const summary = {
                bridge_available: !!this.bridge,
                capabilities: capabilities,
                test_completed: true
            };
            
            console.log('Python bridge automation test results:', summary);
            this.addSystemMessage(`🔧 Python bridge automation test completed. Bridge available: ${summary.bridge_available ? '✅' : '❌'}`);
            
            return summary;
        } catch (error) {
            console.error('Error testing Python bridge automation:', error);
            this.addSystemMessage(`❌ Error testing Python bridge automation: ${error.message}`);
            return null;
        }
    }
    
    async executePythonBrowserAction(action, params = {}) {
        try {
            if (!this.bridge) {
                this.addSystemMessage('❌ Python bridge not available');
                return null;
            }
            
            console.log(`Executing Python browser action: ${action}`, params);
            
            const paramsJson = JSON.stringify(params);
            const resultJson = this.bridge.execute_browser_action(action, paramsJson);
            const resultJsonStr = (resultJson && typeof resultJson.then === 'function') ? 
                await resultJson : resultJson;
            const result = JSON.parse(resultJsonStr);
            
            console.log(`Python browser action ${action} result:`, result);
            
            if (result.status === 'error') {
                this.addSystemMessage(`❌ Browser action "${action}" failed: ${result.error}`);
            } else {
                this.addSystemMessage(`✅ Browser action "${action}" completed: ${result.message || result.status}`);
            }
            
            // Уведомление bridge о результате
            if (typeof this.bridge.browser_automation_result === 'function') {
                this.bridge.browser_automation_result(action, resultJson);
            }
            
            return result;
        } catch (error) {
            console.error(`Error executing Python browser action ${action}:`, error);
            this.addSystemMessage(`❌ Error executing browser action "${action}": ${error.message}`);
            return null;
        }
    }
    
    async getPythonBrowserPageInfo() {
        try {
            if (!this.bridge) {
                this.addSystemMessage('❌ Python bridge not available');
                return null;
            }
            
            // Вызываем метод без параметров, так как он не принимает их
            const resultJson = this.bridge.get_browser_page_info();
            console.log('Raw page info result:', resultJson, 'Type:', typeof resultJson);
            
            const resultJsonStr = (resultJson && typeof resultJson.then === 'function') ? 
                await resultJson : resultJson;
            console.log('Page info result after await:', resultJsonStr, 'Type:', typeof resultJsonStr);
            
            if (!resultJsonStr || resultJsonStr.trim() === '') {
                throw new Error('Empty response from get_browser_page_info');
            }
            
            const result = JSON.parse(resultJsonStr);
            
            console.log('Python browser page info:', result);
            this.addSystemMessage(`📄 Page info: URL: ${result.url}, Title: ${result.title}`);
            
            return result;
        } catch (error) {
            console.error('Error getting Python browser page info:', error);
            this.addSystemMessage(`❌ Error getting page info: ${error.message}`);
            return null;
        }
    }
    
    async getPythonBrowserCapabilities() {
        try {
            if (!this.bridge) {
                this.addSystemMessage('❌ Python bridge not available');
                return null;
            }
            
            const resultJson = this.bridge.get_browser_automation_capabilities();
            const resultJsonStr = (resultJson && typeof resultJson.then === 'function') ? 
                await resultJson : resultJson;
            const result = JSON.parse(resultJsonStr);
            
            console.log('Python browser capabilities:', result);
            this.addSystemMessage(`🔧 Browser automation capabilities:
${JSON.stringify(result, null, 2)}`);
            
            return result;
        } catch (error) {
            console.error('Error getting Python browser capabilities:', error);
            this.addSystemMessage(`❌ Error getting capabilities: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Асинхронное выполнение JavaScript с получением результата
     * Использует новый метод execute_script_async согласно Qt документации
     */
    async executeScriptAsync(script, timeout = 5000) {
        try {
            if (!this.bridge) {
                throw new Error('Python bridge not available');
            }
            
            // Генерируем уникальный ID для действия
            const actionId = 'script_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            
            console.log(`🚀 Executing async script with ID: ${actionId}`);
            console.log(`📜 Script: ${script.substr(0, 100)}...`);
            
            // Создаем Promise для ожидания результата
            const resultPromise = new Promise((resolve, reject) => {
                // Устанавливаем timeout
                const timeoutId = setTimeout(() => {
                    reject(new Error(`Script execution timeout after ${timeout}ms`));
                }, timeout);
                
                // Создаем временный обработчик результата
                const originalHandler = this.onBrowserActionCompleted;
                this.onBrowserActionCompleted = (receivedActionId, action, resultJson) => {
                    // Проверяем, что это наш результат
                    if (receivedActionId === actionId) {
                        clearTimeout(timeoutId);
                        // Восстанавливаем оригинальный обработчик
                        this.onBrowserActionCompleted = originalHandler;
                        
                        try {
                            const result = JSON.parse(resultJson);
                            if (result.success) {
                                resolve(result.result);
                            } else {
                                reject(new Error(result.error || 'Script execution failed'));
                            }
                        } catch (e) {
                            reject(new Error('Failed to parse result JSON: ' + e.message));
                        }
                    } else if (originalHandler) {
                        // Передаем другие результаты оригинальному обработчику
                        originalHandler(receivedActionId, action, resultJson);
                    }
                };
            });
            
            // Вызываем асинхронный метод
            this.bridge.execute_script_async(actionId, script, "true");
            
            // Ждем результат
            const result = await resultPromise;
            console.log(`✅ Script ${actionId} completed:`, result);
            
            return result;
            
        } catch (error) {
            console.error('Error in executeScriptAsync:', error);
            throw error;
        }
    }
    
    /**
     * Обработчик результатов browser automation
     * Вызывается из Python когда асинхронное действие завершено
     */
    onBrowserActionCompleted(actionId, action, resultJson) {
        try {
            console.log(`📨 Browser action completed: ${actionId} (${action})`);
            console.log('Result:', resultJson);
            
            const result = JSON.parse(resultJson);
            
            if (result.success) {
                this.addSystemMessage(`✅ Browser action ${actionId} completed successfully`);
            } else {
                this.addSystemMessage(`❌ Browser action ${actionId} failed: ${result.error}`);
            }
            
        } catch (error) {
            console.error('Error in onBrowserActionCompleted:', error);
            this.addSystemMessage(`❌ Error processing browser action result: ${error.message}`);
        }
    }
    
    /**
     * Обработчик результатов Claude tools
     * Вызывается из Python когда Claude tool завершен
     */
    onClaudeToolResult(requestId, toolName, resultData) {
        try {
            console.log(`🔧 Claude tool completed: ${requestId} (${toolName})`);
            console.log('Tool result:', resultData);
            
            // resultData уже является объектом, не нужно парсить JSON
            const result = resultData;
            
            if (result.success) {
                this.addSystemMessage(`✅ Claude tool "${toolName}" [${requestId}] completed successfully`);
                
                // Специальная обработка для разных типов инструментов
                if (toolName === 'get_page_source' && result.result) {
                    const sourcePreview = result.result.substr(0, 200) + (result.result.length > 200 ? '...' : '');
                    this.addSystemMessage(`📄 Page source preview: ${sourcePreview}`);
                }
                else if (toolName === 'read_file' && result.content) {
                    const contentPreview = result.content.substr(0, 300) + (result.content.length > 300 ? '...' : '');
                    this.addSystemMessage(`📂 File content preview: ${contentPreview}`);
                }
                else if (toolName === 'execute_javascript' && result.result) {
                    this.addSystemMessage(`📜 JavaScript result: ${JSON.stringify(result.result)}`);
                }
                else if (result.message || result.result) {
                    this.addSystemMessage(`📋 Tool result: ${result.message || JSON.stringify(result.result)}`);
                }
            } else {
                this.addSystemMessage(`❌ Claude tool "${toolName}" [${requestId}] failed: ${result.error}`);
            }
            
        } catch (error) {
            console.error('Error in onClaudeToolResult:', error);
            this.addSystemMessage(`❌ Error processing Claude tool result: ${error.message}`);
        }
    }
    
    /**
     * Выполнение Claude tool
     */
    async executeClaudeTool(toolName, params = {}) {
        try {
            if (!this.bridge) {
                throw new Error('Python bridge not available');
            }
            
            console.log(`🔧 Executing Claude tool: ${toolName}`, params);
            
            const paramsJson = JSON.stringify(params);
            
            // Проверяем доступность нового метода
            if (typeof this.bridge.execute_claude_tool === 'function') {
                const resultJson = this.bridge.execute_claude_tool(toolName, paramsJson);
                const resultJsonStr = (resultJson && typeof resultJson.then === 'function') ? 
                    await resultJson : resultJson;
                const result = JSON.parse(resultJsonStr);
                
                console.log(`Claude tool ${toolName} result:`, result);
                
                return result;
            } else {
                throw new Error('execute_claude_tool method not available in bridge');
            }
            
        } catch (error) {
            console.error(`Error executing Claude tool ${toolName}:`, error);
            this.addSystemMessage(`❌ Error executing Claude tool "${toolName}": ${error.message}`);
            return null;
        }
    }
    
    /**
     * Получение списка доступных Claude tools
     */
    async getClaudeToolsList() {
        try {
            if (!this.bridge) {
                throw new Error('Python bridge not available');
            }
            
            if (typeof this.bridge.get_claude_tools_list === 'function') {
                const resultJson = this.bridge.get_claude_tools_list();
                const resultJsonStr = (resultJson && typeof resultJson.then === 'function') ? 
                    await resultJson : resultJson;
                const result = JSON.parse(resultJsonStr);
                
                console.log('Claude tools list:', result);
                this.addSystemMessage(`🔧 Claude Tools available:
${JSON.stringify(result, null, 2)}`);
                return result;
            } else {
                throw new Error('get_claude_tools_list method not available in bridge');
            }
            
        } catch (error) {
            console.error('Error getting Claude tools list:', error);
            this.addSystemMessage(`❌ Error getting Claude tools: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Тестирование Claude tools
     */
    async testClaudeTools() {
        try {
            console.log('Testing Claude tools...');
            this.addSystemMessage('🧪 Testing Claude tools integration...');
            
            // Тест 1: Получение списка инструментов
            const toolsList = await this.getClaudeToolsList();
            if (!toolsList || !toolsList.success) {
                this.addSystemMessage('❌ Failed to get Claude tools list');
                return null;
            }
            
            // Тест 2: Тестирование get_current_url
            try {
                const urlResult = await this.executeClaudeTool('get_current_url');
                if (urlResult && urlResult.success) {
                    this.addSystemMessage(`✅ get_current_url test passed: ${urlResult.url}`);
                } else {
                    this.addSystemMessage('❌ get_current_url test failed');
                }
            } catch (error) {
                this.addSystemMessage(`❌ get_current_url test error: ${error.message}`);
            }
            
            // Тест 3: Тестирование get_page_title
            try {
                const titleResult = await this.executeClaudeTool('get_page_title');
                if (titleResult && titleResult.success) {
                    this.addSystemMessage(`✅ get_page_title test passed: ${titleResult.title}`);
                } else {
                    this.addSystemMessage('❌ get_page_title test failed');
                }
            } catch (error) {
                this.addSystemMessage(`❌ get_page_title test error: ${error.message}`);
            }
            
            // Тест 4: Тестирование simple JavaScript
            try {
                const jsResult = await this.executeClaudeTool('execute_javascript', {
                    script: 'document.title'
                });
                if (jsResult) {
                    this.addSystemMessage(`✅ execute_javascript test initiated`);
                } else {
                    this.addSystemMessage('❌ execute_javascript test failed');
                }
            } catch (error) {
                this.addSystemMessage(`❌ execute_javascript test error: ${error.message}`);
            }
            
            this.addSystemMessage('🧪 Claude tools testing completed. Check results above.');
            
            return {
                tools_available: !!toolsList,
                test_completed: true
            };
            
        } catch (error) {
            console.error('Error testing Claude tools:', error);
            this.addSystemMessage(`❌ Error testing Claude tools: ${error.message}`);
            return null;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.gopiaiChat = new GopiAIChatInterface();
    // Создаем глобальную ссылку для Python bridge
    window.chat = window.gopiaiChat;
    console.log('GopiAI Chat Interface initialized');
});