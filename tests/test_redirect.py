"""
test_redirect.py
Unit tests for rshx.core.redirect.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.core.ast import CommandNode, RedirectNode, RedirectType
from rshx.core.redirect import open_stdin, open_stdout, close_handles, _resolve_mode


class TestOpenStdin:
    def test_returns_none_when_no_redirect(self):
        node = RedirectNode(command=CommandNode(name="sort"))
        assert open_stdin(node) is None

    def test_returns_file_handle_for_existing_file(self, tmp_path: Path):
        f = tmp_path / "input.txt"
        f.write_text("hello")
        node = RedirectNode(
            command=CommandNode(name="sort"),
            stdin_file=str(f),
        )
        handle = open_stdin(node)
        assert handle is not None
        handle.close()

    def test_returns_none_for_missing_file(self, capsys):
        node = RedirectNode(
            command=CommandNode(name="sort"),
            stdin_file="nonexistent.txt",
        )
        result = open_stdin(node)
        assert result is None
        assert "Error" in capsys.readouterr().out

    def test_returns_none_on_permission_error(self, tmp_path: Path, capsys):
        f = tmp_path / "locked.txt"
        f.write_text("data")
        node = RedirectNode(
            command=CommandNode(name="sort"),
            stdin_file=str(f),
        )
        with patch("builtins.open", side_effect=PermissionError):
            result = open_stdin(node)
        assert result is None
        assert "Error" in capsys.readouterr().out

    def test_returns_none_on_os_error(self, tmp_path: Path, capsys):
        f = tmp_path / "input.txt"
        f.write_text("data")
        node = RedirectNode(
            command=CommandNode(name="sort"),
            stdin_file=str(f),
        )
        with patch("builtins.open", side_effect=OSError("disk error")):
            result = open_stdin(node)
        assert result is None
        assert "Error" in capsys.readouterr().out


class TestOpenStdout:
    def test_returns_none_when_no_redirect(self):
        node = RedirectNode(command=CommandNode(name="dir"))
        assert open_stdout(node) is None

    def test_creates_file_for_overwrite(self, tmp_path: Path):
        f = tmp_path / "out.txt"
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file=str(f),
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        handle = open_stdout(node)
        assert handle is not None
        handle.close()
        assert f.exists()

    def test_creates_file_for_append(self, tmp_path: Path):
        f = tmp_path / "out.txt"
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file=str(f),
            stdout_mode=RedirectType.OUTPUT_APPEND,
        )
        handle = open_stdout(node)
        assert handle is not None
        handle.close()
        assert f.exists()

    def test_overwrite_truncates_existing_file(self, tmp_path: Path):
        f = tmp_path / "out.txt"
        f.write_text("existing content")
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file=str(f),
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        handle = open_stdout(node)
        handle.write("new")
        handle.close()
        assert f.read_text() == "new"

    def test_append_preserves_existing_content(self, tmp_path: Path):
        f = tmp_path / "out.txt"
        f.write_text("existing\n")
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file=str(f),
            stdout_mode=RedirectType.OUTPUT_APPEND,
        )
        handle = open_stdout(node)
        handle.write("appended")
        handle.close()
        assert "existing" in f.read_text()
        assert "appended" in f.read_text()

    def test_returns_none_on_permission_error(self, tmp_path: Path, capsys):
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file=str(tmp_path / "out.txt"),
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        with patch("builtins.open", side_effect=PermissionError):
            result = open_stdout(node)
        assert result is None
        assert "Error" in capsys.readouterr().out

    def test_returns_none_on_os_error(self, tmp_path: Path, capsys):
        node = RedirectNode(
            command=CommandNode(name="dir"),
            stdout_file=str(tmp_path / "out.txt"),
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        with patch("builtins.open", side_effect=OSError("disk error")):
            result = open_stdout(node)
        assert result is None
        assert "Error" in capsys.readouterr().out


class TestCloseHandles:
    def test_closes_open_file(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("data")
        handle = open(f, "r")
        close_handles(handle)
        assert handle.closed

    def test_ignores_none(self):
        close_handles(None, None)

    def test_ignores_integer_sentinel(self):
        import subprocess
        close_handles(subprocess.PIPE)

    def test_closes_multiple_handles(self, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("a")
        f2.write_text("b")
        h1 = open(f1, "r")
        h2 = open(f2, "r")
        close_handles(h1, h2)
        assert h1.closed
        assert h2.closed

    def test_handles_os_error_on_close_gracefully(self, tmp_path: Path):
        """OSError during close should not propagate."""
        f = tmp_path / "test.txt"
        f.write_text("data")
        handle = open(f, "r")
        with patch.object(handle, "close", side_effect=OSError("close failed")):
            close_handles(handle)


class TestResolveMode:
    def test_append_returns_a(self):
        assert _resolve_mode(RedirectType.OUTPUT_APPEND) == "a"

    def test_overwrite_returns_w(self):
        assert _resolve_mode(RedirectType.OUTPUT_OVERWRITE) == "w"

    def test_none_returns_w(self):
        assert _resolve_mode(None) == "w"
