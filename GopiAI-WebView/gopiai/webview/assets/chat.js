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
        this.memoryEnabled = false; // Флаг доступности памяти

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
        this.historyButton = document.getElementById('history-btn');

        // Модальные окна
        this.historyModal = document.getElementById('history-modal');
        this.exportModal = document.getElementById('export-modal');
        this.closeHistoryBtn = document.getElementById('close-history'); // Исправлено
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

    async checkMemoryAvailability() {
        try {
            if (!this.bridge) {
                console.log('Bridge not available for memory check');
                return false;
            }

            if (typeof this.bridge.execute_claude_tool === 'function') {
                const toolsList = await this.getClaudeToolsList(true);
                console.log('Tools list received for memory check:', toolsList);

                if (toolsList && toolsList.success) {
                    // Проверяем разные возможные структуры ответа
                    let tools = null;

                    if (Array.isArray(toolsList.tools)) {
                        tools = toolsList.tools;
                        console.log('Found tools array in toolsList.tools');
                    } else if (Array.isArray(toolsList.result)) {
                        tools = toolsList.result;
                        console.log('Found tools array in toolsList.result');
                    } else if (Array.isArray(toolsList.data)) {
                        tools = toolsList.data;
                        console.log('Found tools array in toolsList.data');
                    } else if (Array.isArray(toolsList)) {
                        tools = toolsList;
                        console.log('toolsList itself is an array');
                    } else if (toolsList.tools && typeof toolsList.tools === 'object') {
                        // Если tools - это объект, пытаемся найти массив внутри
                        if (Array.isArray(Object.values(toolsList.tools)[0])) {
                            tools = Object.values(toolsList.tools)[0]; // Исправлено
                            console.log('Converted tools object to array');
                        } else {
                            // Возможно, это объект с ключами-именами инструментов
                            tools = Object.keys(toolsList.tools).map(key => ({
                                name: key,
                                ...toolsList.tools[key]
                            }));
                            console.log('Created tools array from object keys');
                        }
                    } else {
                        console.log('Could not extract tools array from response structure:', Object.keys(toolsList));

                        // Последняя попытка - поиск любого свойства, которое содержит массив
                        for (const [key, value] of Object.entries(toolsList)) {
                            if (Array.isArray(value) && value.length > 0) {
                                tools = value;
                                console.log(`Found tools array in toolsList.${key}`);
                                break;
                            }
                        }
                    }

                    console.log('Final parsed tools array:', tools);

                    if (Array.isArray(tools) && tools.length > 0) {
                        const memoryTool = tools.find(t => {
                            // Проверяем разные возможные структуры элемента tool
                            const name = t?.name || t?.tool_name || t?.id || t?.function_name || String(t);
                            return name === 'search_memory';
                        });

                        this.memoryEnabled = !!memoryTool;
                        console.log('Memory tool search result:', memoryTool);
                        console.log('Memory availability set to:', this.memoryEnabled);

                        if (this.memoryEnabled) {
                            console.log('🧠 Memory system is available');
                        } else {
                            console.log('⚠️ search_memory tool not found in tools list');
                        }

                        return this.memoryEnabled;
                    } else {
                        console.log('No valid tools array found. Tools value:', tools, 'Type:', typeof tools);
                    }
                } else {
                    console.log('Invalid toolsList response:', toolsList);
                }
            } else {
                console.log('execute_claude_tool method not available in bridge');
            }

            this.memoryEnabled = false;
            console.log('Memory availability set to false (fallback)');
            return false;
        } catch (error) {
            console.error('Error checking memory availability:', error);
            this.memoryEnabled = false;
            return false;
        }
    }

    async searchMemory(query, limit = 10) {
        try {
            if (!this.memoryEnabled) {
                console.log('Memory not available');
                return null;
            }

            const result = await this.executeClaudeTool('search_memory', {
                query: query,
                limit: limit
            });

            if (result && result.success) {
                return result.results || [];
            }

            return [];
        } catch (error) {
            console.error('Error searching memory:', error);
            return [];
        }
    }

    async executeClaudeTool(toolName, parameters) {
        try {
            if (!this.bridge || typeof this.bridge.execute_claude_tool !== 'function') {
                console.error('Bridge or execute_claude_tool method not available');
                return { success: false, error: 'Bridge not available' };
            }

            const result = await this.bridge.execute_claude_tool(toolName, parameters);
            return result;
        } catch (error) {
            console.error('Error executing Claude tool:', error);
            return { success: false, error: error.message };
        }
    }

    async loadChatHistory() {
        try {
            if (!this.memoryEnabled) {
                console.log('Memory not available for history');
                return [];
            }

            const result = await this.searchMemory('', 50);

            if (result && Array.isArray(result)) {
                const sessionMap = new Map();

                result.forEach(item => {
                    if (item.metadata && item.metadata.session_id) {
                        const sessionId = item.metadata.session_id;
                        if (!sessionMap.has(sessionId)) {
                            sessionMap.set(sessionId, {
                                session_id: sessionId,
                                timestamp: item.metadata.timestamp || new Date().toISOString(),
                                messages: []
                            });
                        }
                        sessionMap.get(sessionId).messages.push(item);
                    }
                });

                const sessions = Array.from(sessionMap.values());
                sessions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

                return sessions;
            }

            return [];
        } catch (error) {
            console.error('Error loading chat history:', error);
            return [];
        }
    }

    async displayChatHistory() {
        try {
            const historyContainer = document.getElementById('history-list');
            if (!historyContainer) {
                console.error('History container not found');
                return;
            }

            historyContainer.innerHTML = '<div class="loading">📚 Загрузка истории чатов...</div>';

            const sessions = await this.loadChatHistory();

            if (!sessions || sessions.length === 0) {
                historyContainer.innerHTML = '<div class="no-history">📝 История чатов пуста</div>';
                return;
            }

            const dateGroups = new Map();
            sessions.forEach(session => {
                const date = new Date(session.timestamp).toDateString();
                if (!dateGroups.has(date)) {
                    dateGroups.set(date, []);
                }
                dateGroups.get(date).push(session);
            });

            let html = '';
            for (const [date, dateSessions] of dateGroups) {
                html += '<div class="history-date-group"><h3 class="history-date">' + date + '</h3>';

                dateSessions.forEach(session => {
                    const firstMessage = session.messages[0];
                    const preview = firstMessage ?
                        (firstMessage.content || firstMessage.text || 'Пустое сообщение').substring(0, 100) + '...' :
                        'Нет сообщений';

                    html += '<div class="history-session" data-session-id="' + session.session_id + '">';
                    html += '<div class="history-session-header">';
                    html += '<span class="history-session-time">' + new Date(session.timestamp).toLocaleTimeString() + '</span>';
                    html += '<span class="history-session-count">' + session.messages.length + ' сообщений</span>';
                    html += '</div>';
                    html += '<div class="history-session-preview">' + preview + '</div>';
                    html += '</div>';
                });

                html += '</div>';
            }

            historyContainer.innerHTML = html;

            historyContainer.querySelectorAll('.history-session').forEach(sessionEl => {
                sessionEl.addEventListener('click', (e) => {
                    const sessionId = e.currentTarget.dataset.sessionId;
                    this.loadChatSession(sessionId);
                });
            });

        } catch (error) {
            console.error('Error displaying chat history:', error);
            const historyContainer = document.getElementById('history-list');
            if (historyContainer) {
                historyContainer.innerHTML = '<div class="error">❌ Ошибка загрузки истории</div>';
            }
        }
    }

    async searchChatHistory(query) {
        try {
            if (!query || query.trim() === '') {
                await this.displayChatHistory();
                return;
            }

            const historyContainer = document.getElementById('history-list');
            if (!historyContainer) return;

            historyContainer.innerHTML = '<div class="loading">🔍 Поиск в истории...</div>';

            const results = await this.searchMemory(query, 20);

            if (!results || results.length === 0) {
                historyContainer.innerHTML = '<div class="no-results">🔍 Результаты не найдены</div>';
                return;
            }

            let html = '<div class="search-results-header">🔍 Результаты поиска:</div>';

            results.forEach((result, index) => {
                const relevance = Math.round((result.score || 0) * 100);
                const content = result.content || result.text || 'Нет содержимого';
                const timestamp = result.metadata && result.metadata.timestamp ?
                    new Date(result.metadata.timestamp).toLocaleString() :
                    'Неизвестно';

                const highlightedContent = this.highlightSearchTerms(content, query);

                html += '<div class="search-result">';
                html += '<div class="search-result-header">';
                html += '<span class="search-result-time">' + timestamp + '</span>';
                html += '<span class="search-result-relevance">Релевантность: ' + relevance + '%</span>';
                html += '</div>';
                html += '<div class="search-result-content">' + highlightedContent + '</div>';
                html += '</div>';
            });

            historyContainer.innerHTML = html;

        } catch (error) {
            console.error('Error searching chat history:', error);
            const historyContainer = document.getElementById('history-list');
            if (historyContainer) {
                historyContainer.innerHTML = '<div class="error">❌ Ошибка поиска</div>';
            }
        }
    }

    highlightSearchTerms(content, query) {
        if (!query || query.trim() === '') return content;

        const terms = query.toLowerCase().split(/\s+/);
        let highlighted = content;

        terms.forEach(term => {
            if (term.length > 2) {
                const regex = new RegExp('(' + term + ')', 'gi');
                highlighted = highlighted.replace(regex, '<mark>$1</mark>');
            }
        });

        return highlighted;
    }

    async loadChatSession(sessionId) {
        try {
            console.log('Loading chat session:', sessionId);
            const modal = document.getElementById('history-modal');
            if (modal) {
                modal.style.display = 'none';
            }

            this.addSystemMessage('📂 Загружена сессия: ' + sessionId);

        } catch (error) {
            console.error('Error loading chat session:', error);
        }
    }

    async exportChatHistory(format = 'txt') {
        try {
            const sessions = await this.loadChatHistory();

            if (!sessions || sessions.length === 0) {
                this.addSystemMessage('📝 История чатов пуста');
                return;
            }

            let content = '';
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');

            if (format === 'md') {
                content = '# История чатов GopiAI\n\n';
                content += 'Экспортировано: ' + new Date().toLocaleString() + '\n\n';

                sessions.forEach(session => {
                    content += '## Сессия ' + session.session_id + '\n';
                    content += '**Время:** ' + new Date(session.timestamp).toLocaleString() + '\n';
                    content += '**Сообщений:** ' + session.messages.length + '\n\n';

                    session.messages.forEach(msg => {
                        const msgContent = msg.content || msg.text || 'Пустое сообщение';
                        content += '### Сообщение\n' + msgContent + '\n\n';
                    });

                    content += '---\n\n';
                });
            } else {
                content = 'История чатов GopiAI\n';
                content += '='.repeat(50) + '\n\n';
                content += 'Экспортировано: ' + new Date().toLocaleString() + '\n\n';

                sessions.forEach(session => {
                    content += 'Сессия: ' + session.session_id + '\n';
                    content += 'Время: ' + new Date(session.timestamp).toLocaleString() + '\n';
                    content += 'Сообщений: ' + session.messages.length + '\n';
                    content += '-'.repeat(30) + '\n';

                    session.messages.forEach(msg => {
                        const msgContent = msg.content || msg.text || 'Пустое сообщение';
                        content += msgContent + '\n\n';
                    });

                    content += '='.repeat(50) + '\n\n';
                });
            }

            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'gopiai_chat_history_' + timestamp + '.' + format;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.addSystemMessage('📥 История экспортирована в ' + format.toUpperCase());

        } catch (error) {
            console.error('Error exporting chat history:', error);
            this.addSystemMessage('❌ Ошибка экспорта истории');
        }
    }

    // Метод для получения списка Claude Tools
    async getClaudeToolsList(silent = false) {
        try {
            if (!this.bridge || typeof this.bridge.get_claude_tools_list !== 'function') {
                if (!silent) {
                    console.warn('⚠️ bridge.get_claude_tools_list method not available');
                }
                return { success: false, tools: [], error: 'Method not available' };
            }

            const result = await this.bridge.get_claude_tools_list();

            if (!silent) {
                console.log('🔧 Claude tools list received:', result);
            }

            // Обрабатываем разные возможные структуры ответа
            if (typeof result === 'string') {
                try {
                    const parsed = JSON.parse(result);
                    return { success: true, tools: parsed.tools || parsed.result || parsed || [] };
                } catch (e) {
                    if (!silent) {
                        console.warn('⚠️ Failed to parse tools list JSON:', e);
                    }
                    return { success: false, tools: [], error: 'JSON parse error' };
                }
            }

            if (result && typeof result === 'object') {
                return {
                    success: true,
                    tools: result.tools || result.result || result.data || (Array.isArray(result) ? result : [])
                };
            }

            return { success: false, tools: [], error: 'Invalid response format' };

        } catch (error) {
            if (!silent) {
                console.error('❌ Error getting Claude tools list:', error);
            }
            return { success: false, tools: [], error: error.message };
        }
    }

    setupEventListeners() {
        // Кнопка отправки
        this.sendButton?.addEventListener('click', () => this.sendMessage());

        // Поле ввода
        this.messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput?.addEventListener('input', () => this.autoResizeTextarea());

        // Кнопки заголовка
        this.historyButton?.addEventListener('click', () => this.showHistoryModal());
        this.exportButton?.addEventListener('click', () => this.showExportModal());

        // Модальное окно истории
        this.closeHistoryBtn?.addEventListener('click', () => this.hideHistoryModal());

        // Модальное окно экспорта
        this.closeExportBtn?.addEventListener('click', () => this.hideExportModal());

        // Кнопки в модальном окне истории
        document.getElementById('new-chat-btn')?.addEventListener('click', () => this.clearChat());
        document.getElementById('export-history-btn')?.addEventListener('click', () => this.exportCurrentChat());
        document.getElementById('history-search')?.addEventListener('input', (e) => this.searchChatHistory(e.target.value));

        // Кнопки экспорта
        this.downloadBtn?.addEventListener('click', () => this.downloadChatHistory());
        this.copyBtn?.addEventListener('click', () => this.copyChatHistory());

        // Закрытие модальных окон по клику вне них
        this.historyModal?.addEventListener('click', (e) => {
            if (e.target === this.historyModal) {
                this.hideHistoryModal();
            }
        });

        this.exportModal?.addEventListener('click', (e) => {
            if (e.target === this.exportModal) {
                this.hideExportModal();
            }
        });

        // Селектор модели
        this.modelSelect?.addEventListener('change', (e) => {
            this.currentModel = e.target.value;
            this.saveSettings();
        });
    }

    showHistoryModal() {
        if (this.historyModal) {
            this.historyModal.style.display = 'flex';
            this.displayChatHistory();
        }
    }

    hideHistoryModal() {
        if (this.historyModal) {
            this.historyModal.style.display = 'none';
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

    autoResizeTextarea() {
        if (this.messageInput) {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        }
    }

    updateExportPreview() {
        // Обновление превью экспорта
        const format = document.getElementById('export-format')?.value || 'json';
        const content = this.exportContent;

        if (content) {
            const exportData = this.formatChatHistory(format);
            content.textContent = exportData.substring(0, 500) + (exportData.length > 500 ? '...' : '');
        }
    }

    formatChatHistory(format) {
        const messages = this.chatHistory;

        switch (format) {
            case 'txt':
                return messages.map(msg => `${msg.sender}: ${msg.content}`).join('\n\n');
            case 'md':
                return messages.map(msg => `**${msg.sender}:**\n${msg.content}\n`).join('\n');
            case 'json':
            default:
                return JSON.stringify(messages, null, 2);
        }
    }

    downloadChatHistory() {
        const format = document.getElementById('export-format')?.value || 'json';
        const content = this.formatChatHistory(format);
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gopiai_chat_history_${timestamp}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.addSystemMessage(`📁 История экспортирована в ${format.toUpperCase()} формате`);
    }

    copyChatHistory() {
        const format = document.getElementById('export-format')?.value || 'json';
        const content = this.formatChatHistory(format);

        navigator.clipboard.writeText(content).then(() => {
            this.addSystemMessage('📋 История скопирована в буфер обмена');
        }).catch(error => {
            console.error('Error copying to clipboard:', error);
            this.addSystemMessage('❌ Ошибка копирования в буфер обмена');
        });
    }

    clearChat() {
        this.chatHistory = [];
        this.messagesContainer.innerHTML = '';
        this.hideHistoryModal();
        this.addSystemMessage('🧹 Чат очищен');
    }

    exportCurrentChat() {
        // Экспорт текущего чата в формате JSON
        const format = 'json';
        const content = this.formatChatHistory(format);
        
        if (this.chatHistory.length === 0) {
            this.addSystemMessage('📝 Текущий чат пуст');
            return;
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gopiai_current_chat_${timestamp}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.addSystemMessage(`📁 Текущий чат экспортирован`);
    }

    saveSettings() {
        const settings = {
            currentModel: this.currentModel,
            isStreaming: this.isStreaming,
            autoScroll: this.autoScroll,
            theme: this.theme
        };
        localStorage.setItem('gopiaiChatSettings', JSON.stringify(settings));
    }

    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('gopiaiChatSettings') || '{}');
            this.currentModel = settings.currentModel || 'claude-sonnet-4';
            this.isStreaming = settings.isStreaming !== false;
            this.autoScroll = settings.autoScroll !== false;
            this.theme = settings.theme || 'dark';

            // Применяем настройки к элементам
            if (this.modelSelect) {
                this.modelSelect.value = this.currentModel;
            }
        } catch (error) {
            console.warn('Failed to load settings:', error);
        }
    }

    async sendMessage() {
        const message = this.messageInput?.value.trim();
        if (!message) return;

        // Очистка поля ввода
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Добавление сообщения пользователя
        this.addUserMessage(message);

        // Показываем индикатор набора
        this.showTypingIndicator();

        let retryCount = 0;
        const maxRetries = 3;

        while (retryCount < maxRetries) {
            try {
                // Проверяем доступность puter.js
                if (typeof puter === 'undefined') {
                    throw new Error('puter.js is not available. Please check your internet connection and refresh the page.');
                }

                // Проверяем аутентификацию
                const isSignedIn = await this.checkAndEnsureAuth();
                if (!isSignedIn) {
                    throw new Error('Authentication failed. Please sign in to use the chat.');
                }

                console.log(`Sending message (attempt ${retryCount + 1}/${maxRetries}):`, message);

                // Отправляем сообщение через puter.js
                const response = await puter.ai.chat([
                    { role: 'user', content: message }
                ], {
                    model: this.currentModel,
                    stream: this.isStreaming
                });

                this.hideTypingIndicator();

                if (!response) {
                    throw new Error('Empty response from AI service');
                }

                const aiMessage = response.message || response.content || response.text || 'No response content';
                this.addAIMessage(aiMessage);

                // Сохраняем в историю
                this.chatHistory.push({
                    timestamp: new Date().toISOString(),
                    sender: 'User',
                    content: message
                });
                this.chatHistory.push({
                    timestamp: new Date().toISOString(),
                    sender: 'AI',
                    content: aiMessage,
                    model: this.currentModel
                });

                // Успешно отправлено - выходим из цикла
                return;

            } catch (error) {
                retryCount++;
                console.error(`Error sending message (attempt ${retryCount}/${maxRetries}):`, error);

                if (retryCount >= maxRetries) {
                    this.hideTypingIndicator();
                    this.handleSendMessageError(error, retryCount);
                    return;
                }

                // Ждем перед повтором
                await this.sleep(1000 * retryCount);
                console.log(`Retrying in ${1000 * retryCount}ms...`);
            }
        }
    }

    addUserMessage(message) {
        const messageDiv = this.createMessageElement('user', 'You', message);
        this.messagesContainer?.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAIMessage(message) {
        const messageDiv = this.createMessageElement('ai', '🤖 GopiAI Assistant', message, this.currentModel);
        this.messagesContainer?.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const messageDiv = this.createMessageElement('system', '🔧 System', message);
        this.messagesContainer?.appendChild(messageDiv);
        this.scrollToBottom();
    }

    createMessageElement(type, sender, content, model = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        // Заголовок сообщения
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';

        const senderSpan = document.createElement('span');
        senderSpan.className = 'sender';
        senderSpan.textContent = sender;
        headerDiv.appendChild(senderSpan);

        if (model) {
            const modelBadge = document.createElement('span');
            modelBadge.className = 'model-badge';
            modelBadge.textContent = model;
            headerDiv.appendChild(modelBadge);
        }

        // Содержимое сообщения
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        // Время сообщения
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();

        bubbleDiv.appendChild(headerDiv);
        bubbleDiv.appendChild(contentDiv);
        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);

        return messageDiv;
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
        if (this.autoScroll && this.messagesContainer) {
            setTimeout(() => {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }, 100);
        }
    }

    initializeWebChannel() {
        // Инициализация WebChannel для связи с Python
        if (typeof QWebChannel !== 'undefined') {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                this.bridge = channel.objects.bridge;
                console.log('✅ WebChannel bridge initialized');

                // Проверяем доступность памяти после инициализации моста
                this.checkMemoryAvailability().then(() => {
                    console.log('Memory availability check completed');
                });
            });
        } else {
            console.warn('⚠️ QWebChannel not available');
        }
    }

    async checkAndEnsureAuth() {
        try {
            // Проверяем текущий статус аутентификации
            if (typeof puter.isSignedIn === 'function') {
                const isSignedIn = await puter.isSignedIn();
                console.log('Auth status:', isSignedIn);
                
                if (!isSignedIn) {
                    console.log('User not signed in, attempting to sign in...');
                    this.addSystemMessage('🔐 Signing in to enable AI chat...');
                    
                    if (typeof puter.signIn === 'function') {
                        await puter.signIn();
                        return await puter.isSignedIn();
                    } else {
                        console.warn('puter.signIn method not available');
                        return false;
                    }
                }
                
                return true;
            } else {
                console.warn('puter.isSignedIn method not available, assuming signed in');
                return true; // Fallback - продолжаем работу
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            return true; // Fallback - продолжаем работу
        }
    }

    handleSendMessageError(error, retryCount) {
        let errorMessage = '❌ Failed to send message';
        let userMessage = 'An error occurred while sending your message.';

        // Определяем тип ошибки и даем соответствующее сообщение
        if (error.message.includes('puter.js is not available')) {
            errorMessage = '❌ Connection Error';
            userMessage = 'puter.js is not loaded. Please check your internet connection and refresh the page.';
        } else if (error.message.includes('Authentication failed')) {
            errorMessage = '❌ Authentication Error';
            userMessage = 'Authentication failed. Please try signing in again.';
        } else if (error.message.includes('Empty response')) {
            errorMessage = '❌ Empty Response';
            userMessage = 'Received empty response from AI service. Please try again.';
        } else if (error.message.includes('network') || error.message.includes('fetch')) {
            errorMessage = '❌ Network Error';
            userMessage = 'Network connection error. Please check your internet connection and try again.';
        } else if (error.message.includes('rate limit') || error.message.includes('quota')) {
            errorMessage = '❌ Rate Limit Error';
            userMessage = 'AI service rate limit reached. Please wait a moment and try again.';
        } else {
            errorMessage = '❌ Unknown Error';
            userMessage = `An unexpected error occurred: ${error.message}`;
        }

        console.error(`${errorMessage} after ${retryCount} attempts:`, error);
        this.addSystemMessage(`${errorMessage}: ${userMessage}`);

        // Добавляем кнопку повтора для пользователя
        this.addRetryButton();
    }

    addRetryButton() {
        const retryDiv = document.createElement('div');
        retryDiv.className = 'retry-container';
        retryDiv.innerHTML = `
            <button class="retry-btn" onclick="window.gopiaiChat.retryLastMessage()">
                🔄 Retry Last Message
            </button>
        `;
        this.messagesContainer?.appendChild(retryDiv);
        this.scrollToBottom();
    }

    retryLastMessage() {
        // Удаляем кнопку повтора
        const retryContainer = this.messagesContainer?.querySelector('.retry-container');
        if (retryContainer) {
            retryContainer.remove();
        }

        // Находим последнее сообщение пользователя
        const userMessages = this.messagesContainer?.querySelectorAll('.user-message');
        if (userMessages && userMessages.length > 0) {
            const lastUserMessage = userMessages[userMessages.length - 1];
            const messageContent = lastUserMessage.querySelector('.message-content')?.textContent;
            
            if (messageContent) {
                this.messageInput.value = messageContent;
                this.sendMessage();
            }
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.gopiaiChat = new GopiAIChatInterface();
    // Создаем глобальную ссылку для Python bridge
    window.chat = window.gopiaiChat;
    console.log('GopiAI Chat Interface initialized');
});