"""
Direct test of the memory system without UI dependencies.
"""

import sys
import os
import logging
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('memory_direct_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_memory_manager():
    """Test the memory manager directly."""
    try:
        # Add the project root to Python path
        project_root = str(Path(__file__).parent.absolute())
        sys.path.insert(0, project_root)
        
        # Import the memory manager from the UI package
        logger.info("Importing MemoryManager...")
        from gopiai.ui.memory.manager import MemoryManager, get_memory_manager
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Using temporary directory: {temp_dir}")
            
            # Initialize memory manager using the global instance
            logger.info("Initializing MemoryManager...")
            memory = get_memory_manager()
            memory.data_dir = Path(temp_dir)  # Override data directory for testing
            
            # Test 1: Add a message
            logger.info("\n=== Test 1: Add Message ===")
            test_session = "test_session_123"
            test_message = "This is a test message for memory system"
            
            message_id = memory.add_message(
                session_id=test_session,
                role="user",
                content=test_message
            )
            
            logger.info(f"Added message with ID: {message_id}")
            assert message_id is not None
            
            # Test 2: Get message history
            logger.info("\n=== Test 2: Get Message History ===")
            history = memory.get_chat_history(session_id=test_session)
            
            logger.info(f"Retrieved {len(history)} messages")
            assert len(history) == 1
            assert history[0]['content'] == test_message
            
            # Test 3: Search messages
            logger.info("\n=== Test 3: Search Messages ===")
            results = memory.search_memory("test message", limit=1)
            
            logger.info(f"Found {len(results)} results")
            assert len(results) > 0
            assert "test message" in results[0]['content'].lower()
            
            # Test 4: Get statistics
            logger.info("\n=== Test 4: Get Statistics ===")
            stats = memory.get_stats()
            
            logger.info(f"Memory stats: {stats}")
            assert 'total_messages' in stats
            assert stats['total_messages'] > 0
            
            logger.info("\n✅ All tests passed!")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    logger.info("Starting memory manager tests...")
    sys.exit(test_memory_manager())
