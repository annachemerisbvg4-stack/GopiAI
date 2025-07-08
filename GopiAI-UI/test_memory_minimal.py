"""
Minimal test of the memory manager core functionality.
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
        logging.FileHandler('memory_minimal_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_memory_minimal():
    """Minimal test of memory manager."""
    try:
        # Add the project root to Python path
        project_root = str(Path(__file__).parent.absolute())
        sys.path.insert(0, project_root)
        
        # Import the memory manager directly
        logger.info("Importing MemoryManager...")
        sys.modules['gopiai.ui.utils.icon_manager'] = type('FakeIconManager', (), {'get_icon': lambda *args, **kwargs: None})
        from gopiai.ui.memory.manager import MemoryManager
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Using temporary directory: {temp_dir}")
            
            # Initialize memory manager with test directory
            logger.info("Initializing MemoryManager...")
            memory = MemoryManager(data_dir=temp_dir)
            
            # Test 1: Basic initialization
            logger.info("\n=== Test 1: Memory Manager Initialization ===")
            assert memory is not None
            logger.info("✅ Memory manager initialized successfully")
            
            # Test 2: Add a message
            logger.info("\n=== Test 2: Add Message ===")
            test_session = "test_session_123"
            test_message = "This is a test message for memory system"
            
            message_id = memory.add_message(
                session_id=test_session,
                role="user",
                content=test_message
            )
            
            assert message_id is not None
            logger.info(f"✅ Added test message with ID: {message_id}")
            
            # Test 3: Get message history
            logger.info("\n=== Test 3: Get Message History ===")
            history = memory.get_chat_history(session_id=test_session)
            
            assert len(history) > 0
            assert history[0]['content'] == test_message
            logger.info("✅ Successfully retrieved message history")
            
            logger.info("\n✅ All minimal memory tests passed!")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    logger.info("Starting minimal memory tests...")
    sys.exit(test_memory_minimal())
