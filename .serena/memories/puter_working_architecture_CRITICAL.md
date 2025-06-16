# КРИТИЧЕСКИ ВАЖНО: Рабочая архитектура Puter.js

## ✅ РАБОЧАЯ СХЕМА (НЕ ТРОГАТЬ!)
```
WebViewChatWidget → file:///.../chat.html → Puter.js (CDN) → Python Bridge  
```

## 🔍 Детали из логов (16.06.2025):
- WebView загружается: `file:///C:/Users/crazy/GOPI_AI_MODULES/GopiAI-WebView/gopiai/webview/assets/chat.html`
- Bridge работает: `🔄 Bridge: received message from JS: привет!...` 
- AI отвечает: `🤖 Bridge: received AI response from claude-sonnet-4`
- Puter.js инициализируется из CDN через file:// протокол

## ❌ ЧТО НЕ ДЕЛАТЬ:
- НЕ создавать HTTP серверы для WebView (ломает всё)
- НЕ менять способ загрузки chat.html 
- НЕ модифицировать WebChannel bridge
- НЕ трогать модульную структуру UI

## ✅ БЕЗОПАСНЫЕ УЛУЧШЕНИЯ:
- RAG сервер отдельно (порт 8080)
- CSS/JS внутри существующего chat.html
- requirements_final_clean_2025-06-16.txt

**ЗАПОМНИТЬ**: file:// протокол работает с Puter.js! HTTP серверы были ненужными.