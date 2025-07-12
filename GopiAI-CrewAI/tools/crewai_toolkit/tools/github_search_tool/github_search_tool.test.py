import unittest
from unittest.mock import patch, MagicMock
from typing import List, Optional, Type

from embedchain.loaders.github import GithubLoader
from pydantic import BaseModel, Field, PrivateAttr

from embedchain.tools.github_search import (
    GithubSearchTool,
    GithubSearchToolSchema,
    FixedGithubSearchToolSchema,
)


class TestGithubSearchTool(unittest.TestCase):
    @patch("embedchain.tools.github_search.GithubLoader")
    def test_init_with_repo_and_content_types(self, MockGithubLoader):
        tool = GithubSearchTool(
            github_repo="test_repo", content_types=["code"], gh_token="test_token"
        )
        self.assertEqual(tool.args_schema, FixedGithubSearchToolSchema)
        self.assertIn("test_repo", tool.description)

    @patch("embedchain.tools.github_search.GithubLoader")
    def test_add(self, MockGithubLoader):
        tool = GithubSearchTool(gh_token="test_token")
        tool.add(repo="test_repo", content_types=["code"])
        tool._loader.load_data.assert_called_with(
            "repo:test_repo type:code", data_type="github"
        )

    @patch("embedchain.tools.github_search.GithubLoader")
    def test_run_with_repo_and_content_types(self, MockGithubLoader):
        tool = GithubSearchTool(gh_token="test_token")
        tool.add = MagicMock()
        tool._run(search_query="test_query", github_repo="test_repo", content_types=["code"])
        tool.add.assert_called_with(repo="test_repo", content_types=["code"])

    @patch("embedchain.tools.github_search.GithubLoader")
    def test_run_without_repo(self, MockGithubLoader):
        tool = GithubSearchTool(gh_token="test_token")
        tool.add = MagicMock()
        tool._run(search_query="test_query")
        tool.add.assert_not_called()

    def test_github_search_tool_schema(self):
        schema = GithubSearchToolSchema(github_repo="test_repo", content_types=["code"], search_query="test_query")
        self.assertEqual(schema.github_repo, "test_repo")
        self.assertEqual(schema.content_types, ["code"])
        self.assertEqual(schema.search_query, "test_query")