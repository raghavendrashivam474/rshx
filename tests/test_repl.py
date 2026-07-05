"""
test_repl.py
Unit tests for rshx.core.repl.
"""

from pathlib import Path
from prompt_toolkit.formatted_text import HTML

from rshx.core.repl import ShellState, _build_prompt


class TestShellState:
    def test_default_running_is_true(self):
        state = ShellState()
        assert state.running is True

    def test_default_cwd_is_current_directory(self):
        state = ShellState()
        assert state.cwd == Path.cwd()

    def test_cwd_can_be_overridden(self, tmp_path: Path):
        state = ShellState(cwd=tmp_path)
        assert state.cwd == tmp_path

    def test_running_can_be_set_false(self):
        state = ShellState()
        state.running = False
        assert state.running is False


class TestBuildPrompt:
    def test_returns_html_instance(self, tmp_path: Path):
        state = ShellState(cwd=tmp_path)
        result = _build_prompt(state)
        assert isinstance(result, HTML)

    def test_prompt_contains_cwd(self, tmp_path: Path):
        state = ShellState(cwd=tmp_path)
        result = _build_prompt(state)
        assert str(tmp_path) in result.value

    def test_prompt_contains_rshx_label(self, tmp_path: Path):
        state = ShellState(cwd=tmp_path)
        result = _build_prompt(state)
        assert "RSHX" in result.value
