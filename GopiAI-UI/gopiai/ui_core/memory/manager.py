"""
Standalone Memory Manager for GopiAI

This module provides a unified interface for managing both short-term (chat history)
and long-term (semantic search) memory using txtai, without any UI dependencies.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified memory management for GopiAI (standalone version)
    
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
        
        # Initialize emotional classifier (simplified without UI deps)
        self.emotion_classifier = None
        self._init_emotion_classifier()
        
        # Load existing data
        self._load_data()
        
        # Initialize txtai embeddings
        self._init_embeddings()
    
    def _init_emotion_classifier(self):
        """Initialize a simplified emotion classifier"""
        try:
            # Simplified emotion classifier without UI dependencies
            class SimpleEmotionClassifier:
                def predict_emotion(self, text):
                    return {
                        'emotion': 'neutral',
                        'confidence': 0.0,
                        'emotion_analyzer_available': False
                    }
            
            self.emotion_classifier = SimpleEmotionClassifier()
            logger.info("Initialized simplified emotion classifier")
            
        except Exception as e:
            logger.warning(f"Could not initialize emotion classifier: {e}")
            self.emotion_classifier = None
    
    def _load_data(self):
        """Load existing data from disk"""
        # Load chats
        if self.chats_file.exists():
            try:
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
                logger.info(f"Loaded {len(self.chats)} chat messages from disk")
            except Exception as e:
                logger.error(f"Error loading chats: {e}")
                self.chats = []
        
        # Load sessions
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from disk")
            except Exception as e:
                logger.error(f"Error loading sessions: {e}")
                self.sessions = {}
    
    def _save_data(self):
        """Save data to disk"""
        try:
            # Save chats
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
            
            # Save sessions
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def _init_embeddings(self):
        """Initialize txtai embeddings for semantic search with persistent storage"""
        try:
            from txtai.embeddings import Embeddings
            
            # Create directory for vector storage if it doesn't exist
            vectors_dir = self.data_dir / "vectors"
            vectors_dir.mkdir(exist_ok=True)
            
            # Configure embeddings with persistent storage
            self.embeddings = Embeddings({
                'path': 'sentence-transformers/all-MiniLM-L6-v2',
                'gpu': False,  # Disable GPU for testing
                'batch': 8,
                'content': True,  # Store original content
                'store': True,    # Enable persistent storage
                'path': str(vectors_dir)  # Store vectors in persistent location
            })
            
            # If we have chats but no vectors, index existing messages
            if self.chats and not any(vectors_dir.iterdir()):
                logger.info("No existing vector index found, creating new index...")
                self._index_messages()
            elif self.chats:
                logger.info("Found existing vector index, loading...")
                
            logger.info(f"Initialized txtai embeddings with {len(self.chats)} messages")
            
        except ImportError:
            logger.warning("txtai not available, semantic search disabled")
            self.embeddings = None
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            self.embeddings = None
    
    def _index_messages(self):
        """Index chat messages for semantic search and persist to disk"""
        if not self.embeddings or not self.chats:
            return
            
        try:
            # Create documents for indexing
            documents = []
            for i, msg in enumerate(self.chats):
                if 'content' in msg and 'role' in msg and 'id' in msg:
                    documents.append((
                        msg['id'],  # Use message ID as document ID for consistency
                        msg['content'],
                        {
                            'role': msg['role'],
                            'timestamp': msg.get('timestamp', ''),
                            'session_id': msg.get('session_id', '')
                        }
                    ))
            
            # Index documents in batches to handle large chat histories
            if documents:
                logger.info(f"Indexing {len(documents)} messages...")
                self.embeddings.upsert(documents)  # Use upsert to handle updates
                self.embeddings.save()  # Explicitly save to disk
                logger.info(f"Successfully indexed {len(documents)} messages")
                
        except Exception as e:
            logger.error(f"Error indexing messages: {e}")
            raise  # Re-raise to allow caller to handle the error
    
    def add_message(self, session_id: str, role: str, content: str, **kwargs) -> str:
        """
        Add a message to the chat history
        
        Args:
            session_id: ID of the chat session
            role: 'user' or 'assistant'
            content: Message content
            **kwargs: Additional message metadata
            
        Returns:
            str: Message ID
        """
        message_id = str(len(self.chats))
        timestamp = kwargs.get('timestamp')
        
        # Create message
        message = {
            'id': message_id,
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': timestamp or str(datetime.now()),
            **kwargs
        }
        
        # Add emotion analysis if available
        if self.emotion_classifier and role == 'user':
            try:
                emotion_result = self.emotion_classifier.predict_emotion(content)
                message.update({
                    'emotion': emotion_result.get('emotion'),
                    'emotion_confidence': emotion_result.get('confidence')
                })
            except Exception as e:
                logger.warning(f"Error analyzing emotion: {e}")
        
        # Add to chats
        self.chats.append(message)
        
        # Update session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created_at': message['timestamp'],
                'updated_at': message['timestamp'],
                'message_count': 0
            }
        
        self.sessions[session_id]['updated_at'] = message['timestamp']
        self.sessions[session_id]['message_count'] += 1
        
        # Index for semantic search if embeddings are available
        if self.embeddings is not None:
            try:
                self.embeddings.upsert([(
                    message_id,  # Use message ID as document ID
                    content,
                    {
                        'role': role,
                        'timestamp': message['timestamp'],
                        'session_id': session_id
                    }
                )])
                # Save the index to disk after each update
                self.embeddings.save()
                logger.debug(f"Indexed message {message_id} in session {session_id}")
            except Exception as e:
                logger.error(f"Error indexing message: {e}")
        
        # Save chat history to disk
        try:
            self._save_data()
        except Exception as e:
            logger.error(f"Error saving chat data: {e}")
        
        return message_id
    
    def get_chat_history(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get chat history for a session
        
        Args:
            session_id: ID of the chat session
            limit: Maximum number of messages to return (most recent first)
            
        Returns:
            List of message dictionaries
        """
        # Filter messages by session
        session_messages = [
            msg for msg in self.chats 
            if msg.get('session_id') == session_id
        ]
        
        # Sort by timestamp (newest first)
        session_messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply limit if specified
        if limit is not None:
            session_messages = session_messages[:limit]
        
        # Sort back to chronological order
        session_messages.sort(key=lambda x: x.get('timestamp', ''))
        
        return session_messages
    
    def search_memory(self, query: str, limit: int = 5, **filters) -> List[Dict[str, Any]]:
        """
        Search chat history using semantic search
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            **filters: Additional filters (e.g., role='user')
            
        Returns:
            List of matching messages with relevance scores
        """
        if not self.embeddings:
            return []
            
        try:
            # Search with filters
            results = self.embeddings.search(
                f"select id, text, score from txtai where similar('{query}') "
                f"and role = '{filters.get('role', '')}'" if 'role' in filters else f"select id, text, score from txtai where similar('{query}')",
                limit=limit
            )
            
            # Get full message details
            messages = []
            for result in results:
                msg_id = result['id']
                if 0 <= int(msg_id) < len(self.chats):
                    message = dict(self.chats[int(msg_id)])
                    message['score'] = result['score']
                    messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dictionary containing memory statistics
        """
        return {
            'total_messages': len(self.chats),
            'total_sessions': len(self.sessions),
            'embeddings_available': self.embeddings is not None,
            'emotion_analyzer_available': self.emotion_classifier is not None,
            'data_dir': str(self.data_dir.absolute())
        }
    
    def clear_memory(self):
        """Clear all memory data"""
        self.chats = []
        self.sessions = {}
        if self.embeddings:
            self.embeddings.delete([str(i) for i in range(len(self.chats))])
        self._save_data()
        logger.info("Cleared all memory data")


# Global instance
memory_manager = MemoryManager()

def get_memory_manager() -> MemoryManager:
    """
    Get the global memory manager instance
    
    Returns:
        MemoryManager: Global memory manager instance
    """
    return memory_manager
