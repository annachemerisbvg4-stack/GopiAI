/**
 * 🔧 КОНФИГУРАЦИЯ AI ПРОВАЙДЕРОВ
 * Настройки всех ваших драгоценных free tier ключей
 * Обновите API ключи на свои реальные!
 */

const AI_PROVIDERS_CONFIG = {
    providers: [
        // 🥇 TIER 1 - САМЫЕ МОЩНЫЕ
        {
            name: 'Novita-Qwen',
            type: 'openai-compatible',
            endpoint: 'https://api.novita.ai/v3/openai/chat/completions',
            apiKey: 'YOUR_NOVITA_API_KEY_HERE', // 🔑 Замените на свой ключ
            model: 'qwen/qwen-2.5-coder-32b-instruct',
            priority: 1, // Высший приоритет
            status: 'active',
            limits: {
                rpm: 1000,        // 1000 запросов в минуту
                tpm: 50000000,    // 50М токенов в минуту
                daily: 1440000    // ~1.4М запросов в день
            },
            headers: {
                'User-Agent': 'GopiAI/1.0'
            },
            features: ['chat', 'code', 'reasoning'],
            description: '🧠 Мощная модель для кода и рассуждений'
        },

        {
            name: 'Groq-Lightning',
            type: 'openai-compatible', 
            endpoint: 'https://api.groq.com/openai/v1/chat/completions',
            apiKey: 'YOUR_GROQ_API_KEY_HERE', // 🔑 Замените на свой ключ
            model: 'llama-3.3-70b-versatile', // ✅ Обновлено! (llama-3.1 устарел с 24.01.2025)
            priority: 2,
            status: 'active',
            limits: {
                rpm: 30,          // 30 запросов в минуту
                tpm: 6000,        // 6K токенов в минуту
                daily: 43200      // ~43K запросов в день
            },
            features: ['chat', 'fast-response'],
            description: '⚡ Сверхбыстрые ответы для интерактивного чата'
        },

        // 🥈 TIER 2 - НАДЕЖНЫЕ РЕЗЕРВЫ
        {
            name: 'Google-Gemini',
            type: 'gemini',
            endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
            apiKey: 'YOUR_GEMINI_API_KEY_HERE', // 🔑 Замените на свой ключ
            model: 'gemini-1.5-flash',
            priority: 3,
            status: 'active',
            limits: {
                rpm: 15,          // 15 запросов в минуту
                tpm: 1000000,     // 1М токенов в минуту
                daily: 21600      // ~21K запросов в день
            },
            headers: {
                'Content-Type': 'application/json'
            },
            features: ['chat', 'multimodal', 'long-context'],
            description: '🧠 Умный Google AI с поддержкой изображений'
        },

        {
            name: 'Cohere-Command',
            type: 'cohere',
            endpoint: 'https://api.cohere.ai/v1/chat',
            apiKey: 'YOUR_COHERE_API_KEY_HERE', // 🔑 Замените на свой ключ
            model: 'command-r-plus',
            priority: 4,
            status: 'active',
            limits: {
                rpm: 20,          // 20 запросов в минуту (примерно)
                tpm: 40000,       // 40K токенов в минуту
                daily: 28800      // ~28K запросов в день
            },
            features: ['chat', 'rag', 'multilingual'],
            description: '💬 Отличная модель для диалогов и RAG'
        },

        {
            name: 'Cerebras-Llama',
            type: 'openai-compatible',
            endpoint: 'https://api.cerebras.ai/v1/chat/completions',
            apiKey: 'YOUR_CEREBRAS_API_KEY_HERE', // 🔑 Замените на свой ключ
            model: 'llama-3.3-70b', // ✅ Обновлено! (теперь поддерживается 3.3)
            priority: 5,
            status: 'active',
            limits: {
                rpm: 30,          // 30 запросов в минуту (примерно)
                tpm: 60000,       // 60K токенов в минуту
                daily: 43200      // ~43K запросов в день
            },
            features: ['chat', 'reasoning'],
            description: '🦙 Мощная Llama модель от Cerebras'
        },

        // 🥉 TIER 3 - СПЕЦИАЛЬНЫЕ И РЕЗЕРВНЫЕ
        {
            name: 'HuggingFace-Mistral',
            type: 'openai-compatible',
            endpoint: 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1',
            apiKey: 'YOUR_HF_API_KEY_HERE', // 🔑 Замените на свой ключ
            model: 'mistralai/Mistral-7B-Instruct-v0.1',
            priority: 6,
            status: 'backup', // Резервный
            limits: {
                rpm: 10,          // 10 запросов в минуту
                tpm: 20000,       // 20K токенов в минуту
                daily: 14400      // ~14K запросов в день
            },
            features: ['chat', 'instruct'],
            description: '🤖 Бесплатная модель Mistral через HuggingFace'
        }
    ],

    // 🎯 НАСТРОЙКИ РОУТИНГА
    routing: {
        // Стратегия выбора провайдера
        strategy: 'priority-based', // 'priority-based', 'round-robin', 'least-used'
        
        // Буферы безопасности (% от лимита)
        safetyBuffers: {
            rpm: 20,  // Оставляем 20% буфер для RPM
            tpm: 20   // Оставляем 20% буфер для TPM
        },
        
        // Настройки retry
        retrySettings: {
            maxRetries: 3,
            retryDelay: 1000, // мс
            backoffMultiplier: 2
        },
        
        // Timeouts
        timeouts: {
            requestTimeout: 30000,  // 30 секунд
            providerTimeout: 5000   // 5 секунд ожидания ответа
        }
    },

    // 🎛️ НАСТРОЙКИ ПО ТИПАМ ЗАДАЧ
    taskProfiles: {
        'chat': {
            preferredProviders: ['Groq-Lightning', 'Novita-Qwen'],
            maxTokens: 1000,
            temperature: 0.7
        },
        'code': {
            preferredProviders: ['Novita-Qwen', 'Cerebras-Llama'],
            maxTokens: 2000,
            temperature: 0.3
        },
        'creative': {
            preferredProviders: ['Google-Gemini', 'Cohere-Command'],
            maxTokens: 1500,
            temperature: 0.9
        },
        'analysis': {
            preferredProviders: ['Google-Gemini', 'Novita-Qwen'],
            maxTokens: 2500,
            temperature: 0.4
        }
    },

    // 📊 МОНИТОРИНГ
    monitoring: {
        enableLogging: true,
        logLevel: 'info', // 'debug', 'info', 'warn', 'error'
        statsUpdateInterval: 60000, // Обновление статистики каждую минуту
        
        // Алерты
        alerts: {
            usageThreshold: 80, // Предупреждение при 80% использования
            errorThreshold: 5,  // Предупреждение при 5 ошибках подряд
            enableNotifications: true
        }
    }
};

