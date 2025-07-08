"""
Test script for verifying memory system functionality in GopiAI.

This script tests the memory system independently of the UI.
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
        logging.FileHandler('memory_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_memory_basic():
    """Basic tests for the memory system."""
    try:
        # Import the memory manager from the correct location
        import sys
        sys.path.append(str(Path(__file__).parent.parent))  # Add project root to path
        from gopiai.ui.memory.manager import MemoryManager
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize memory manager with test directory
            memory_manager = MemoryManager(data_dir=temp_dir)
            
            # Test 1: Basic initialization
            logger.info("=== Test 1: Memory Manager Initialization ===")
            assert memory_manager is not None
            logger.info("✅ Memory manager initialized successfully")
            
            # Test 2: Add a message
            logger.info("\n=== Test 2: Add Message ===")
            test_session = "test_session_123"
            test_message = "This is a test message for memory system"
            
            message_id = memory_manager.add_message(
                session_id=test_session,
                role="user",
                content=test_message
            )
            
            assert message_id is not None
            logger.info(f"✅ Added test message with ID: {message_id}")
            
            # Test 3: Retrieve message history
            logger.info("\n=== Test 3: Get Message History ===")
            history = memory_manager.get_chat_history(session_id=test_session)
            
            assert len(history) == 1
            assert history[0]['content'] == test_message
            logger.info("✅ Successfully retrieved message history")
            
            # Test 4: Search messages
            logger.info("\n=== Test 4: Search Messages ===")
            results = memory_manager.search_memory("test message", limit=1)
            
            assert len(results) > 0
            assert "test message" in results[0]['content'].lower()
            logger.info("✅ Successfully searched messages")
            
            # Test 5: Get statistics
            logger.info("\n=== Test 5: Get Statistics ===")
            stats = memory_manager.get_stats()
            
            assert 'total_messages' in stats
            assert stats['total_messages'] > 0
            logger.info(f"✅ Memory stats: {stats}")
            
            logger.info("\n✅ All memory tests passed!")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    logger.info("Starting memory system tests...")
    sys.exit(test_memory_basic())
