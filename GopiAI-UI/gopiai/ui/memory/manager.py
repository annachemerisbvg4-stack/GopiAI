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

    def _init_embeddings(self):
        """Initialize txtai embeddings with persistent storage."""
        if os.getenv("GOPI_DISABLE_EMBEDDINGS", "false").lower() == "true":
            logger.info("Embeddings are disabled by GOPI_DISABLE_EMBEDDINGS environment variable.")
            self.embeddings = None
            return

        try:
            from txtai.embeddings import Embeddings
            
            embeddings_path = self.data_dir / "vectors"
            logger.info(f"Initializing embeddings at {embeddings_path.as_posix()}")

            faiss_avx2 = False
            try:
                import faiss
                faiss_avx2 = hasattr(faiss, "StandardGpuResources") or "AVX2" in faiss.get_compile_options()
                logger.info(f"FAISS found, AVX2 support: {faiss_avx2}")
            except ImportError:
                logger.warning("FAISS not found, falling back to Annoy. For better performance, install 'faiss-cpu' or 'faiss-gpu'.")

            config = {
                "path": "sentence-transformers/nli-mpnet-base-v2",
                "content": True,
                "objects": True,
                "backend": "faiss" if faiss_avx2 else "annoy"
            }
            
            self.embeddings = Embeddings(config)
            
            if (embeddings_path / "config").exists():
                self.embeddings.load(embeddings_path.as_posix())
                logger.info(f"✅ Loaded existing txtai embeddings from: {embeddings_path.as_posix()}")
            else:
                logger.info("No existing embeddings found, will create a new index.")

            if self.chats:
                self._update_embeddings()

        except ImportError:
            logger.warning("⚠️ txtai is not installed. Semantic search will be disabled. Please run 'pip install txtai'.")
            self.embeddings = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize txtai embeddings: {e}", exc_info=True)
            self.embeddings = None

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

    def _save_embeddings(self):
        """Save the embeddings index to disk."""
        if self.embeddings:
            try:
                embeddings_path = self.data_dir / "vectors"
                self.embeddings.save(embeddings_path.as_posix())
                logger.info(f"Saved embeddings to {embeddings_path.as_posix()}")
            except Exception as e:
                logger.error(f"Error saving embeddings: {e}")

    def _update_embeddings(self):
        """Update embeddings with current chat messages."""
        if not self.embeddings or not self.chats:
            return
            
        try:
            upserts = [(msg['id'], msg) for msg in self.chats]
            self.embeddings.upsert(upserts)
            self._save_embeddings()
            logger.info(f"Updated and saved {len(upserts)} items to embeddings index.")
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
    
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
        
        if self.embeddings:
            try:
                self.embeddings.upsert([(message['id'], message)])
                self._save_embeddings() # Save after every addition
            except Exception as e:
                logger.error(f"Error updating embeddings with new message: {e}")
        
        self._save_data()
        return message['id']
    
    def search_memory(self, query: str, limit: int = 5, min_score: float = 0.0) -> List[Dict]:
        """
        Search the chat history using semantic search.
        """
        if not self.embeddings or self.embeddings.count() == 0:
            logger.warning("Search unavailable - vector store is empty or not initialized.")
            return []
            
        try:
            safe_query = query.replace("'", "''")
            results = self.embeddings.search(f"select object, score from txtai where similar('{safe_query}') limit {limit}")
            
            search_results = []
            for res in results:
                if res['score'] >= min_score:
                    message_object = res.get('object')
                    if message_object:
                        message_object['score'] = res['score']
                        search_results.append(message_object)
            
            logger.info(f"Found {len(search_results)} results for query: '{query[:30]}...' (min_score={min_score})")
            return search_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
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
