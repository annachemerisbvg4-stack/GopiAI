// Исправленная версия без лишних усложнений

class GopiAIChatInterface {
    constructor() {
        this.bridge = null;
        this.currentModel = 'claude-sonnet-4';
        this.chatHistory = [];
        this.isProcessing = false;

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        this.initializeElements();
        this.initializeWebChannel();
        this.setupEventListeners();
        this.loadSettings();

        this.addAIMessage('Welcome to GopiAI Chat! Send a message to start chatting with Claude AI.');
    }

    initializeElements() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-btn');
        this.modelSelect = document.getElementById('model-select');
        this.typingIndicator = document.getElementById('typing-indicator');

        if (!this.messagesContainer || !this.messageInput || !this.sendButton) {
            console.error('Required elements not found');
            return;
        }
    }

    initializeWebChannel() {
        if (typeof qt !== 'undefined' && qt.webChannelTransport) {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                this.bridge = channel.objects.bridge;
                console.log('✅ WebChannel bridge initialized');
            });
        }
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());

        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        if (this.modelSelect) {
            this.modelSelect.addEventListener('change', (e) => {
                this.currentModel = e.target.value;
                console.log('Model changed to:', this.currentModel);
            });
        }

        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
    }

    loadSettings() {
        const savedModel = localStorage.getItem('gopiai_model');
        if (savedModel && this.modelSelect) {
            this.modelSelect.value = savedModel;
            this.currentModel = savedModel;
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isProcessing) return;

        if (typeof puter === 'undefined') {
            this.addSystemMessage('❌ Puter.js is not loaded. Please refresh the page.');
            return;
        }

        this.isProcessing = true;
        this.sendButton.disabled = true;

        try {
            this.addUserMessage(message);
            this.messageInput.value = '';
            this.messageInput.style.height = 'auto';

            this.showTypingIndicator();

            // Простое обогащение через память (если доступна)
            let enrichedMessage = message;
            if (this.bridge && typeof this.bridge.enrich_message === 'function') {
                try {
                    const enrichResult = this.bridge.enrich_message(message);
                    // Проверяем, что получили строку
                    if (typeof enrichResult === 'string' && enrichResult.trim() !== '') {
                        enrichedMessage = enrichResult;
                        console.log('💾 Memory enriched message');
                    }
                } catch (e) {
                    console.warn('Memory enrichment failed:', e);
                }
            }

            const messages = [...this.chatHistory];
            messages.push({ role: 'user', content: enrichedMessage });

            console.log('Sending to puter.ai.chat:', messages);

            const response = await puter.ai.chat(messages, { model: this.currentModel });

            this.hideTypingIndicator();

            // Обработка ответа
            let aiMessage = '';

            if (response && response.message && response.message.content &&
                Array.isArray(response.message.content) &&
                response.message.content[0] &&
                response.message.content[0].text) {
                aiMessage = response.message.content[0].text;
            } else if (response && response.message && typeof response.message === 'string') {
                aiMessage = response.message;
            } else if (response && response.content && Array.isArray(response.content) &&
                response.content[0] && response.content[0].text) {
                aiMessage = response.content[0].text;
            } else if (response && response.text) {
                aiMessage = response.text;
            } else if (typeof response === 'string') {
                aiMessage = response;
            } else {
                console.error('Unexpected response structure:', response);
                aiMessage = 'Sorry, I received an unexpected response format.';
            }

            if (!aiMessage || aiMessage.trim() === '') {
                aiMessage = 'Sorry, I received an empty response from the AI service.';
            }

            this.addAIMessage(aiMessage);

            // Простое сохранение в память
            if (this.bridge && typeof this.bridge.save_chat_exchange === 'function') {
                try {
                    this.bridge.save_chat_exchange(message, aiMessage);
                    console.log('💾 Saved to memory');
                } catch (e) {
                    console.warn('Memory save failed:', e);
                }
            }

            // Локальная история
            this.chatHistory.push({ role: 'user', content: message });
            this.chatHistory.push({ role: 'assistant', content: aiMessage });

            localStorage.setItem('gopiai_model', this.currentModel);

        } catch (error) {
            this.hideTypingIndicator();
            console.error('Error sending message:', error);

            // Безопасная обработка ошибки
            let errorMessage = 'Sorry, I encountered an error while processing your message.';
            try {
                const errorMsg = (error && error.message) ? error.message : String(error);

                if (errorMsg.includes && errorMsg.includes('Authentication') || errorMsg.includes && errorMsg.includes('sign')) {
                    errorMessage = '🔐 Please sign in to Puter to use AI chat. The sign-in popup should appear automatically.';
                } else if (errorMsg.includes && errorMsg.includes('network') || errorMsg.includes && errorMsg.includes('fetch')) {
                    errorMessage = '🌐 Network error. Please check your internet connection.';
                } else if (errorMsg.includes && (errorMsg.includes('context') || errorMsg.includes('token'))) {
                    errorMessage = '📏 Context window may be full. Try starting a new conversation.';
                } else {
                    errorMessage = `❌ Error: ${errorMsg}`;
                }
            } catch (e) {
                console.error('Error processing error message:', e);
                errorMessage = '❌ An unexpected error occurred.';
            }

            this.addSystemMessage(errorMessage);

        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }

    addUserMessage(message) {
        const messageElement = this.createMessageElement('user', message);
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addAIMessage(message) {
        const messageElement = this.createMessageElement('assistant', message);
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const messageElement = this.createMessageElement('system', message);
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    createMessageElement(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${role}-message`);

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');

        if (role === 'system') {
            messageContent.innerHTML = content;
        } else {
            messageContent.textContent = content;
        }

        const messageTime = document.createElement('div');
        messageTime.classList.add('message-time');
        messageTime.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);

        return messageDiv;
    }

    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
}

// Инициализация
let chatInterface;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatInterface = new GopiAIChatInterface();
    });
} else {
    chatInterface = new GopiAIChatInterface();
}

// Инициализация AI Recovery модуля
if (window.AIRecoveryModule && chatInterface) {
    const recovery = new AIRecoveryModule(chatInterface, {
        timeoutSeconds: 45,
        maxRetries: 2,
        showNotifications: true
    });
    recovery.activate();
}