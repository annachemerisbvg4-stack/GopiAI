#!/usr/bin/env python3
"""
Smart Chunking System для RAG Memory
====================================
Умное разбиение файлов на chunk-и с интеграцией в GopiAI RAG систему
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from client import RAGMemoryClient

class SmartChunker:
    """Умный разбивщик файлов на chunk-и"""
    
    def __init__(self, rag_client: Optional[RAGMemoryClient] = None):
        self.rag_client = rag_client or RAGMemoryClient()
        
        # Настройки для разных типов файлов
        self.chunk_configs = {
            '.py': {'max_length': 2000, 'overlap': 200, 'split_by': 'code'},
            '.js': {'max_length': 1500, 'overlap': 150, 'split_by': 'code'},
            '.md': {'max_length': 1000, 'overlap': 100, 'split_by': 'markdown'},
            '.txt': {'max_length': 800, 'overlap': 80, 'split_by': 'paragraphs'},
            '.log': {'max_length': 500, 'overlap': 50, 'split_by': 'lines'},
            '.json': {'max_length': 1200, 'overlap': 120, 'split_by': 'json'},
        }
    
    def chunk_by_code(self, text: str, max_length: int, overlap: int) -> List[str]:
        """Разбивка кода по функциям/классам"""
        chunks = []
        
        # Ищем функции и классы
        patterns = [
            r'^(class\s+\w+.*?):',
            r'^(def\s+\w+.*?):',
            r'^(async\s+def\s+\w+.*?):',
            r'^(function\s+\w+.*?\{)',  # JS функции
        ]
        
        lines = text.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            # Проверяем, начинается ли новая функция/класс
            is_new_block = any(re.match(pattern, line.strip(), re.MULTILINE) for pattern in patterns)
            
            if is_new_block and current_length > max_length // 2:
                # Сохраняем текущий chunk
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
            else:
                current_chunk.append(line)
                current_length += len(line) + 1
                
                # Если chunk стал слишком большим
                if current_length > max_length:
                    chunks.append('\n'.join(current_chunk))
                    # Оставляем overlap
                    overlap_lines = current_chunk[-overlap//50:] if overlap//50 > 0 else []
                    current_chunk = overlap_lines
                    current_length = sum(len(line) for line in overlap_lines)
        
        # Добавляем последний chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return [chunk for chunk in chunks if chunk.strip()]
    
    def chunk_by_markdown(self, text: str, max_length: int, overlap: int) -> List[str]:
        """Разбивка markdown по заголовкам"""
        chunks = []
        sections = re.split(r'^(#{1,6}\s+.*)$', text, flags=re.MULTILINE)
        
        current_chunk = ""
        
        for section in sections:
            if not section.strip():
                continue
                
            # Если добавление секции превысит лимит
            if len(current_chunk) + len(section) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                # Добавляем overlap
                lines = current_chunk.split('\n')
                overlap_lines = lines[-overlap//50:] if overlap//50 > 0 else []
                current_chunk = '\n'.join(overlap_lines) + '\n' + section
            else:
                current_chunk += section
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return [chunk for chunk in chunks if chunk.strip()]
    
    def chunk_by_paragraphs(self, text: str, max_length: int, overlap: int) -> List[str]:
        """Разбивка текста по абзацам"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                # Простой overlap - последние слова
                words = current_chunk.split()
                overlap_words = words[-overlap//10:] if overlap//10 > 0 else []
                current_chunk = ' '.join(overlap_words) + '\n\n' + paragraph
            else:
                current_chunk += '\n\n' + paragraph if current_chunk else paragraph
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return [chunk for chunk in chunks if chunk.strip()]
    
    def chunk_text(self, text: str, file_extension: str) -> List[str]:
        """Основной метод разбивки текста"""
        config = self.chunk_configs.get(file_extension, self.chunk_configs['.txt'])
        
        max_length = config['max_length']
        overlap = config['overlap']
        split_by = config['split_by']
        
        if split_by == 'code':
            return self.chunk_by_code(text, max_length, overlap)
        elif split_by == 'markdown':
            return self.chunk_by_markdown(text, max_length, overlap)
        elif split_by == 'paragraphs':
            return self.chunk_by_paragraphs(text, max_length, overlap)
        else:
            # Простая разбивка по длине
            return self.simple_chunk(text, max_length, overlap)
    
    def simple_chunk(self, text: str, max_length: int, overlap: int) -> List[str]:
        """Простая разбивка по длине с overlap"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + max_length, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start += max_length - overlap
        return [chunk for chunk in chunks if chunk.strip()]
    
    def process_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Обработка одного файла"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception as e:
            print(f"Ошибка чтения файла {filepath}: {e}")
            return []
        
        extension = filepath.suffix.lower()
        chunks = self.chunk_text(text, extension)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                'file': str(filepath),
                'chunk_id': i,
                'text': chunk,
                'extension': extension,
                'size': len(chunk),
                'created_at': datetime.now().isoformat()
            })
        
        return result
    
    def scan_and_chunk(self, folder: str, extensions: tuple = ('.md', '.py', '.txt', '.js'), 
                      recursive: bool = True) -> List[Dict[str, Any]]:
        """Сканирование папки и разбивка всех файлов"""
        folder_path = Path(folder)
        all_chunks = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for filepath in folder_path.glob(pattern):
            if filepath.is_file() and filepath.suffix.lower() in extensions:
                print(f"Обрабатываем {filepath}...")
                chunks = self.process_file(filepath)
                all_chunks.extend(chunks)
        
        return all_chunks
    
    def upload_to_rag(self, chunks: List[Dict[str, Any]], session_title: str = None) -> str:
        """Загрузка chunk-ов в RAG систему"""
        if not self.rag_client:
            print("RAG клиент не настроен")
            return None
        
        # Создаем сессию
        title = session_title or f"Chunks Upload {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        session_id = self.rag_client.create_conversation(
            title=title,
            project_context="Auto-chunked files",
            tags=["auto-chunk", "file-import"]
        )
        
        # Загружаем chunk-и
        for chunk_data in chunks:
            try:
                self.rag_client.add_message(
                    session_id=session_id,
                    role="system",
                    content=chunk_data['text'],
                    metadata={
                        'file': chunk_data['file'],
                        'chunk_id': chunk_data['chunk_id'],
                        'extension': chunk_data['extension'],
                        'size': chunk_data['size'],
                        'created_at': chunk_data['created_at']
                    }
                )
            except Exception as e:
                print(f"Ошибка загрузки chunk-а {chunk_data['file']}[{chunk_data['chunk_id']}]: {e}")
        
        print(f"✅ Загружено {len(chunks)} chunk-ов в сессию {session_id}")
        return session_id

def main():
    """Пример использования"""
    chunker = SmartChunker()
    
    # Пример: chunk-им папку с документацией
    folder = input("Введите путь к папке для chunk-инга: ").strip()
    if not folder:
        folder = "."
    
    extensions = ('.md', '.py', '.txt', '.js', '.json')
    
    print(f"Сканируем папку: {folder}")
    chunks = chunker.scan_and_chunk(folder, extensions)
    
    print(f"Найдено {len(chunks)} chunk-ов")
    
    # Показываем примеры
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Файл: {chunk['file']}")
        print(f"Размер: {chunk['size']} символов")
        print(f"Текст: {chunk['text'][:200]}...")
    
    # Предлагаем загрузить в RAG
    upload = input("\nЗагрузить в RAG систему? (y/n): ").strip().lower()
    if upload in ['y', 'yes', 'да']:
        session_id = chunker.upload_to_rag(chunks)
        print(f"Загружено в сессию: {session_id}")

if __name__ == "__main__":
    main()