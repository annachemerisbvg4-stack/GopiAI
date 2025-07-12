import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from embedchain.tools.youtube_channel_search import (
    FixedYoutubeChannelSearchToolSchema,
    YoutubeChannelSearchTool,
    YoutubeChannelSearchToolSchema,
)


class TestYoutubeChannelSearchTool(unittest.TestCase):
    def test_youtube_channel_search_tool_schema(self):
        schema = YoutubeChannelSearchToolSchema(
            youtube_channel_handle="@test_channel", search_query="test query"
        )
        self.assertEqual(schema.youtube_channel_handle, "@test_channel")
        self.assertEqual(schema.search_query, "test query")

    def test_fixed_youtube_channel_search_tool_schema(self):
        schema = FixedYoutubeChannelSearchToolSchema(search_query="test query")
        self.assertEqual(schema.search_query, "test query")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_youtube_channel_search_tool_init(self, mock_add):
        tool = YoutubeChannelSearchTool(youtube_channel_handle="@test_channel")
        mock_add.assert_called_once_with("@test_channel", data_type=DataType.YOUTUBE_CHANNEL)
        self.assertEqual(
            tool.description,
            "A tool that can be used to semantic search a query the @test_channel Youtube Channels content.",
        )
        self.assertEqual(tool.args_schema, FixedYoutubeChannelSearchToolSchema)

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_youtube_channel_search_tool_add(self, mock_add):
        tool = YoutubeChannelSearchTool()
        tool.add("test_channel")
        mock_add.assert_called_once_with("@test_channel", data_type=DataType.YOUTUBE_CHANNEL)

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_youtube_channel_search_tool_run(self, mock_run):
        tool = YoutubeChannelSearchTool()
        tool._run(search_query="test query", youtube_channel_handle="@test_channel")
        mock_run.assert_called_once_with(query="test query")