import unittest
from typing import List, Optional
from crewai.tools import BaseTool
from crewai.tool_collection import ToolCollection

class MockTool(BaseTool):
    name: str = "MockTool"
    description: str = "A mock tool for testing."

class TestToolCollection(unittest.TestCase):
    def test_init(self):
        tools = [MockTool(name="tool1"), MockTool(name="tool2")]
        collection = ToolCollection(tools)
        self.assertEqual(len(collection), 2)
        self.assertEqual(collection["tool1"].name, "tool1")

    def test_getitem_string(self):
        tool = MockTool(name="test_tool")
        collection = ToolCollection([tool])
        self.assertEqual(collection["test_tool"], tool)

    def test_append(self):
        collection = ToolCollection()
        tool = MockTool(name="new_tool")
        collection.append(tool)
        self.assertIn("new_tool", collection._name_cache)
        self.assertEqual(collection["new_tool"], tool)

    def test_remove(self):
        tool1 = MockTool(name="tool1")
        tool2 = MockTool(name="tool2")
        collection = ToolCollection([tool1, tool2])
        collection.remove(tool1)
        self.assertNotIn("tool1", collection._name_cache)
        self.assertEqual(len(collection), 1)

    def test_pop(self):
        tool1 = MockTool(name="tool1")
        tool2 = MockTool(name="tool2")
        collection = ToolCollection([tool1, tool2])
        popped_tool = collection.pop()
        self.assertEqual(popped_tool.name, "tool2")
        self.assertNotIn("tool2", collection._name_cache)
        self.assertEqual(len(collection), 1)

if __name__ == '__main__':
    unittest.main()