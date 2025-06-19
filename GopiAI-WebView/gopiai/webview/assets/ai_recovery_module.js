/**
 * AI Recovery Module - Автоматическое восстановление зависших ИИ сессий
 * Модуль подключается к существующему чату без изменения основного кода
 */

class AIRecoveryModule {
    constructor(chatInterface, options = {}) {
        this.chat = chatInterface;
        this.options = {
            enabled: true,
            timeoutSeconds: 45,
            maxRetries: 2,
            compressionLevel: 'smart',
            showNotifications: true,
            ...options
        };

        // Состояние модуля
        this.isMonitoring = false;
        this.lastRequestTime = null;
        this.retryCount = 0;
        this.originalSendMessage = null;

        // Флаги для предотвращения рекурсии
        this.isRecovering = false;
        this.isRetrying = false;

        console.log('🔄 AI Recovery Module initialized');
    }

    /**
     * Активация модуля - подключение к существующему чату
     */
    activate() {
        if (!this.chat) {
            console.error('❌ AI Recovery: No chat interface provided');
            return;
        }

        // Патчим существующий sendMessage методы
        this.patchChatInterface();

        // Запускаем мониторинг
        this.startHealthMonitoring();

        console.log('✅ AI Recovery Module activated');
    }

    /**
     * Патчинг существующего интерфейса чата
     */
    patchChatInterface() {
        // Сохраняем оригинальный метод
        this.originalSendMessage = this.chat.sendMessage.bind(this.chat);

        // Заменяем на наш wrapper
        this.chat.sendMessage = this.wrappedSendMessage.bind(this);

        // Добавляем наши методы в интерфейс чата
        this.chat._recoveryModule = this;
        this.chat.triggerRecovery = () => this.performRecovery();
    }

    /**
     * Обёртка для sendMessage с мониторингом
     */
    async wrappedSendMessage() {
        if (this.isRecovering || this.isRetrying) {
            return; // Избегаем рекурсии
        }

        this.lastRequestTime = Date.now();
        this.startTimeoutWatch();

        try {
            // Вызываем оригинальный метод
            const result = await this.originalSendMessage();
            this.onSuccessfulResponse();
            return result;

        } catch (error) {
            await this.handleSendError(error);
            throw error;
        }
    }

    /**
     * Запуск мониторинга таймаутов
     */
    startTimeoutWatch() {
        this.clearTimeoutWatch();

        this.timeoutWatcher = setTimeout(() => {
            if (this.chat.isProcessing && !this.isRecovering) {
                console.warn('🚨 AI Recovery: Response timeout detected');
                this.performRecovery();
            }
        }, this.options.timeoutSeconds * 1000);
    }

    clearTimeoutWatch() {
        if (this.timeoutWatcher) {
            clearTimeout(this.timeoutWatcher);
            this.timeoutWatcher = null;
        }
    }

    /**
     * Обработка успешного ответа
     */
    onSuccessfulResponse() {
        this.clearTimeoutWatch();
        this.retryCount = 0;
        this.lastRequestTime = null;
    }

    /**
     * Обработка ошибок отправки
     */
    async handleSendError(error) {
        this.clearTimeoutWatch();

        // Проверяем, нужно ли восстановление
        if (this.shouldTriggerRecovery(error)) {
            await this.performRecovery();
        }
    }

    /**
     * Определение, нужно ли восстановление
     */
    shouldTriggerRecovery(error) {
        if (!this.options.enabled || this.retryCount >= this.options.maxRetries) {
            return false;
        }

        const errorMessage = error?.message?.toLowerCase() || '';
        const recoveryTriggers = [
            'timeout',
            'failed to fetch',
            'network error',
            'connection',
            'context window',
            'rate limit'
        ];

        return recoveryTriggers.some(trigger => errorMessage.includes(trigger));
    }

    /**
     * Главный метод восстановления
     */
    async performRecovery() {
        if (this.isRecovering) {
            return; // Избегаем множественного восстановления
        }

        this.isRecovering = true;
        this.retryCount++;

        console.log(`🔄 AI Recovery: Starting recovery attempt ${this.retryCount}/${this.options.maxRetries}`);

        try {
            // 1. Показываем уведомление
            if (this.options.showNotifications) {
                this.showRecoveryNotification();
            }

            // 2. Останавливаем текущие операции
            this.stopCurrentOperations();

            // 3. Сжимаем контекст
            const compressedContext = this.compressContext();

            // 4. Выполняем тихое восстановление
            await this.silentRestore(compressedContext);

            // 5. Убираем уведомление
            if (this.options.showNotifications) {
                this.hideRecoveryNotification();
                this.showSuccessNotification();
            }

            console.log('✅ AI Recovery: Recovery completed successfully');

        } catch (error) {
            console.error('❌ AI Recovery: Recovery failed:', error);
            this.showFailureNotification();

        } finally {
            this.isRecovering = false;
        }
    }

    /**
     * Остановка текущих операций
     */
    stopCurrentOperations() {
        if (this.chat.hideTypingIndicator) {
            this.chat.hideTypingIndicator();
        }

        this.chat.isProcessing = false;

        if (this.chat.sendButton) {
            this.chat.sendButton.disabled = false;
        }

        this.clearTimeoutWatch();
    }

    /**
     * Сжатие контекста для восстановления
     */
    compressContext() {
        const history = this.chat.chatHistory || [];

        if (history.length === 0) {
            return null;
        }

        // Берем последние несколько сообщений
        const recentMessages = history.slice(-4);

        // Создаем краткое резюме
        const summary = this.createContextSummary(history.slice(0, -4));

        return {
            summary,
            recent: recentMessages,
            compressed: true
        };
    }

