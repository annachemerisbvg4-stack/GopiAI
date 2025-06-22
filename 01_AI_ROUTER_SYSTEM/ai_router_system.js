/**
 * 🎯 УМНАЯ СИСТЕМА AI РОТАЦИИ
 * Автоматическое переключение между провайдерами на основе лимитов и нагрузки
 * Создано для максимального использования free tier API
 */

class AIRouter {
    constructor(config) {
        this.providers = config.providers || [];
        this.usage = this.loadUsage();
        this.currentProvider = null;
        this.requestQueue = [];
        this.isProcessing = false;
        
        // Инициализация мониторинга
        this.initializeMonitoring();
        
        console.log('🚀 AI Router инициализирован с', this.providers.length, 'провайдерами');
    }

    /**
     * 🧠 ИНТЕЛЛЕКТУАЛЬНЫЙ ВЫБОР ПРОВАЙДЕРА
     */
    selectBestProvider(taskType = 'general') {
        const now = Date.now();
        const currentMinute = Math.floor(now / 60000);
        
        // Сброс счетчиков если прошла минута
        this.resetCountersIfNeeded(currentMinute);
        
        // Фильтруем доступных провайдеров
        const availableProviders = this.providers.filter(provider => {
            const usage = this.usage[provider.name] || { rpm: 0, tpm: 0, currentMinute };
            
            // Проверяем лимиты (оставляем 20% буфер)
            const rpmUsage = (usage.rpm / provider.limits.rpm) * 100;
            const tpmUsage = (usage.tpm / provider.limits.tpm) * 100;
            
            return rpmUsage < 80 && tpmUsage < 80 && provider.status === 'active';
        });

        if (availableProviders.length === 0) {
            console.warn('⚠️ Все провайдеры исчерпали лимиты! Ожидание...');
            return null;
        }

        // Выбираем лучшего на основе приоритета и нагрузки
        const bestProvider = availableProviders.sort((a, b) => {
            // Сначала по приоритету
            if (a.priority !== b.priority) {
                return a.priority - b.priority;
            }
            
            // Потом по загруженности
            const aUsage = this.getProviderUsagePercent(a.name);
            const bUsage = this.getProviderUsagePercent(b.name);
            return aUsage - bUsage;
        })[0];

        this.currentProvider = bestProvider;
        console.log('🎯 Выбран провайдер:', bestProvider.name, 
                   `(RPM: ${this.usage[bestProvider.name]?.rpm || 0}/${bestProvider.limits.rpm})`);
        
        return bestProvider;
    }

    /**
     * 💬 ОСНОВНАЯ ФУНКЦИЯ ЧАТА
     */
    async chat(message, options = {}) {
        const provider = this.selectBestProvider(options.taskType);
        
        if (!provider) {
            throw new Error('Все провайдеры временно недоступны. Попробуйте через минуту.');
        }

        try {
            const startTime = Date.now();
            const response = await this.makeRequest(provider, message, options);
            const duration = Date.now() - startTime;
            
            // Обновляем статистику
            this.updateUsage(provider.name, message, response);
            
            // Логируем успех
            console.log(`✅ ${provider.name}: ${duration}ms, ${this.estimateTokens(response)} токенов`);
            
            return {
                response: response,
                provider: provider.name,
                model: provider.model,
                duration: duration,
                success: true
            };

        } catch (error) {
            console.error(`❌ Ошибка ${provider.name}:`, error.message);
            
            // Помечаем провайдера как проблемного
            if (this.isRateLimitError(error)) {
                this.markProviderExhausted(provider.name);
            } else {
                this.markProviderError(provider.name);
            }
            
            // Пробуем следующего провайдера
            return this.retryWithNextProvider(message, options, provider.name);
        }
    }

    /**
     * 🔄 ПОВТОРНАЯ ПОПЫТКА С ДРУГИМ ПРОВАЙДЕРОМ
     */
    async retryWithNextProvider(message, options, excludeProvider) {
        const availableProviders = this.providers.filter(p => 
            p.name !== excludeProvider && p.status === 'active'
        );

        if (availableProviders.length === 0) {
            throw new Error('Все провайдеры недоступны');
        }

        console.log('🔄 Переключение на резервного провайдера...');
        return this.chat(message, options);
    }

