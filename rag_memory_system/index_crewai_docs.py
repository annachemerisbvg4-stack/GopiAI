#!/usr/bin/env python3
"""
📚 Скрипт индексации документации CrewAI для RAG системы
Создает индекс документации для последующего поиска
"""

import os
import sys
from pathlib import Path
import time
import json

# Добавляем путь к корневой директории
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Импортируем модули RAG системы
try:
    from rag_memory_system import index_documents, search_documents
except ImportError as e:
    print(f"❌ Ошибка импорта rag_memory_system: {e}")
    print("Убедитесь, что вы выполняете скрипт из корректной директории")
    sys.exit(1)

def index_crewai_documentation():
    """Индексирует документацию CrewAI для RAG системы"""
    print("🔍 Индексация документации CrewAI...")
    
    # Путь к документации
    doc_path = os.path.join(parent_dir, "GopiAI-CrewAI", "crewai_complete_documentation.md")
    if not os.path.exists(doc_path):
        print(f"❌ Документация не найдена: {doc_path}")
        return False
        
    print(f"✅ Документация найдена: {doc_path}")
    
    # Читаем документацию
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_text = f.read()
            
        print(f"📊 Размер документации: {len(doc_text)} символов")
        
        # Разбиваем на чанки с перекрытием
        chunks = []
        chunk_size = 1000
        overlap = 200
        
        for i in range(0, len(doc_text), chunk_size - overlap):
            chunk = doc_text[i:i+chunk_size]
            chunk_id = f"crewai_doc_{i//(chunk_size - overlap)}"
            
            # Контекстная информация (номер страницы и т.д.)
            metadata = {
                "type": "crewai_documentation",
                "chunk_id": chunk_id,
                "position": i,
                "source": "crewai_complete_documentation.md"
            }
            
            chunks.append({
                "id": chunk_id,
                "text": chunk,
                "metadata": metadata
            })
        
        print(f"📄 Создано {len(chunks)} фрагментов документации")
        
        # Индексируем чанки
        index_documents(chunks, index_name="crewai_docs")
        
        print("✅ Индексация успешно завершена")
        
        # Проверяем индекс простым запросом
        results = search_documents("How to create a crew with multiple agents", 
                                   index_name="crewai_docs",
                                   limit=1)
        
        if results:
            print("✅ Тестовый поиск успешен")
            print(f"Найден фрагмент: {results[0]['id']}")
        else:
            print("⚠️ Тестовый поиск не дал результатов")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при индексации: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    index_crewai_documentation()