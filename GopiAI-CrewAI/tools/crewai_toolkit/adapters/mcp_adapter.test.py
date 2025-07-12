import unittest
from unittest.mock import patch, MagicMock

from crewai_tools.mcp_server import MCPServerAdapter

class TestMCPServerAdapter(unittest.TestCase):

    @patch("crewai_tools.mcp_server.MCP_AVAILABLE", False)
    @patch("crewai_tools.mcp_server.click.confirm", return_value=False)
    def test_init_mcp_not_available_no_install(self, mock_confirm):
        with self.assertRaises(ImportError):
            MCPServerAdapter({})

    @patch("crewai_tools.mcp_server.MCP_AVAILABLE", True)
    @patch("crewai_tools.mcp_server.MCPAdapt")
    def test_init_success(self, mock_mcp_adapt):
        adapter_instance = MagicMock()
        mock_mcp_adapt.return_value = adapter_instance
        adapter_instance.__enter__.return_value = ["tool1", "tool2"]
        mcp_server = MCPServerAdapter({})
        self.assertIsNotNone(mcp_server._adapter)
        self.assertIsNotNone(mcp_server._tools)

    @patch("crewai_tools.mcp_server.MCP_AVAILABLE", True)
    @patch("crewai_tools.mcp_server.MCPAdapt")
    def test_tools_property_success(self, mock_mcp_adapt):
        adapter_instance = MagicMock()
        mock_mcp_adapt.return_value = adapter_instance
        adapter_instance.__enter__.return_value = ["tool1", "tool2"]
        mcp_server = MCPServerAdapter({})
        tools = mcp_server.tools
        self.assertEqual(len(tools), 2)

    @patch("crewai_tools.mcp_server.MCP_AVAILABLE", True)
    @patch("crewai_tools.mcp_server.MCPAdapt")
    def test_tools_property_before_start(self, mock_mcp_adapt):
        adapter_instance = MagicMock()
        mock_mcp_adapt.return_value = adapter_instance
        adapter_instance.__enter__.return_value = ["tool1", "tool2"]
        mcp_server = MCPServerAdapter({})
        mcp_server._tools = None
        with self.assertRaises(ValueError):
            _ = mcp_server.tools

    @patch("crewai_tools.mcp_server.MCP_AVAILABLE", True)
    @patch("crewai_tools.mcp_server.MCPAdapt")
    def test_stop(self, mock_mcp_adapt):
        adapter_instance = MagicMock()
        mock_mcp_adapt.return_value = adapter_instance
        adapter_instance.__enter__.return_value = ["tool1", "tool2"]
        mcp_server = MCPServerAdapter({})
        mcp_server.stop()
        adapter_instance.__exit__.assert_called_once()