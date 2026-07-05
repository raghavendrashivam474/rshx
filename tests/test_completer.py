"""
test_completer.py
Unit tests for rshx.core.completer.
"""

from pathlib import Path
import os
from prompt_toolkit.document import Document
from prompt_toolkit.completion import CompleteEvent

from rshx.core.completer import (
    BuiltinCompleter,
    ShellPathCompleter,
    RshxCompleter,
    _get_path_completions,
)
from rshx.commands.builtins import BUILTIN_REGISTRY


def completions(completer, text: str) -> list[str]:
    """Return completion texts for a given input string."""
    document = Document(text, cursor_position=len(text))
    event = CompleteEvent()
    return [c.text for c in completer.get_completions(document, event)]


# ---------------------------------------------------------------------------
# Path completion helper
# ---------------------------------------------------------------------------

class TestGetPathCompletions:
    def test_returns_matching_entries(self, tmp_path: Path):
        (tmp_path / "alpha").mkdir()
        (tmp_path / "beta").mkdir()
        result = _get_path_completions("al", tmp_path)
        assert any("alpha" in r for r in result)

    def test_appends_separator_for_directories(self, tmp_path: Path):
        (tmp_path / "mydir").mkdir()
        result = _get_path_completions("mydir", tmp_path)
        assert any(r.endswith(("\\", "/")) for r in result)

    def test_returns_empty_for_no_match(self, tmp_path: Path):
        result = _get_path_completions("zzz", tmp_path)
        assert result == []

    def test_handles_permission_error_gracefully(self, tmp_path: Path):
        from unittest.mock import patch
        with patch("rshx.core.completer.Path.iterdir", side_effect=PermissionError):
            result = _get_path_completions("any", tmp_path)
        assert result == []

    def test_returns_empty_on_nonexistent_dir(self, tmp_path: Path):
        result = _get_path_completions("nosuchdir/file", tmp_path)
        assert result == []

    def test_prefix_with_separator_searches_subdirectory(self, tmp_path: Path):
        """Cover the branch where prefix contains a path separator."""
        sub = tmp_path / "parent"
        sub.mkdir()
        (sub / "child").mkdir()
        prefix = f"parent{os.path.sep}ch"
        result = _get_path_completions(prefix, tmp_path)
        assert any("child" in r for r in result)

    def test_case_insensitive_matching(self, tmp_path: Path):
        (tmp_path / "Documents").mkdir()
        result = _get_path_completions("doc", tmp_path)
        assert any("Documents" in r for r in result)


# ---------------------------------------------------------------------------
# Built-in completer
# ---------------------------------------------------------------------------

class TestBuiltinCompleter:
    def setup_method(self):
        self.completer = BuiltinCompleter(list(BUILTIN_REGISTRY.keys()))

    def test_completes_full_command_name(self):
        assert "help" in completions(self.completer, "help")

    def test_completes_partial_command(self):
        assert "help" in completions(self.completer, "he")

    def test_no_match_returns_empty(self):
        assert completions(self.completer, "xyz") == []

    def test_empty_input_returns_all_builtins(self):
        result = completions(self.completer, "")
        for name in BUILTIN_REGISTRY:
            assert name in result

    def test_cl_completes_to_clear(self):
        assert "clear" in completions(self.completer, "cl")

    def test_ex_completes_to_exit(self):
        assert "exit" in completions(self.completer, "ex")

    def test_pw_completes_to_pwd(self):
        assert "pwd" in completions(self.completer, "pw")


# ---------------------------------------------------------------------------
# Shell path completer
# ---------------------------------------------------------------------------

class TestShellPathCompleter:
    def test_completes_directory_name(self, tmp_path: Path):
        (tmp_path / "docs").mkdir()
        completer = ShellPathCompleter(cwd_provider=lambda: tmp_path)
        result = completions(completer, "do")
        assert any("docs" in r for r in result)

    def test_completes_file_name(self, tmp_path: Path):
        (tmp_path / "readme.txt").write_text("hi")
        completer = ShellPathCompleter(cwd_provider=lambda: tmp_path)
        result = completions(completer, "read")
        assert any("readme.txt" in r for r in result)

    def test_empty_prefix_returns_all_entries(self, tmp_path: Path):
        (tmp_path / "aaa").mkdir()
        (tmp_path / "bbb").mkdir()
        completer = ShellPathCompleter(cwd_provider=lambda: tmp_path)
        result = completions(completer, "")
        assert any("aaa" in r for r in result)
        assert any("bbb" in r for r in result)


# ---------------------------------------------------------------------------
# RshxCompleter routing
# ---------------------------------------------------------------------------

class TestRshxCompleter:
    def test_first_token_uses_builtin_completer(self):
        completer = RshxCompleter()
        assert "help" in completions(completer, "he")

    def test_second_token_does_not_return_builtins(self):
        completer = RshxCompleter()
        result = completions(completer, "cd ")
        assert "help" not in result
        assert "clear" not in result

    def test_update_cwd_changes_path_resolution(self, tmp_path: Path):
        (tmp_path / "newdir").mkdir()
        completer = RshxCompleter(cwd_provider=lambda: tmp_path)
        completer.update_cwd(tmp_path)
        result = completions(completer, "cd new")
        assert any("newdir" in r for r in result)