    /**
     * Создание краткого резюме контекста
     */
    createContextSummary(messages) {
        if (messages.length === 0) return "";

        // Простое извлечение ключевых тем
        const userMessages = messages.filter(m => m.role === 'user');
        const lastUserMessages = userMessages.slice(-3).map(m => m.content);

        if (lastUserMessages.length === 0) return "";

        return `Предыдущий контекст: обсуждали ${lastUserMessages.join(', ').substring(0, 200)}...`;
    }

    /**
     * Тихое восстановление сессии
     */
    async silentRestore(context) {
        if (!context) {
            return;
        }

        // Создаем специальное восстановительное сообщение
        const restorePrompt = this.createRestorePrompt(context);

        // Отправляем тихо (без UI обновлений)
        const tempHistory = [{ role: 'user', content: restorePrompt }];

        const response = await puter.ai.chat(tempHistory, {
            model: this.chat.currentModel
        });

        // Обновляем внутреннее состояние
        this.updateInternalState(context, response);
    }

    /**
     * Создание промпта для восстановления
     */
    createRestorePrompt(context) {
        return `[СИСТЕМА: Краткое восстановление сессии]
${context.summary}

Последний контекст:
${context.recent.map(msg =>
            `${msg.role === 'user' ? 'Пользователь' : 'Ассистент'}: ${msg.content.substring(0, 100)}...`
        ).join('\n')}

Подтвердите готовность продолжить беседу. Ответьте кратко "Готов продолжить".`;
    }

    /**
     * Обновление внутреннего состояния чата
     */
    updateInternalState(context, response) {
        // Обновляем историю чата минимальным контекстом
        this.chat.chatHistory = [
            ...context.recent.slice(-2), // Последние 2 сообщения
            { role: 'assistant', content: 'Готов продолжить беседу.' }
        ];
    }

    /**
     * UI уведомления
     */
    showRecoveryNotification() {
        this.hideAllNotifications();

        const notification = document.createElement('div');
        notification.id = 'ai-recovery-notification';
        notification.className = 'recovery-notification recovery-in-progress';
        notification.innerHTML = `
            <div class="recovery-content">
                <span class="recovery-icon">🔄</span>
                <span class="recovery-text">Переподключение к ИИ...</span>
            </div>
        `;

        this.addNotificationToDOM(notification);
    }

    showSuccessNotification() {
        this.hideAllNotifications();

        const notification = document.createElement('div');
        notification.id = 'ai-recovery-notification';
        notification.className = 'recovery-notification recovery-success';
        notification.innerHTML = `
            <div class="recovery-content">
                <span class="recovery-icon">✅</span>
                <span class="recovery-text">Соединение восстановлено</span>
            </div>
        `;

        this.addNotificationToDOM(notification);

        // Автоматически скрываем через 3 секунды
        setTimeout(() => this.hideAllNotifications(), 3000);
    }

    showFailureNotification() {
        this.hideAllNotifications();

        const notification = document.createElement('div');
        notification.id = 'ai-recovery-notification';
        notification.className = 'recovery-notification recovery-failure';
        notification.innerHTML = `
            <div class="recovery-content">
                <span class="recovery-icon">❌</span>
                <span class="recovery-text">Не удалось восстановить соединение</span>
            </div>
        `;

        this.addNotificationToDOM(notification);
    }

    addNotificationToDOM(notification) {
        // Добавляем в контейнер сообщений или в body
        const container = this.chat.messagesContainer || document.body;
        container.appendChild(notification);

        // Добавляем стили если их нет
        this.ensureNotificationStyles();
    }

    hideAllNotifications() {
        const existing = document.getElementById('ai-recovery-notification');
        if (existing) {
            existing.remove();
        }
    }

    /**
     * Стили для уведомлений
     */
    ensureNotificationStyles() {
        if (document.getElementById('ai-recovery-styles')) {
            return;
        }

        const styles = document.createElement('style');
        styles.id = 'ai-recovery-styles';
        styles.textContent = `
            .recovery-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                padding: 12px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideIn 0.3s ease-out;
            }
            
            .recovery-in-progress {
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            }
            
            .recovery-success {
                background: linear-gradient(135deg, #10b981, #047857);
            }
            
            .recovery-failure {
                background: linear-gradient(135deg, #ef4444, #dc2626);
            }
            
            .recovery-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .recovery-icon {
                font-size: 16px;
            }
            
            .recovery-text {
                font-size: 14px;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;

        document.head.appendChild(styles);
    }

    /**
     * Мониторинг здоровья ИИ
     */
    startHealthMonitoring() {
        if (this.isMonitoring) {
            return;
        }

        this.isMonitoring = true;
        console.log('🔍 AI Recovery: Health monitoring started');
    }

    /**
     * Деактивация модуля
     */
    deactivate() {
        // Восстанавливаем оригинальный метод
        if (this.originalSendMessage && this.chat) {
            this.chat.sendMessage = this.originalSendMessage;
        }

        // Останавливаем мониторинг
        this.clearTimeoutWatch();
        this.isMonitoring = false;

        // Убираем уведомления
        this.hideAllNotifications();

        console.log('🔄 AI Recovery Module deactivated');
    }

    /**
     * Настройки модуля
     */
    updateSettings(newOptions) {
        this.options = { ...this.options, ...newOptions };
        console.log('⚙️ AI Recovery: Settings updated', this.options);
    }
}

// Экспорт для использования
window.AIRecoveryModule = AIRecoveryModule;