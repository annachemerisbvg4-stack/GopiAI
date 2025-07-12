import os
import pytest
from crewai_tools.tools.files_compressor_tool import FileCompressorTool
from unittest.mock import patch, MagicMock

@pytest.fixture
def tool():
    return FileCompressorTool()

@patch("os.path.exists", return_value=False)
def test_input_path_does_not_exist(mock_exists, tool):
    result = tool._run("nonexistent_path")
    assert "does not exist" in result

@patch("os.path.exists", return_value=True)
@patch("os.getcwd", return_value="/mocked/cwd")
@patch.object(FileCompressorTool, "_compress_zip")
@patch.object(FileCompressorTool, "_prepare_output", return_value=True)
def test_generate_output_path_default(mock_prepare, mock_compress, mock_cwd, mock_exists, tool):
    result = tool._run(input_path="mydir", format="zip")
    assert "Successfully compressed" in result
    mock_compress.assert_called_once()

@patch("os.path.exists", return_value=True)
def test_extension_mismatch(_ , tool):
    result = tool._run(input_path="some/path", output_path="archive.zip", format="tar.gz")
    assert "must have a '.tar.gz' extension" in result

@patch("os.path.exists", return_value=True)
@patch("os.path.isfile", return_value=True)
@patch("os.path.exists", return_value=True)
def test_existing_output_no_overwrite(_, __, ___, tool):
    result = tool._run(input_path="some/path", output_path="archive.zip", format="zip", overwrite=False)
    assert "overwrite is set to False" in result

@patch("os.makedirs")
@patch("os.path.exists", return_value=False)
def test_prepare_output_makes_dir(mock_exists, mock_makedirs):
    tool = FileCompressorTool()
    result = tool._prepare_output("some/missing/path/file.zip", overwrite=True)
    assert result is True
    mock_makedirs.assert_called_once()