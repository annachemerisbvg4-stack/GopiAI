import unittest
import os
import json
from unittest.mock import patch, mock_open
from crewai_tools.gopiai_memory.gopiai_memory import GopiAIMemoryTool

class TestGopiAIMemoryTool(unittest.TestCase):

    def setUp(self):
        self.test_memory_file = "test_memory.json"
        self.tool = GopiAIMemoryTool(local_memory_file=self.test_memory_file)
        self.tool.init_files()

    def tearDown(self):
        if os.path.exists(self.test_memory_file):
            os.remove(self.test_memory_file)

    def test_store_and_search_memory(self):
        self.tool._run("store", "test_key", "test data", "general", 5, "test_conversation")
        result = self.tool._run("search", "test_key", conversation_id="test_conversation")
        self.assertIn("test data", result)

    def test_retrieve_memory(self):
        self.tool._run("store", "retrieve_key", "retrieve data", "general", 5, "test_conversation")
        result = self.tool._run("retrieve", "retrieve_key", conversation_id="test_conversation")
        self.assertIn("retrieve data", result)

    def test_list_memories(self):
        self.tool._run("store", "list_key", "list data", "code", 5, "test_conversation")
        result = self.tool._run("list", category="code", conversation_id="test_conversation")
        self.assertIn("code", result)

    def test_delete_memory(self):
        self.tool._run("store", "delete_key", "delete data", "general", 5, "test_conversation")
        result = self.tool._run("delete", "delete_key", conversation_id="test_conversation")
        self.assertIn("удалена", result)
        result = self.tool._run("retrieve", "delete_key", conversation_id="test_conversation")
        self.assertIn("не найдена", result)

    def test_new_conversation_and_history(self):
        conversation_id = self.tool._run("new_conversation")
        self.assertIsInstance(conversation_id, str)
        self.tool._run("store", "user", "Hello", "conversation", 5, conversation_id)
        history = self.tool._run("get_conversation_history", conversation_id=conversation_id)
        self.assertIn("USER: Hello", history)