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
        this.closeHistoryBtn = document.getElementById('close-settings'); // Переиспользуем тот же ID
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
                        if (Array.isArray(Object.values(toolsList.tools))) {
                            tools = Object.values(toolsList.tools);
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.gopiaiChat = new GopiAIChatInterface();
    // Создаем глобальную ссылку для Python bridge
    window.chat = window.gopiaiChat;
    console.log('GopiAI Chat Interface initialized');
});