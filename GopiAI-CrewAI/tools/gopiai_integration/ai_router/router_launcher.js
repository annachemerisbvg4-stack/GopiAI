/**
 * Router Launcher
 * Скрипт для запуска AI Router из Python с использованием временных файлов
 * 
 * Использование:
 * node router_launcher.js <input_file> <output_file>
 */

const fs = require('fs');
const path = require('path');

// Импортируем модуль роутера
const { AIRouter, createRouter } = require('./ai_router_system');

async function main() {
    try {
        // Проверка аргументов
        if (process.argv.length < 4) {
            console.error('Необходимо указать пути к входному и выходному файлам');
            console.error('Использование: node router_launcher.js <input_file> <output_file>');
            process.exit(1);
        }

        const inputFile = process.argv[2];
        const outputFile = process.argv[3];

        // Проверяем существование входного файла
        if (!fs.existsSync(inputFile)) {
            console.error(`Входной файл не найден: ${inputFile}`);
            process.exit(1);
        }

        // Читаем входные данные
        const inputData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
        const { message, taskType, configPath } = inputData;

        // Проверяем наличие всех необходимых данных
        if (!message) {
            writeOutput(outputFile, { success: false, error: 'Отсутствует сообщение пользователя' });
            process.exit(1);
        }

        // Инициализируем роутер
        const router = createRouter(configPath || './ai_rotation_config.js');
        
        if (!router) {
            writeOutput(outputFile, { success: false, error: 'Не удалось создать экземпляр AIRouter' });
            process.exit(1);
        }

        // Обрабатываем запрос
        try {
            const response = await router.chat(message, { taskType: taskType || 'general' });
            
            // Записываем результат в выходной файл
            writeOutput(outputFile, {
                success: true,
                response: response.response,
                provider: response.provider,
                model: response.model
            });
        } catch (error) {
            writeOutput(outputFile, { success: false, error: error.message });
        }
    } catch (error) {
        console.error('Ошибка:', error.message);
        // Пытаемся записать ошибку в выходной файл, если он был указан
        if (process.argv.length >= 4) {
            try {
                writeOutput(process.argv[3], { success: false, error: error.message });
            } catch (writeError) {
                console.error('Не удалось записать ошибку в выходной файл:', writeError.message);
            }
        }
        process.exit(1);
    }
}

// Функция для записи результата в выходной файл
function writeOutput(outputFile, data) {
    fs.writeFileSync(outputFile, JSON.stringify(data, null, 2), 'utf8');
}

// Запускаем основную функцию
main(); 