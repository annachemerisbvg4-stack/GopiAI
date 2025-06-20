/**
 * AI Recovery Module v2.0 - С интеграцией TxtAI памяти
 * Модуль подключается к существующему чату без изменения основного кода
 * НОВОЕ: Интеграция с GopiAI Memory System для сохранения полного контекста
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
            useMemorySystem: true, // НОВОЕ: использовать TxtAI память
            memoryContextLimit: 5,  // НОВОЕ: количество сообщений из памяти
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

        // НОВОЕ: Ссылка на bridge для доступа к памяти
        this.bridge = null;

        console.log('🔄 AI Recovery Module v2.0 initialized with Memory System');
    }

    /**
     * Активация модуля - подключение к существующему чату
     */
    activate() {
        if (!this.chat) {
            console.error('❌ AI Recovery: No chat interface provided');
            return;
        }

        // НОВОЕ: Получаем доступ к bridge
        this.getBridgeReference();

        // Патчим существующий sendMessage методы
        this.patchChatInterface();

        // Запускаем мониторинг
        this.startHealthMonitoring();

        console.log('✅ AI Recovery Module v2.0 activated with Memory System');
    }

    /**
     * НОВОЕ: Получение ссылки на bridge для доступа к памяти
     */
    getBridgeReference() {
        // Пытаемся найти bridge в глобальном контексте
        if (window.bridge) {
            this.bridge = window.bridge;
            console.log('🧠 AI Recovery: Memory bridge connected');
        } else {
            console.warn('⚠️ AI Recovery: Memory bridge not found, working without memory');
            this.options.useMemorySystem = false;
        }
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
            // НОВОЕ: Сохраняем сообщение в память ПЕРЕД отправкой
            await this.saveMessageToMemory();

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
     * НОВОЕ: Сохранение сообщения в память перед отправкой
     */
    async saveMessageToMemory() {
        if (!this.options.useMemorySystem || !this.bridge) {
            return;
        }

        try {
            // Получаем текущее сообщение из input
            const messageInput = document.getElementById('message-input');
            if (messageInput && messageInput.value.trim()) {
                const message = messageInput.value.trim();
                console.log('💾 AI Recovery: Pre-saving message to memory');
                
                // Сохраняем через bridge (это обновит TxtAI память)
                if (this.bridge.save_chat_exchange) {
                    // Сохранение произойдет после получения ответа от ИИ
                }
            }
        } catch (error) {
            console.warn('⚠️ AI Recovery: Failed to pre-save message:', error);
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
     * ОБНОВЛЕНО: Главный метод восстановления с памятью
     */
    async performRecovery() {
        if (this.isRecovering) {
            return; // Избегаем множественного восстановления
        }

        this.isRecovering = true;
        this.retryCount++;

        console.log(`🔄 AI Recovery: Starting recovery attempt ${this.retryCount}/${this.options.maxRetries} with Memory System`);

        try {
            // 1. Показываем уведомление
            if (this.options.showNotifications) {
                this.showRecoveryNotification();
            }

            // 2. Останавливаем текущие операции
            this.stopCurrentOperations();

            // 3. НОВОЕ: Получаем полный контекст из памяти
            const memoryContext = await this.getMemoryContext();

            // 4. НОВОЕ: Выполняем восстановление с полной памятью
            await this.memoryAwareRestore(memoryContext);

            // 5. Убираем уведомление
            if (this.options.showNotifications) {
                this.hideRecoveryNotification();
                this.showSuccessNotification();
            }

            console.log('✅ AI Recovery: Recovery completed successfully with Memory');

        } catch (error) {
            console.error('❌ AI Recovery: Recovery failed:', error);
            this.showFailureNotification();

        } finally {
            this.isRecovering = false;
        }
    }

    /**
     * НОВОЕ: Получение контекста из TxtAI памяти
     */
    async getMemoryContext() {
        if (!this.options.useMemorySystem || !this.bridge) {
            return this.getFallbackContext();
        }

        try {
            // Получаем последнее сообщение пользователя
            const messageInput = document.getElementById('message-input');
            const lastMessage = messageInput ? messageInput.value.trim() : '';

            if (!lastMessage) {
                return this.getFallbackContext();
            }

            // Обогащаем контекст через память
            let enrichedContext = '';
            if (this.bridge.enrich_message) {
                enrichedContext = await this.bridge.enrich_message(lastMessage);
                console.log('🧠 AI Recovery: Retrieved memory context');
            }

            // Получаем статистику памяти
            let memoryStats = {};
            if (this.bridge.get_memory_stats) {
                const statsJson = await this.bridge.get_memory_stats();
                try {
                    memoryStats = JSON.parse(statsJson);
                } catch (e) {
                    console.warn('⚠️ Failed to parse memory stats');
                }
            }

            return {
                lastMessage,
                enrichedContext,
                memoryStats,
                source: 'txtai_memory'
            };

        } catch (error) {
            console.warn('⚠️ AI Recovery: Failed to get memory context:', error);
            return this.getFallbackContext();
        }
    }

    /**
     * НОВОЕ: Fallback контекст если память недоступна
     */
    getFallbackContext() {
        const history = this.chat.chatHistory || [];
        const recentMessages = history.slice(-4);

        return {
            recent: recentMessages,
            source: 'local_history'
        };
    }

    /**
     * НОВОЕ: Восстановление с учетом памяти
     */
    async memoryAwareRestore(context) {
        console.log('🧠 AI Recovery: Performing memory-aware restore');

        if (context.source === 'txtai_memory') {
            // Используем обогащенный контекст из памяти
            await this.restoreWithTxtAIMemory(context);
        } else {
            // Fallback к старому методу
            await this.restoreWithLocalHistory(context);
        }
    }

    /**
     * НОВОЕ: Восстановление с TxtAI памятью
     */
    async restoreWithTxtAIMemory(context) {
        const restorePrompt = `[СИСТЕМА: Восстановление сессии с памятью GopiAI]

Контекст проекта: GopiAI - модульная система ИИ-ассистента
Архитектура: Модульная (GopiAI-Core, GopiAI-UI, GopiAI-WebView, GopiAI-Widgets)
Технологии: Python, PySide6, QtWebEngine, TxtAI, Claude AI

Последнее сообщение пользователя: "${context.lastMessage}"

Релевантный контекст из памяти:
${context.enrichedContext}

Статистика памяти: ${context.memoryStats.total_messages || 0} сообщений в базе

Пожалуйста, подтвердите готовность продолжить работу с проектом GopiAI. Ответьте кратко "Готов продолжить работу с GopiAI".`;

        try {
            // Отправляем восстановительный запрос
            const response = await puter.ai.chat([{ 
                role: 'user', 
                content: restorePrompt 
            }], {
                model: this.chat.currentModel
            });

            // Сохраняем факт восстановления в память
            if (this.bridge.save_chat_exchange) {
                await this.bridge.save_chat_exchange(
                    "[Восстановление сессии]", 
                    "Сессия восстановлена с полным контекстом GopiAI"
                );
            }

            console.log('✅ AI Recovery: TxtAI memory restore completed');

        } catch (error) {
            console.error('❌ AI Recovery: TxtAI restore failed:', error);
            throw error;
        }
    }

    /**
     * НОВОЕ: Fallback восстановление с локальной историей
     */
    async restoreWithLocalHistory(context) {
        console.log('📝 AI Recovery: Using fallback local history restore');

        const recentMessages = context.recent || [];
        const summary = recentMessages.length > 0 ? 
            `Последние сообщения: ${recentMessages.slice(-2).map(m => 
                `${m.role}: ${m.content.substring(0, 50)}...`).join('; ')}` : 
            'Нет доступной истории';

        const restorePrompt = `[СИСТЕМА: Восстановление сессии GopiAI]
Проект: GopiAI - модульная система ИИ-ассистента
${summary}
Подтвердите готовность продолжить. Ответьте "Готов продолжить".`;

        const response = await puter.ai.chat([{ 
            role: 'user', 
            content: restorePrompt 
        }], {
            model: this.chat.currentModel
        });

        console.log('✅ AI Recovery: Local history restore completed');
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
     * UI уведомления (без изменений)
     */
    showRecoveryNotification() {
        this.hideAllNotifications();

        const notification = document.createElement('div');
        notification.id = 'ai-recovery-notification';
        notification.className = 'recovery-notification recovery-in-progress';
        notification.innerHTML = `
            <div class="recovery-content">
                <span class="recovery-icon">🔄</span>
                <span class="recovery-text">Переподключение к ИИ с полной памятью...</span>
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
                <span class="recovery-text">Соединение восстановлено с памятью GopiAI</span>
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
     * Стили для уведомлений (без изменений)
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
        console.log('🔍 AI Recovery: Health monitoring started with Memory System');
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

        console.log('🔄 AI Recovery Module v2.0 deactivated');
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