    /**
     * 📡 ВЫПОЛНЕНИЕ ЗАПРОСА К ПРОВАЙДЕРУ
     */
    async makeRequest(provider, message, options) {
        const requestData = this.buildRequestData(provider, message, options);
        
        const response = await fetch(provider.endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${provider.apiKey}`,
                ...provider.headers
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        return this.extractResponse(provider, data);
    }

    /**
     * 🏗️ ПОСТРОЕНИЕ ЗАПРОСА ДЛЯ РАЗНЫХ ПРОВАЙДЕРОВ
     */
    buildRequestData(provider, message, options) {
        const baseRequest = {
            messages: [{ role: 'user', content: message }],
            max_tokens: options.maxTokens || 1000,
            temperature: options.temperature || 0.7
        };

        switch (provider.type) {
            case 'openai-compatible':
                return {
                    ...baseRequest,
                    model: provider.model
                };
                
            case 'gemini':
                return {
                    contents: [{ parts: [{ text: message }] }],
                    generationConfig: {
                        maxOutputTokens: options.maxTokens || 1000,
                        temperature: options.temperature || 0.7
                    }
                };
                
            case 'cohere':
                return {
                    message: message,
                    model: provider.model,
                    max_tokens: options.maxTokens || 1000,
                    temperature: options.temperature || 0.7
                };
                
            default:
                return baseRequest;
        }
    }

    /**
     * 📝 ИЗВЛЕЧЕНИЕ ОТВЕТА ИЗ РАЗНЫХ ФОРМАТОВ
     */
    extractResponse(provider, data) {
        switch (provider.type) {
            case 'openai-compatible':
                return data.choices?.[0]?.message?.content || data.choices?.[0]?.text || '';
                
            case 'gemini':
                return data.candidates?.[0]?.content?.parts?.[0]?.text || '';
                
            case 'cohere':
                return data.text || '';
                
            default:
                return data.response || data.text || JSON.stringify(data);
        }
    }

    /**
     * 📊 ОБНОВЛЕНИЕ СТАТИСТИКИ ИСПОЛЬЗОВАНИЯ
     */
    updateUsage(providerName, request, response) {
        const now = Date.now();
        const currentMinute = Math.floor(now / 60000);
        
        if (!this.usage[providerName]) {
            this.usage[providerName] = { rpm: 0, tpm: 0, currentMinute };
        }

        const usage = this.usage[providerName];
        
        // Сброс если новая минута
        if (usage.currentMinute !== currentMinute) {
            usage.rpm = 0;
            usage.tpm = 0;
            usage.currentMinute = currentMinute;
        }

        // Обновляем счетчики
        usage.rpm += 1;
        usage.tpm += this.estimateTokens(request) + this.estimateTokens(response);
        
        // Сохраняем в localStorage
        this.saveUsage();
    }

    /**
     * 🔢 ОЦЕНКА КОЛИЧЕСТВА ТОКЕНОВ
     */
    estimateTokens(text) {
        if (!text) return 0;
        // Грубая оценка: ~4 символа = 1 токен для латиницы, ~2 для кириллицы
        const latinChars = (text.match(/[a-zA-Z0-9\s.,!?;:()\-]/g) || []).length;
        const cyrillicChars = text.length - latinChars;
        return Math.ceil(latinChars / 4 + cyrillicChars / 2);
    }

    /**
     * 🔄 СБРОС СЧЕТЧИКОВ ПО ВРЕМЕНИ
     */
    resetCountersIfNeeded(currentMinute) {
        Object.keys(this.usage).forEach(providerName => {
            const usage = this.usage[providerName];
            if (usage.currentMinute !== currentMinute) {
                usage.rpm = 0;
                usage.tpm = 0;
                usage.currentMinute = currentMinute;
            }
        });
    }

    /**
     * 📈 ПОЛУЧЕНИЕ ПРОЦЕНТА ИСПОЛЬЗОВАНИЯ
     */
    getProviderUsagePercent(providerName) {
        const provider = this.providers.find(p => p.name === providerName);
        const usage = this.usage[providerName] || { rpm: 0, tpm: 0 };
        
        const rpmPercent = (usage.rpm / provider.limits.rpm) * 100;
        const tpmPercent = (usage.tpm / provider.limits.tpm) * 100;
        
        return Math.max(rpmPercent, tpmPercent);
    }

    /**
     * ⚠️ ПРОВЕРКА ОШИБОК ЛИМИТОВ
     */
    isRateLimitError(error) {
        const message = error.message.toLowerCase();
        return message.includes('rate limit') || 
               message.includes('quota') || 
               message.includes('429') ||
               message.includes('too many requests');
    }

    /**
     * 🚫 ПОМЕТКА ПРОВАЙДЕРА КАК ИСЧЕРПАННОГО
     */
    markProviderExhausted(providerName) {
        const provider = this.providers.find(p => p.name === providerName);
        if (provider) {
            const usage = this.usage[providerName] || { rpm: 0, tpm: 0 };
            usage.rpm = provider.limits.rpm; // Помечаем как исчерпанный
            console.warn(`⚠️ ${providerName} исчерпал лимиты`);
        }
    }

    /**
     * 💾 СОХРАНЕНИЕ/ЗАГРУЗКА СТАТИСТИКИ
     */
    saveUsage() {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('ai_router_usage', JSON.stringify(this.usage));
        }
    }

    loadUsage() {
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('ai_router_usage');
            return saved ? JSON.parse(saved) : {};
        }
        return {};
    }

    /**
     * 📊 МОНИТОРИНГ И СТАТИСТИКА
     */
    initializeMonitoring() {
        // Периодическое логирование статистики
        setInterval(() => {
            this.logStatus();
        }, 60000); // Каждую минуту
    }

    logStatus() {
        console.log('📊 Статус AI Router:');
        this.providers.forEach(provider => {
            const usage = this.usage[provider.name] || { rpm: 0, tpm: 0 };
            const percent = this.getProviderUsagePercent(provider.name);
            const status = percent > 80 ? '🔴' : percent > 50 ? '🟡' : '🟢';
            
            console.log(`${status} ${provider.name}: ${usage.rpm}/${provider.limits.rpm} RPM (${percent.toFixed(1)}%)`);
        });
    }

    /**
     * 🎯 ПОЛУЧЕНИЕ СТАТИСТИКИ ДЛЯ UI
     */
    getStats() {
        return {
            providers: this.providers.map(provider => ({
                name: provider.name,
                model: provider.model,
                status: provider.status,
                usage: this.usage[provider.name] || { rpm: 0, tpm: 0 },
                limits: provider.limits,
                usagePercent: this.getProviderUsagePercent(provider.name)
            })),
            totalRequests: Object.values(this.usage).reduce((sum, u) => sum + u.rpm, 0),
            currentProvider: this.currentProvider?.name || 'auto'
        };
    }
}

// 🎯 ЭКСПОРТ ДЛЯ ИСПОЛЬЗОВАНИЯ
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIRouter;
} else if (typeof window !== 'undefined') {
    window.AIRouter = AIRouter;
}

console.log('🚀 AI Router System загружен и готов к работе!');