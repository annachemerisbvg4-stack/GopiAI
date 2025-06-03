// Скрипт для запуска MCP сервера
const { spawn } = require('child_process');
const path = require('path');

console.log('Starting BrowserMCP server...');

// Запускаем MCP сервер
const mcp = spawn('npx', ['@browsermcp/mcp'], {
  stdio: 'inherit',
  shell: true
});

// Обрабатываем события
mcp.on('error', (err) => {
  console.error('Failed to start MCP server:', err);
});

mcp.on('close', (code) => {
  console.log(`MCP server exited with code ${code}`);
});

// Обрабатываем сигналы завершения
process.on('SIGINT', () => {
  console.log('Stopping MCP server...');
  mcp.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('Stopping MCP server...');
  mcp.kill('SIGTERM');
});
