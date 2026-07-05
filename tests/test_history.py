"""
test_history.py
Unit tests for rshx.core.history.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from rshx.core.history import get_history, get_history_file_path, HISTORY_DIR, HISTORY_FILE
from prompt_toolkit.history import FileHistory, InMemoryHistory


class TestGetHistoryFilePath:
    def test_returns_path_instance(self):
        result = get_history_file_path()
        assert isinstance(result, Path)

    def test_history_file_is_inside_rshx_dir(self):
        result = get_history_file_path()
        assert result.parent.name == ".rshx"

    def test_history_filename_is_correct(self):
        result = get_history_file_path()
        assert result.name == "history"


class TestGetHistory:
    def test_returns_file_history_on_success(self, tmp_path: Path):
        """When the directory is writable, FileHistory is returned."""
        history_dir = tmp_path / ".rshx"
        history_file = history_dir / "history"

        with patch("rshx.core.history.HISTORY_DIR", history_dir), \
             patch("rshx.core.history.HISTORY_FILE", history_file):
            result = get_history()

        assert isinstance(result, FileHistory)

    def test_falls_back_to_in_memory_history_on_os_error(self):
        """When directory creation fails, InMemoryHistory is returned."""
        with patch("rshx.core.history.HISTORY_DIR") as mock_dir:
            mock_dir.mkdir.side_effect = OSError("permission denied")
            result = get_history()

        assert isinstance(result, InMemoryHistory)

    def test_creates_history_directory(self, tmp_path: Path):
        """get_history should create the .rshx directory if missing."""
        history_dir = tmp_path / ".rshx"
        history_file = history_dir / "history"

        assert not history_dir.exists()

        with patch("rshx.core.history.HISTORY_DIR", history_dir), \
             patch("rshx.core.history.HISTORY_FILE", history_file):
            get_history()

        assert history_dir.exists()

    def test_creates_history_file(self, tmp_path: Path):
        """get_history should create the history file if missing."""
        history_dir = tmp_path / ".rshx"
        history_file = history_dir / "history"

        with patch("rshx.core.history.HISTORY_DIR", history_dir), \
             patch("rshx.core.history.HISTORY_FILE", history_file):
            get_history()

        assert history_file.exists()

    def test_existing_history_file_is_not_overwritten(self, tmp_path: Path):
        """An existing history file should not be truncated."""
        history_dir = tmp_path / ".rshx"
        history_dir.mkdir()
        history_file = history_dir / "history"
        history_file.write_text("existing content")

        with patch("rshx.core.history.HISTORY_DIR", history_dir), \
             patch("rshx.core.history.HISTORY_FILE", history_file):
            get_history()

        assert history_file.read_text() == "existing content"
