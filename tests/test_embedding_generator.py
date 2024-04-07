from unittest import mock
import pytest
from beatrica_embedding.embedding_generator import BeatricaCodeChangeProcessor


@pytest.fixture
def processor():
    return BeatricaCodeChangeProcessor(commit_changes=[], language_model=None)

@pytest.fixture
def processor_with_mock():
    processor = BeatricaCodeChangeProcessor(commit_changes=[], language_model=None)
    processor.cache_path = "/fake/path"
    processor.cache_file = "test_cache.txt"
    return processor

def test_process_changes(processor):
    processor.commit_changes = [
        ("hash123", {"changes": [{"commit_message": "Fix bug", "file_path": "/path/to/file.py", "change_type": "Modified", "old_lines": [{"line number": 1, "line content": "old content"}], "new_lines": [{"line number": 1, "line content": "new content"}]}]})
    ]
    expected_update = 'Commit: hash123\nMessage: Fix bug\nFile: /path/to/file.py\nType: Modified\nOld Lines:\n1: old content\nNew Lines:\n1: new content\n'
    assert processor.process_changes() == [expected_update]


@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("os.makedirs")
@mock.patch("os.path.exists", return_value=False)
def test_write_updates_to_file(mock_exists, mock_makedirs, mock_open, processor_with_mock):
    updates = ["Update 1", "Update 2"]
    processor_with_mock.write_updates_to_file(updates)
    mock_open.assert_called_once_with("/fake/path/test_cache.txt", 'w')
    mock_open().write.assert_called()
    mock_makedirs.assert_called_once_with("/fake/path")
