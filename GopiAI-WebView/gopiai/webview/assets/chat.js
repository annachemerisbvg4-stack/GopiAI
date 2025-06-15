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
}

document.addEventListener('DOMContentLoaded', () => {
    window.gopiaiChat = new GopiAIChatInterface();
    console.log('GopiAI Chat Interface initialized');
});