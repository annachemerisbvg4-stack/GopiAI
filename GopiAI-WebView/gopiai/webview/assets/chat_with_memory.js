// JavaScript для GopiAI WebView Chat с интеграцией памяти

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
        this.settingsButton = document.getElementById('settings-btn');
        
        // Модальные окна
        this.settingsModal = document.getElementById('settings-modal');
        this.exportModal = document.getElementById('export-modal');
        
        // Элементы настроек
        this.streamToggle = document.getElementById('stream-toggle');
        this.autoScrollToggle = document.getElementById('auto-scroll-toggle');
        this.themeSelect = document.getElementById('theme-select');
        
        // Элементы экспорта
        this.exportFormatSelect = document.getElementById('export-format');
        this.downloadButton = document.getElementById('download-btn');
        this.copyButton = document.getElementById('copy-btn');
        this.exportContent = document.getElementById('export-content');
    }
    
    async initializeWebChannel() {
        if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined') {
            try {
                await new Promise((resolve) => {
                    new QWebChannel(qt.webChannelTransport, (channel) => {
                        this.bridge = channel.objects.bridge;
                        console.log('✅ WebChannel bridge connected');
                        
                        // Проверяем доступность системы памяти
                        this.checkMemoryAvailability();
                        
                        resolve();
                    });
                });
            } catch (error) {
                console.error('❌ Error initializing WebChannel:', error);
            }
        } else {
            console.warn('⚠️ QWebChannel not available');
        }
    }
    
    async checkMemoryAvailability() {
        if (this.bridge && typeof this.bridge.is_memory_available === 'function') {
            try {
                this.memoryEnabled = await this.bridge.is_memory_available();
                console.log(`${this.memoryEnabled ? '🧠' : '⚠️'} Memory system: ${this.memoryEnabled ? 'Available' : 'Not available'}`);
                
                if (this.memoryEnabled) {
                    this.addSystemMessage('🧠 AI память активирована - я буду помнить наши разговоры!');
                    
                    // Получаем статистику памяти
                    const stats = await this.getMemoryStats();
                    if (stats && stats.total_conversations) {
                        this.addSystemMessage(`📊 В памяти: ${stats.total_conversations} разговоров, ${stats.total_messages} сообщений`);
                    }
                }
            } catch (error) {
                console.error('Error checking memory availability:', error);
                this.memoryEnabled = false;
            }
        }
    }
    
    async getMemoryStats() {
        if (this.bridge && typeof this.bridge.get_memory_stats === 'function') {
            try {
                const statsJson = await this.bridge.get_memory_stats();
                return JSON.parse(statsJson);
            } catch (error) {
                console.error('Error getting memory stats:', error);
                return null;
            }
        }
        return null;
    }
    
    setupEventListeners() {
        // Отправка сообщения
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Обработка Enter в текстовом поле
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
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
        this.setupModalListeners();
        
        // Автоматическое изменение размера textarea
        this.messageInput.addEventListener('input', () => this.adjustTextareaHeight());
    }
    
    setupModalListeners() {
        // Закрытие модальных окон
        document.getElementById('close-settings').addEventListener('click', () => {
            this.settingsModal.style.display = 'none';
        });
        
        document.getElementById('close-export').addEventListener('click', () => {
            this.exportModal.style.display = 'none';
        });
        
        // Настройки
        this.streamToggle.addEventListener('change', (e) => {
            this.isStreaming = e.target.checked;
            this.saveSettings();
        });
        
        this.autoScrollToggle.addEventListener('change', (e) => {
            this.autoScroll = e.target.checked;
            this.saveSettings();
        });
        
        this.themeSelect.addEventListener('change', (e) => {
            this.theme = e.target.value;
            this.applyTheme();
            this.saveSettings();
        });
        
        // Экспорт
        this.exportFormatSelect.addEventListener('change', () => this.updateExportPreview());
        this.downloadButton.addEventListener('click', () => this.downloadChat());
        this.copyButton.addEventListener('click', () => this.copyToClipboard());
        
        // Закрытие модальных окон по клику вне них
        window.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.settingsModal.style.display = 'none';
            }
            if (e.target === this.exportModal) {
                this.exportModal.style.display = 'none';
            }
        });
    }
    
    async initializePuter() {
        try {
            await waitForPuter();
            console.log('✅ Puter.js loaded successfully');
        } catch (error) {
            console.error('❌ Failed to load puter.js:', error);
            this.addSystemMessage('⚠️ Error: Failed to load puter.js. Please check your internet connection.');
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Очищаем поле ввода
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        
        // Добавляем сообщение пользователя
        this.addUserMessage(message);
        
        // Показываем индикатор набора
        this.showTypingIndicator();
        
        try {
            // 🧠 НОВОЕ: Обогащение сообщения контекстом из памяти
            let enrichedMessage = message;
            if (this.memoryEnabled && this.bridge && typeof this.bridge.enrich_message === 'function') {
                try {
                    enrichedMessage = await this.bridge.enrich_message(message);
                    console.log('🧠 Message enriched with memory context');
                } catch (error) {
                    console.error('Memory enrichment failed:', error);
                    // Продолжаем с исходным сообщением
                }
            }
            
            // Уведомляем Python о сообщении пользователя
            if (this.bridge && typeof this.bridge.send_message === 'function') {
                await this.bridge.send_message(message);
            }
            
            // Отправляем обогащенное сообщение к ИИ
            const response = await puter.ai.chat(enrichedMessage, {
                model: this.currentModel,
                stream: this.isStreaming
            });
            
            this.hideTypingIndicator();
            
            if (this.isStreaming) {
                await this.handleStreamingResponse(response);
            } else {
                await this.handleSimpleResponse(response);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            console.error('❌ Error sending message:', error);
            this.addSystemMessage(`❌ Error: ${error.message}`);
            
            // Логируем ошибку в Python
            if (this.bridge && typeof this.bridge.log_error === 'function') {
                await this.bridge.log_error(error.message);
            }
        }
    }
    
    async handleStreamingResponse(response) {
        const messageElement = this.addAIMessage('', true);
        let fullResponse = '';
        
        try {
            for await (const part of response) {
                if (part?.text) {
                    fullResponse += part.text;
                    this.updateMessage(messageElement, fullResponse);
                }
            }
            
            // Завершаем стриминг
            messageElement.classList.remove('streaming');
            
            // 🧠 НОВОЕ: Сохраняем обмен в память
            await this.saveToMemory(this.getLastUserMessage(), fullResponse);
            
            // Уведомляем Python о полном ответе
            if (this.bridge && typeof this.bridge.receive_ai_message === 'function') {
                await this.bridge.receive_ai_message(this.currentModel, fullResponse);
            }
            
        } catch (error) {
            console.error('Streaming error:', error);
            this.updateMessage(messageElement, `❌ Streaming error: ${error.message}`);
            messageElement.classList.remove('streaming');
        }
    }
    
    async handleSimpleResponse(response) {
        try {
            const content = response.message?.content?.[0]?.text || response.text || 'No response';
            this.addAIMessage(content);
            
            // 🧠 НОВОЕ: Сохраняем обмен в память
            await this.saveToMemory(this.getLastUserMessage(), content);
            
            // Уведомляем Python
            if (this.bridge && typeof this.bridge.receive_ai_message === 'function') {
                await this.bridge.receive_ai_message(this.currentModel, content);
            }
            
        } catch (error) {
            console.error('Response handling error:', error);
            this.addSystemMessage(`❌ Response error: ${error.message}`);
        }
    }
    
    // 🧠 НОВЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С ПАМЯТЬЮ
    
    async saveToMemory(userMessage, aiResponse) {
        if (this.memoryEnabled && this.bridge && typeof this.bridge.save_chat_exchange === 'function') {
            try {
                const result = await this.bridge.save_chat_exchange(userMessage, aiResponse);
                if (result === 'OK') {
                    console.log('🧠 Chat exchange saved to memory');
                } else {
                    console.warn('⚠️ Failed to save to memory:', result);
                }
            } catch (error) {
                console.error('Memory save error:', error);
            }
        }
    }
    
    async startNewMemorySession() {
        if (this.memoryEnabled && this.bridge && typeof this.bridge.start_new_chat_session === 'function') {
            try {
                const sessionId = await this.bridge.start_new_chat_session();
                console.log('🧠 New memory session started:', sessionId);
                this.addSystemMessage('🔄 Новая сессия памяти начата');
            } catch (error) {
                console.error('Failed to start new memory session:', error);
            }
        }
    }
    
    getLastUserMessage() {
        // Ищем последнее сообщение пользователя
        const messages = this.messagesContainer.querySelectorAll('.user-message');
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            return lastMessage.querySelector('.message-content').textContent;
        }
        return '';
    }
    
    // БАЗОВЫЕ МЕТОДЫ ИНТЕРФЕЙСА
    
    addUserMessage(message) {
        const messageDiv = this.createMessageElement('user', message);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }
    
    addAIMessage(message, isStreaming = false) {
        const messageDiv = this.createMessageElement('ai', message, isStreaming);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }
    
    addSystemMessage(message) {
        const messageDiv = this.createMessageElement('system', message);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }
    
    createMessageElement(type, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message${isStreaming ? ' streaming' : ''}`;
        
        const timestamp = new Date().toLocaleTimeString();
        let senderLabel = '';
        let modelBadge = '';
        
        if (type === 'user') {
            senderLabel = '👤 You';
        } else if (type === 'ai') {
            senderLabel = '🤖 Assistant';
            modelBadge = `<span class="model-badge">${this.currentModel}</span>`;
        } else if (type === 'system') {
            senderLabel = '⚙️ System';
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="sender">${senderLabel}</span>
                ${modelBadge}
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${this.formatMessage(content)}</div>
        `;
        
        return messageDiv;
    }
    
    updateMessage(messageElement, content) {
        const contentElement = messageElement.querySelector('.message-content');
        contentElement.innerHTML = this.formatMessage(content);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Простое форматирование текста
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        if (this.autoScroll) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    async changeModel(model) {
        this.currentModel = model;
        this.addSystemMessage(`🔄 Model changed to ${model}`);
        
        // Уведомляем Python
        if (this.bridge && typeof this.bridge.change_model === 'function') {
            await this.bridge.change_model(model);
        }
    }
    
    async clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Очищаем интерфейс
            const messages = this.messagesContainer.querySelectorAll('.message:not(.welcome-message .ai-message)');
            messages.forEach(msg => msg.remove());
            
            // 🧠 НОВОЕ: Начинаем новую сессию памяти
            await this.startNewMemorySession();
            
            // Уведомляем Python
            if (this.bridge && typeof this.bridge.clear_chat === 'function') {
                await this.bridge.clear_chat();
            }
            
            this.addSystemMessage('🗑️ Chat cleared');
        }
    }
    
    // МОДАЛЬНЫЕ ОКНА И НАСТРОЙКИ
    
    showSettingsModal() {
        this.settingsModal.style.display = 'flex';
    }
    
    showExportModal() {
        this.exportModal.style.display = 'flex';
        this.updateExportPreview();
    }
    
    async updateExportPreview() {
        const format = this.exportFormatSelect.value;
        let content = '';
        
        if (this.bridge && typeof this.bridge.get_chat_history_json === 'function') {
            try {
                const historyJson = await this.bridge.get_chat_history_json();
                const history = JSON.parse(historyJson);
                
                if (format === 'json') {
                    content = JSON.stringify(history, null, 2);
                } else if (format === 'txt') {
                    content = this.formatHistoryAsText(history);
                } else if (format === 'md') {
                    content = this.formatHistoryAsMarkdown(history);
                }
            } catch (error) {
                content = 'Error generating preview: ' + error.message;
            }
        } else {
            content = 'Export not available - WebChannel not connected';
        }
        
        this.exportContent.textContent = content;
    }
    
    formatHistoryAsText(history) {
        return history.map(msg => {
            const role = msg.role === 'user' ? 'User' : `AI (${msg.model})`;
            return `[${msg.timestamp}] ${role}: ${msg.content}`;
        }).join('\\n\\n');
    }
    
    formatHistoryAsMarkdown(history) {
        let md = '# Chat History\\n\\n';
        history.forEach(msg => {
            const role = msg.role === 'user' ? '**User**' : `**AI (${msg.model})**`;
            md += `## ${role} - ${msg.timestamp}\\n\\n${msg.content}\\n\\n`;
        });
        return md;
    }
    
    async downloadChat() {
        const format = this.exportFormatSelect.value;
        const content = this.exportContent.textContent;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gopiai-chat-${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    async copyToClipboard() {
        try {
            await navigator.clipboard.writeText(this.exportContent.textContent);
            alert('Chat history copied to clipboard!');
        } catch (error) {
            console.error('Failed to copy:', error);
            alert('Failed to copy to clipboard');
        }
    }
    
    saveSettings() {
        const settings = {
            isStreaming: this.isStreaming,
            autoScroll: this.autoScroll,
            theme: this.theme,
            currentModel: this.currentModel
        };
        localStorage.setItem('gopiai-chat-settings', JSON.stringify(settings));
    }
    
    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('gopiai-chat-settings') || '{}');
            
            this.isStreaming = settings.isStreaming !== undefined ? settings.isStreaming : true;
            this.autoScroll = settings.autoScroll !== undefined ? settings.autoScroll : true;
            this.theme = settings.theme || 'dark';
            this.currentModel = settings.currentModel || 'claude-sonnet-4';
            
            // Применяем настройки к элементам
            this.streamToggle.checked = this.isStreaming;
            this.autoScrollToggle.checked = this.autoScroll;
            this.themeSelect.value = this.theme;
            this.modelSelect.value = this.currentModel;
            
            this.applyTheme();
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    applyTheme() {
        document.body.setAttribute('data-theme', this.theme);
    }
}

// Инициализация интерфейса
let chatInterface;

document.addEventListener('DOMContentLoaded', () => {
    chatInterface = new GopiAIChatInterface();
    
    // Экспорт для глобального использования
    window.gopiaiChat = chatInterface;
    
    console.log('🚀 GopiAI Chat Interface initialized');
});