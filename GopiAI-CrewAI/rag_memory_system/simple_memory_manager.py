#!/usr/bin/env python3
"""
🧠 Server-Side Simple Memory Manager for GopiAI RAG

Handles txtai embeddings for long-term semantic memory.
- Initializes a persistent vector store.
- Provides methods to add and search for memories.
- Uses a singleton pattern to maintain one instance.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Txtai Dependency Check ---
try:
    from txtai.embeddings import Embeddings
    txtai_available = True
except ImportError:
    logger.warning("⚠️ txtai is not installed. Semantic memory will be disabled. Please run 'pip install txtai[faiss]'")
    Embeddings = None
    txtai_available = False

class SimpleMemoryManager:
    """Manages the persistent semantic memory using txtai."""

    def __init__(self):
        """Initializes the memory manager and the embeddings index."""
        self.embeddings: Optional[Embeddings] = None
        self.data_dir = Path.home() / ".gopiai" / "memory"
        self.embeddings_path = self.data_dir / "vectors"
        
        if txtai_available:
            self._init_embeddings()

    def _init_embeddings(self):
        """Initializes txtai embeddings with persistent storage."""
        if os.getenv("GOPI_DISABLE_EMBEDDINGS", "false").lower() == "true":
            logger.info("Embeddings are disabled by GOPI_DISABLE_EMBEDDINGS environment variable.")
            return

        try:
            self.embeddings_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initializing embeddings at {self.embeddings_path.as_posix()}")

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
                "backend": "faiss" if faiss_avx2 else "annoy",
                "store": True # Ensure index is stored within the object
            }
            
            self.embeddings = Embeddings(config)
            
            if (self.embeddings_path / "config").exists():
                self.embeddings.load(self.embeddings_path.as_posix())
                logger.info(f"✅ Loaded existing txtai embeddings from: {self.embeddings_path.as_posix()}")
            else:
                logger.info("No existing embeddings found, creating a new index.")

        except Exception as e:
            logger.error(f"❌ Failed to initialize txtai embeddings: {e}", exc_info=True)
            self.embeddings = None

    def add_message(self, role: str, content: str) -> None:
        """Adds a message to the semantic memory."""
        if not self.embeddings or not content.strip():
            return

        try:
            message_id = str(uuid.uuid4())
            message_object = {
                "id": message_id,
                "role": role,
                "content": content,
                "timestamp": self.get_current_timestamp()
            }
            
            # Upsert into embeddings index
            self.embeddings.upsert([(message_id, message_object)])
            self._save_embeddings()
            logger.info(f"Added message from '{role}' to semantic memory.")

        except Exception as e:
            logger.error(f"Error adding message to embeddings: {e}", exc_info=True)

    def search(self, query: str, limit: int = 5, min_score: float = 0.1) -> List[Tuple[str, float]]:
        """
        Searches the memory for a given query.
        Returns a list of (text, score) tuples.
        """
        if not self.embeddings or self.embeddings.count() == 0:
            logger.warning("Search unavailable - vector store is empty or not initialized.")
            return []

        try:
            # Use a safer query format for txtai
            safe_query = query.replace("'", "''")
            results = self.embeddings.search(f"select text, score from txtai where similar('{safe_query}') and score >= {min_score} limit {limit}")
            
            # The result from txtai is a list of dicts {'text': ..., 'score': ...}
            # We need to convert it to a list of tuples (text, score)
            search_results = [(res['text'], res['score']) for res in results]
            
            logger.info(f"Found {len(search_results)} results for query: '{query[:30]}...' (min_score={min_score})")
            return search_results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}", exc_info=True)
            return []

    def _save_embeddings(self):
        """Saves the embeddings index to disk."""
        if self.embeddings:
            try:
                self.embeddings.save(self.embeddings_path.as_posix())
                logger.info(f"Saved embeddings to {self.embeddings_path.as_posix()}")
            except Exception as e:
                logger.error(f"Error saving embeddings: {e}", exc_info=True)

    @staticmethod
    def get_current_timestamp() -> str:
        return datetime.utcnow().isoformat()

# --- Singleton Instance ---
_memory_manager_instance = None

def get_memory_manager() -> SimpleMemoryManager:
    """Returns the singleton instance of the SimpleMemoryManager."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        logger.info("Creating new SimpleMemoryManager instance.")
        _memory_manager_instance = SimpleMemoryManager()
    return _memory_manager_instance

# Example usage for direct execution
if __name__ == '__main__':
    print("Running SimpleMemoryManager directly for testing...")
    manager = get_memory_manager()
    
    if manager.embeddings:
        print(f"Embeddings loaded. Total items in index: {manager.embeddings.count()}")
        
        # Add some test data
        print("\nAdding test messages...")
        manager.add_message("user", "My favorite color is blue.")
        manager.add_message("assistant", "Blue is a great color for the sky.")
        manager.add_message("user", "I work as a software developer.")
        
        # Search for related concepts
        print("\nSearching for 'what is my job?'...")
        results = manager.search("what is my job?", limit=2)
        for text, score in results:
            print(f"- Found: '{text}' (Score: {score:.4f})")
            
        print("\nSearching for 'what do I like?'...")
        results = manager.search("what do I like?", limit=2)
        for text, score in results:
            print(f"- Found: '{text}' (Score: {score:.4f})")
        
        print(f"\nTotal items in index after adding: {manager.embeddings.count()}")
    else:
        print("\nCould not run tests because embeddings are not available.")