// 🎯 ФУНКЦИИ ДЛЯ РАБОТЫ С КОНФИГОМ
const ConfigManager = {
    /**
     * 🔑 Обновление API ключей
     */
    updateApiKeys(keyMapping) {
        AI_PROVIDERS_CONFIG.providers.forEach(provider => {
            if (keyMapping[provider.name]) {
                provider.apiKey = keyMapping[provider.name];
                console.log(`🔑 Обновлен ключ для ${provider.name}`);
            }
        });
    },

    /**
     * ✅ Валидация конфигурации
     */
    validateConfig() {
        const issues = [];
        
        AI_PROVIDERS_CONFIG.providers.forEach(provider => {
            if (!provider.apiKey || provider.apiKey.includes('YOUR_')) {
                issues.push(`❌ ${provider.name}: не установлен API ключ`);
            }
            
            if (!provider.endpoint) {
                issues.push(`❌ ${provider.name}: не указан endpoint`);
            }
        });
        
        if (issues.length > 0) {
            console.warn('⚠️ Проблемы конфигурации:');
            issues.forEach(issue => console.warn(issue));
            return false;
        }
        
        console.log('✅ Конфигурация валидна');
        return true;
    },

    /**
     * 📊 Получение активных провайдеров
     */
    getActiveProviders() {
        return AI_PROVIDERS_CONFIG.providers.filter(p => p.status === 'active');
    },

    /**
     * 🎯 Получение провайдеров для задачи
     */
    getProvidersForTask(taskType) {
        const profile = AI_PROVIDERS_CONFIG.taskProfiles[taskType];
        if (!profile) return this.getActiveProviders();
        
        const preferred = profile.preferredProviders;
        return AI_PROVIDERS_CONFIG.providers.filter(p => 
            preferred.includes(p.name) && p.status === 'active'
        );
    }
};

// 🎨 БЫСТРЫЕ НАСТРОЙКИ
const QUICK_CONFIGS = {
    // 🚀 Максимальная производительность
    'high-performance': {
        strategy: 'priority-based',
        safetyBuffers: { rpm: 10, tpm: 10 }, // Меньше буферы
        preferProviders: ['Novita-Qwen', 'Groq-Lightning']
    },
    
    // 🛡️ Максимальная надежность  
    'high-reliability': {
        strategy: 'round-robin',
        safetyBuffers: { rpm: 30, tpm: 30 }, // Больше буферы
        enableAllBackups: true
    },
    
    // 💰 Экономия лимитов
    'conservative': {
        strategy: 'least-used',
        safetyBuffers: { rpm: 40, tpm: 40 },
        preferFreeProviders: true
    }
};

// 📝 ИНСТРУКЦИИ ПО НАСТРОЙКЕ
const SETUP_INSTRUCTIONS = `
🚀 БЫСТРАЯ НАСТРОЙКА AI ROUTER:

1️⃣ Обновите API ключи:
   - Откройте ai_rotation_config.js
   - Замените YOUR_*_API_KEY_HERE на ваши реальные ключи
   
2️⃣ Выберите конфигурацию:
   - high-performance: для максимальной скорости
   - high-reliability: для максимальной надежности  
   - conservative: для экономии лимитов

3️⃣ Инициализация:
   const config = AI_PROVIDERS_CONFIG;
   const router = new AIRouter(config);
   
4️⃣ Использование:
   const result = await router.chat("Привет!");
   console.log(result.response);

🔧 Настройки готовы! Осталось только вставить ваши ключи!
`;

// 🎯 ЭКСПОРТ КОНФИГУРАЦИИ
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        AI_PROVIDERS_CONFIG, 
        ConfigManager, 
        QUICK_CONFIGS,
        SETUP_INSTRUCTIONS 
    };
} else if (typeof window !== 'undefined') {
    window.AI_PROVIDERS_CONFIG = AI_PROVIDERS_CONFIG;
    window.ConfigManager = ConfigManager;
    window.QUICK_CONFIGS = QUICK_CONFIGS;
    window.SETUP_INSTRUCTIONS = SETUP_INSTRUCTIONS;
}

console.log('🔧 AI Router Config загружен!');
console.log(SETUP_INSTRUCTIONS);