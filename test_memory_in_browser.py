"""
Простой тестовый HTML для проверки работы памяти в GopiAI
Добавьте этот код в чат и посмотрите результат
"""

test_memory_js = """
// Тест интеграции памяти GopiAI
console.log('🧪 Тестирование памяти GopiAI...');

// Проверяем доступность bridge
if (typeof bridge !== 'undefined') {
    console.log('✅ Bridge доступен');
    
    // Проверяем методы памяти
    const memoryMethods = [
        'enrich_message',
        'save_chat_exchange', 
        'start_new_chat_session',
        'get_memory_stats',
        'is_memory_available'
    ];
    
    memoryMethods.forEach(method => {
        if (typeof bridge[method] === 'function') {
            console.log(`✅ ${method} доступен`);
        } else {
            console.log(`❌ ${method} НЕ доступен`);
        }
    });
    
    // Тестируем проверку доступности памяти
    try {
        const available = bridge.is_memory_available();
        console.log(`🧠 Память доступна: ${available}`);
        
        if (available) {
            // Тестируем получение статистики
            const stats = bridge.get_memory_stats();
            console.log('📊 Статистика памяти:', JSON.parse(stats));
            
            // Тестируем обогащение сообщения
            const testMessage = "Привет! Как дела?";
            const enriched = bridge.enrich_message(testMessage);
            console.log('💬 Обогащенное сообщение:', enriched);
        }
    } catch (error) {
        console.error('❌ Ошибка тестирования памяти:', error);
    }
} else {
    console.log('❌ Bridge НЕ доступен');
}

// Выводим результат в документ
document.body.innerHTML += `
<div style="background: #2d2d2d; color: #fff; padding: 20px; margin: 10px; border-radius: 8px; font-family: monospace;">
<h3>🧪 Тест памяти GopiAI</h3>
<p>Откройте консоль браузера (F12) для подробной информации.</p>
<p>Bridge доступен: ${typeof bridge !== 'undefined' ? '✅ Да' : '❌ Нет'}</p>
${typeof bridge !== 'undefined' && typeof bridge.is_memory_available === 'function' ? 
  `<p>Память доступна: ${bridge.is_memory_available() ? '✅ Да' : '❌ Нет'}</p>` : 
  '<p>Методы памяти: ❌ Недоступны</p>'
}
</div>
`;
"""

print("Скопируйте этот JavaScript код в консоль браузера GopiAI:")
print("=" * 60)
print(test_memory_js)
print("=" * 60)
print("\nИли просто запустите GopiAI и проверьте логи на наличие сообщений о памяти:")
print("- '✅ Chat memory system imported successfully'")
print("- '✅ Memory system initialized in WebViewChatBridge'")
print("- Или сообщения о недоступности RAG API")