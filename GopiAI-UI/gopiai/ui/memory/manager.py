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
        self.embeddings = None
        
        # Initialize emotional classifier
        self.emotion_classifier = None
        self._init_emotion_classifier()
        
        # Load existing data
        self._load_data()
        
        # Initialize txtai embeddings
        self._init_embeddings()
    
    def _init_emotion_classifier(self):
        """Initialize the emotion classifier"""
        try:
            from ..components.emotional_classifier import EmotionalClassifier
            self.emotion_classifier = EmotionalClassifier()
            logger.info("✅ Emotional classifier initialized")
        except ImportError:
            try:
                # Fallback to simple classifier
                from simple_emotion_classifier import get_emotion_classifier
                self.emotion_classifier = get_emotion_classifier()
                logger.info("✅ Simple emotion classifier initialized")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize emotion classifier: {e}")
    
    def _init_embeddings(self):
        """Initialize txtai embeddings"""
        try:
            from txtai.embeddings import Embeddings
            self.embeddings = Embeddings({"path": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"})
            logger.info("✅ txtai embeddings initialized")
            
            # Update embeddings with existing messages
            if self.chats:
                self._update_embeddings()
                
        except ImportError as e:
            logger.warning(f"⚠️ txtai not available: {e}")
    
    def _load_data(self):
        """Load existing chat and session data"""
        # Load chats
        if self.chats_file.exists():
            try:
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
                logger.info(f"Loaded {len(self.chats)} messages from {self.chats_file}")
            except Exception as e:
                logger.error(f"Error loading chats: {e}")
                self.chats = []
        
        # Load sessions
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
            # Save chats
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
                
            # Save sessions
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def _update_embeddings(self):
        """Update embeddings with current chat messages"""
        if not self.embeddings or not self.chats:
            return
            
        try:
            # Create index from messages
            texts = [msg['content'] for msg in self.chats]
            
            # Clear existing index if any
            if hasattr(self.embeddings, 'unindex'):
                self.embeddings.unindex(range(len(texts)))
                
            # Create new index
            self.embeddings.index([(i, text, None) for i, text in enumerate(texts)])
            
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
    
    def add_message(self, session_id: str, role: str, content: str, **metadata) -> str:
        """
        Add a message to the chat history
        
        Args:
            session_id: ID of the chat session
            role: 'user' or 'assistant'
            content: Message content
            **metadata: Additional metadata to store with the message
            
        Returns:
            str: ID of the added message
        """
        import uuid
        from datetime import datetime
        
        # Create session if it doesn't exist
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
        
        # Analyze emotion for user messages
        emotion_data = {}
        if role == 'user' and self.emotion_classifier:
            try:
                emotion_data = self.emotion_classifier.analyze_emotion(content)
                logger.debug(f"Emotion analysis: {emotion_data}")
            except Exception as e:
                logger.warning(f"Error in emotion analysis: {e}")
        
        # Create message
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
        
        # Add to chat history
        self.chats.append(message)
        self.sessions[session_id]['message_count'] += 1
        
        # Update embeddings if this is a user message
        if role == 'user' and self.embeddings:
            try:
                self.embeddings.upsert([(len(self.chats)-1, content, None)])
            except Exception as e:
                logger.error(f"Error updating embeddings with new message: {e}")
        
        # Save data
        self._save_data()
        
        return message['id']
    
    def search_memory(self, query: str, limit: int = 5, min_score: float = 0.0) -> List[Dict]:
        """
        Search the chat history using semantic search
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            min_score: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of matching messages with scores
        """
        if not self.embeddings or not self.chats:
            return []
            
        try:
            # Perform semantic search
            results = self.embeddings.search(query, limit=limit)
            
            # Format results
            search_results = []
            for score, idx in results:
                if idx < len(self.chats):
                    msg = self.chats[idx]
                    search_results.append({
                        'id': msg['id'],
                        'session_id': msg['session_id'],
                        'role': msg['role'],
                        'content': msg['content'],
                        'timestamp': msg['timestamp'],
                        'score': float(score),
                        'emotion': msg.get('emotion', 'neutral'),
                        'sentiment': msg.get('sentiment', 'neutral')
                    })
            
            # Filter by min_score
            if min_score > 0:
                search_results = [r for r in search_results if r['score'] >= min_score]
                
            return search_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def get_chat_history(self, session_id: str = None, limit: int = 20) -> List[Dict]:
        """
        Get chat history for a session or all sessions
        
        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        if session_id:
            messages = [msg for msg in self.chats if msg['session_id'] == session_id]
        else:
            messages = self.chats[:]
            
        # Sort by timestamp (newest first)
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply limit
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
            # Remove session
            del self.sessions[session_id]
            
            # Remove associated messages
            self.chats = [msg for msg in self.chats if msg['session_id'] != session_id]
            
            # Save changes
            self._save_data()
            self._update_embeddings()
            
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'total_messages': len(self.chats),
            'total_sessions': len(self.sessions),
            'embeddings_available': self.embeddings is not None,
            'emotion_analyzer_available': self.emotion_classifier is not None,
            'data_dir': str(self.data_dir.absolute())
        }


# Global instance
memory_manager = MemoryManager()

def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance"""
    return memory_manager
