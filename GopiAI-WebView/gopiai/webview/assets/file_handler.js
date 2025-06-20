// file_handler.js - модуль для работы с файлами и изображениями

class FileHandler {
    constructor(chatApp) {
        this.chatApp = chatApp;
        this.bridge = chatApp.bridge;
        this.supportedImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        this.supportedFileTypes = ['text/plain', 'text/csv', 'application/json', 'application/pdf'];
        
        // Макс размер файла (10MB)
        this.maxFileSize = 10 * 1024 * 1024; 
        
        this.init();
    }
    
    init() {
        // Инициализация обработчиков событий
        this.setupPasteHandler();
        this.setupDropHandler();
        
        console.log('📁 FileHandler initialized');
    }
    
    setupPasteHandler() {
        // Обработка Ctrl+V
        document.addEventListener('paste', (event) => {
            // Предотвращаем стандартное поведение вставки только если что-то есть в буфере обмена
            if (event.clipboardData && event.clipboardData.items.length > 0) {
                const items = event.clipboardData.items;
                let handled = false;
                
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    
                    // Обработка изображений
                    if (item.type.startsWith('image/')) {
                        const file = item.getAsFile();
                        this.processImageFile(file);
                        handled = true;
                        break;
                    }
                    
                    // Обработка файлов
                    if (this.isSupportedFile(item.type)) {
                        const file = item.getAsFile();
                        this.processFile(file);
                        handled = true;
                        break;
                    }
                }
                
                // Только если мы обработали файл, предотвращаем стандартную вставку
                if (handled) {
                    event.preventDefault();
                }
            }
        });
        
        console.log('📋 Paste handler initialized');
    }
    
    setupDropHandler() {
        // Элементы для обработки drop событий
        const chatMessages = document.getElementById('chat-messages');
        const messageInput = document.getElementById('message-input');
        
        // Предотвращаем стандартное поведение перетаскивания браузера
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            chatMessages.addEventListener(eventName, preventDefaults, false);
            messageInput.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Визуальные эффекты при перетаскивании
        ['dragenter', 'dragover'].forEach(eventName => {
            chatMessages.addEventListener(eventName, highlight, false);
            messageInput.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            chatMessages.addEventListener(eventName, unhighlight, false);
            messageInput.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            chatMessages.classList.add('drag-highlight');
        }
        
        function unhighlight() {
            chatMessages.classList.remove('drag-highlight');
        }
        
        // Обработка сброшенных файлов
        chatMessages.addEventListener('drop', (e) => this.handleDrop(e), false);
        messageInput.addEventListener('drop', (e) => this.handleDrop(e), false);
        
        console.log('🖱️ Drop handler initialized');
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0]; // Берем только первый файл
            
            if (this.isImageFile(file)) {
                this.processImageFile(file);
            } else if (this.isSupportedFile(file.type)) {
                this.processFile(file);
            } else {
                this.showError(`Unsupported file type: ${file.type}`);
            }
        }
    }
    
    isImageFile(file) {
        return this.supportedImageTypes.includes(file.type);
    }
    
    isSupportedFile(fileType) {
        return this.supportedFileTypes.includes(fileType);
    }
    
    async processImageFile(file) {
        // Проверка размера файла
        if (file.size > this.maxFileSize) {
            this.showError(`File is too large. Maximum size is ${this.maxFileSize / (1024 * 1024)}MB`);
            return;
        }
        
        try {
            // Отображаем предпросмотр и сообщение о загрузке
            const messageId = this.chatApp.addUserMessage(`📤 Uploading image: ${file.name}...`);
            
            // Чтение файла как base64
            const base64Data = await this.readFileAsBase64(file);
            
            // Обновляем сообщение с предпросмотром
            const imagePreview = `<img src="${base64Data}" alt="${file.name}" class="chat-image">`;
            this.chatApp.updateUserMessage(messageId, imagePreview);
            
            // Создаем сообщение для отправки Claude с base64 данными
            const claudeMessage = `![Image](${base64Data})`;
            
            // Отправляем сообщение ИИ через bridge
            this.chatApp.sendMessageToAI(claudeMessage);
            
        } catch (error) {
            console.error('Error processing image:', error);
            this.showError('Failed to process the image');
        }
    }
    
    async processFile(file) {
        // Проверка размера файла
        if (file.size > this.maxFileSize) {
            this.showError(`File is too large. Maximum size is ${this.maxFileSize / (1024 * 1024)}MB`);
            return;
        }
        
        try {
            // Отображаем сообщение о загрузке
            const messageId = this.chatApp.addUserMessage(`📤 Uploading file: ${file.name}...`);
            
            // Чтение файла как текст/base64 в зависимости от типа
            let fileContent;
            
            if (file.type === 'text/plain' || file.type === 'application/json' || file.type === 'text/csv') {
                // Текстовые файлы читаем как текст
                fileContent = await this.readFileAsText(file);
                this.chatApp.updateUserMessage(messageId, `📄 File: ${file.name}\n\`\`\`\n${fileContent.slice(0, 200)}...\n\`\`\``);
            } else {
                // Другие файлы как base64
                fileContent = await this.readFileAsBase64(file);
                this.chatApp.updateUserMessage(messageId, `📎 File uploaded: ${file.name}`);
            }
            
            // Создаем сообщение для отправки Claude
            const claudeMessage = file.type.startsWith('text/') ? 
                `File content of ${file.name}:\n\`\`\`\n${fileContent}\n\`\`\`` :
                `File uploaded as base64: ${file.name}`;
            
            // Отправляем сообщение ИИ через bridge
            this.chatApp.sendMessageToAI(claudeMessage);
            
        } catch (error) {
            console.error('Error processing file:', error);
            this.showError('Failed to process the file');
        }
    }
    
    readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsDataURL(file);
        });
    }
    
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }
    
    showError(message) {
        // Отображение ошибки в чате
        this.chatApp.addSystemMessage(`⚠️ Error: ${message}`);
    }
}

// Экспорт модуля
if (typeof module !== 'undefined') {
    module.exports = { FileHandler };
} else {
    // Для использования в браузере
    window.FileHandler = FileHandler;
}