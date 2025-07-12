"""
Memory Manager for GopiAI

This module provides a unified interface for managing both short-term (chat history)
and long-term (semantic search) memory using txtai.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified memory management for GopiAI
    
    Handles both short-term chat history and long-term semantic memory
    using txtai for semantic search capabilities.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize the memory manager"""
        # Set up data directory
        if data_dir is None:
            self.data_dir = Path.home() / ".gopiai" / "memory"
        else:
            self.data_dir = Path(data_dir)
            
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize file paths
        self.chats_file = self.data_dir / "chats.json"
        self.sessions_file = self.data_dir / "sessions.json"
        
        # Initialize data structures
        self.chats = []
        self.sessions = {}
        
        # Initialize emotional classifier
        self.emotion_classifier = None
        self._init_emotion_classifier()
        
        # Load existing data
        self._load_data()
    
    def _init_emotion_classifier(self):
        """Initialize the emotion classifier"""
        try:
            # First try to import the simple emotion classifier from the project root
            import sys
            from pathlib import Path
            
            # Add the project root to Python path if not already there
            project_root = str(Path(__file__).parent.parent.parent.parent.absolute())
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
                
            from simple_emotion_classifier import SimpleEmotionClassifier
            self.emotion_classifier = SimpleEmotionClassifier()
            logger.info("✅ Simple emotion classifier initialized")
        except ImportError as e:
            try:
                # Fallback to trying to import from the standard location
                from simple_emotion_classifier import get_emotion_classifier
                self.emotion_classifier = get_emotion_classifier()
                logger.info("✅ Simple emotion classifier (legacy) initialized")
            except ImportError:
                # If all else fails, log a warning and continue without emotion classification
                logger.warning("⚠️ Could not initialize emotion classifier. Emotion analysis will be disabled.")
                self.emotion_classifier = None



    def _load_data(self):
        """Load existing chat and session data"""
        if self.chats_file.exists():
            try:
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
                logger.info(f"Loaded {len(self.chats)} messages from {self.chats_file}")
            except Exception as e:
                logger.error(f"Error loading chats: {e}")
                self.chats = []
        
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from {self.sessions_file}")
            except Exception as e:
                logger.error(f"Error loading sessions: {e}")
                self.sessions = {}
    
    def _save_data(self):
        """Save chat and session data to disk"""
        try:
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
                
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")


    
    def add_message(self, session_id: str, role: str, content: str, **metadata) -> str:
        """
        Add a message to the chat history
        """
        import uuid
        from datetime import datetime
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'id': session_id,
                'title': f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'message_count': 0
            }
        else:
            self.sessions[session_id]['updated_at'] = datetime.now().isoformat()
        
        emotion_data = {}
        if role == 'user' and self.emotion_classifier:
            try:
                emotion_data = self.emotion_classifier.analyze_emotion(content)
            except Exception as e:
                logger.warning(f"Error in emotion analysis: {e}")
        
        message = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion_data.get('emotion', 'neutral'),
            'emotion_confidence': emotion_data.get('confidence', 0.0),
            'sentiment': emotion_data.get('sentiment', 'neutral'),
            **metadata
        }
        
        self.chats.append(message)
        self.sessions[session_id]['message_count'] += 1
        

        
        self._save_data()
        return message['id']
    

    
    def get_chat_history(self, session_id: str = None, limit: int = 20) -> List[Dict]:
        """Get chat history for a session or all sessions"""
        if session_id:
            messages = [msg for msg in self.chats if msg['session_id'] == session_id]
        else:
            messages = self.chats[:]
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return messages[:limit]
    
    def get_session(self, session_id: str) -> Dict:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self, limit: int = 20) -> List[Dict]:
        """List all chat sessions"""
        sessions = list(self.sessions.values())
        sessions.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return sessions[:limit]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and its messages"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.chats = [msg for msg in self.chats if msg['session_id'] != session_id]
            self._save_data()
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'total_messages': len(self.chats),
            'total_sessions': len(self.sessions),
            'embeddings_available': False,
            'emotion_analyzer_available': self.emotion_classifier is not None,
            'data_dir': str(self.data_dir.absolute())
        }

# Global instance
memory_manager = MemoryManager()

def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance"""
    return memory_manager
