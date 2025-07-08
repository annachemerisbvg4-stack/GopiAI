"""
Test script for the standalone memory manager.
"""

import sys
import os
import logging
import tempfile
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('standalone_memory_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_standalone_memory():
    """Test the standalone memory manager."""
    try:
        # Add the project root to Python path
        project_root = str(Path(__file__).parent.absolute())
        sys.path.insert(0, project_root)
        
        # Import the standalone memory manager
        logger.info("Importing MemoryManager...")
        from gopiai.core.memory import MemoryManager
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Using temporary directory: {temp_dir}")
            
            # Initialize memory manager with test directory
            logger.info("Initializing MemoryManager...")
            memory = MemoryManager(data_dir=temp_dir)
            
            # Test 1: Basic initialization
            logger.info("\n=== Test 1: Memory Manager Initialization ===")
            assert memory is not None
            stats = memory.get_stats()
            logger.info(f"Memory stats: {stats}")
            logger.info("✅ Memory manager initialized successfully")
            
            # Test 2: Add a message
            logger.info("\n=== Test 2: Add Message ===")
            test_session = "test_session_123"
            test_message = "This is a test message for the standalone memory system"
            
            message_id = memory.add_message(
                session_id=test_session,
                role="user",
                content=test_message,
                timestamp=str(datetime.now())
            )
            
            assert message_id is not None
            logger.info(f"✅ Added test message with ID: {message_id}")
            
            # Test 3: Get message history
            logger.info("\n=== Test 3: Get Message History ===")
            history = memory.get_chat_history(session_id=test_session)
            
            assert len(history) > 0
            assert history[0]['content'] == test_message
            logger.info(f"Retrieved message: {history[0]['content']}")
            logger.info("✅ Successfully retrieved message history")
            
            # Test 4: Search messages (if embeddings are available)
            logger.info("\n=== Test 4: Search Messages ===")
            if stats['embeddings_available']:
                results = memory.search_memory("test message", limit=1)
                assert len(results) > 0
                logger.info(f"Search result: {results[0]['content']} (score: {results[0].get('score', 'N/A')})")
                logger.info("✅ Successfully searched messages")
            else:
                logger.warning("Skipping search test - embeddings not available")
            
            # Test 5: Get updated statistics
            logger.info("\n=== Test 5: Get Updated Statistics ===")
            updated_stats = memory.get_stats()
            logger.info(f"Updated stats: {updated_stats}")
            assert updated_stats['total_messages'] > 0
            assert updated_stats['total_sessions'] > 0
            logger.info("✅ Successfully retrieved updated statistics")
            
            logger.info("\n✅ All standalone memory tests passed!")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    logger.info("Starting standalone memory tests...")
    sys.exit(test_standalone_memory())
