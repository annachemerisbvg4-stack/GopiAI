#!/usr/bin/env python3
"""
Просмотр содержимого памяти GOPI_AI
"""

import json
from pathlib import Path

def view_memory():
    """Показать все данные в памяти"""
    
    memory_file = Path("C:/Users/crazy/GOPI_AI_MODULES/conversations/chats.json")
    
    if not memory_file.exists():
        print("❌ Файл памяти не найден!")
        return
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chats = data.get('chats', [])
        sessions = data.get('sessions', {})
        
        print("🧠 СОДЕРЖИМОЕ ПАМЯТИ GOPI_AI")
        print("=" * 60)
        print(f"📊 Всего сообщений: {len(chats)}")
        print(f"📁 Всего сессий: {len(sessions)}")
        print()
        
        # Показываем сессии
        print("📂 СЕССИИ:")
        print("-" * 30)
        for session_id, session in sessions.items():
            print(f"🗂️  {session['title']}")
            print(f"   ID: {session_id}")
            print(f"   Создана: {session['created_at']}")
            print(f"   Сообщений: {session['message_count']}")
            print()
        
        # Показываем все сообщения
        print("💬 ВСЕ СООБЩЕНИЯ:")
        print("-" * 40)
        
        for i, chat in enumerate(chats, 1):
            # Находим название сессии
            session_title = "Unknown Session"
            for session_id, session in sessions.items():
                if session_id == chat['session_id']:
                    session_title = session['title']
                    break
            
            role_emoji = "👤" if chat['role'] == 'user' else "🤖"
            print(f"{i}. [{session_title}] {role_emoji} {chat['role'].upper()}:")
            print(f"   \"{chat['content']}\"")
            print(f"   {chat['timestamp']}")
            print()
        
        if not chats:
            print("📭 Пока что сообщений нет!")
            
    except Exception as e:
        print(f"❌ Ошибка чтения памяти: {e}")

if __name__ == "__main__":
    view_memory()
