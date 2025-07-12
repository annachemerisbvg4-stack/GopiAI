import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from embedchain.tools.youtube_video_search import (
    FixedYoutubeVideoSearchToolSchema,
    YoutubeVideoSearchTool,
    YoutubeVideoSearchToolSchema,
)


class TestYoutubeVideoSearchTool(unittest.TestCase):
    def test_youtube_video_search_tool_schema(self):
        schema = YoutubeVideoSearchToolSchema(
            youtube_video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", search_query="test query"
        )
        self.assertEqual(schema.youtube_video_url, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(schema.search_query, "test query")

    def test_fixed_youtube_video_search_tool_schema(self):
        schema = FixedYoutubeVideoSearchToolSchema(search_query="test query")
        self.assertEqual(schema.search_query, "test query")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_youtube_video_search_tool_init(self, mock_add):
        tool = YoutubeVideoSearchTool(youtube_video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_add.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ", data_type=DataType.YOUTUBE_VIDEO)
        self.assertEqual(tool.args_schema, FixedYoutubeVideoSearchToolSchema)

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_youtube_video_search_tool_add(self, mock_add):
        tool = YoutubeVideoSearchTool()
        tool.add("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_add.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ", data_type=DataType.YOUTUBE_VIDEO)

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_youtube_video_search_tool_run(self, mock_super_run):
        tool = YoutubeVideoSearchTool()
        tool._run(search_query="test query", youtube_video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_super_run.assert_called_once_with(query="test query")