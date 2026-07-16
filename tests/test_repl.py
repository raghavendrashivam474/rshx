"""
test_repl.py
Unit tests for rshx.core.repl and rshx.core.prompt.
"""

from pathlib import Path
from prompt_toolkit.formatted_text import HTML

from rshx.core.repl import ShellState
from rshx.core.prompt import build_prompt
from unittest.mock import patch
from rshx.core.repl import _handle_interrupt, _handle_eof


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
        result = build_prompt(tmp_path)
        assert isinstance(result, HTML)

    def test_prompt_contains_cwd(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert str(tmp_path) in result.value

    def test_prompt_contains_rshx_label(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert "RSHX" in result.value

    def test_prompt_contains_gt_symbol(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert "&gt;" in result.value

    def test_prompt_contains_newline(self, tmp_path: Path):
        result = build_prompt(tmp_path)
        assert "\n" in result.value

    def test_prompt_reflects_different_paths(self):
        path_a = Path("C:/Users/test")
        path_b = Path("C:/Projects/rshx")
        result_a = build_prompt(path_a)
        result_b = build_prompt(path_b)
        assert str(path_a) in result_a.value
        assert str(path_b) in result_b.value
        assert str(path_a) not in result_b.value


class TestHandleInterrupt:
    def test_prints_interrupted_message(self, capsys):
        _handle_interrupt()
        captured = capsys.readouterr()
        assert "interrupted" in captured.out

    def test_prints_ctrl_d_hint(self, capsys):
        _handle_interrupt()
        captured = capsys.readouterr()
        assert "Ctrl+D" in captured.out

    def test_output_starts_with_newline(self, capsys):
        _handle_interrupt()
        captured = capsys.readouterr()
        assert captured.out.startswith("\n")


class TestHandleEof:
    def test_sets_running_false(self):
        state = ShellState()
        assert state.running is True
        _handle_eof(state)
        assert state.running is False

    def test_does_not_raise(self):
        state = ShellState()
        try:
            _handle_eof(state)
        except Exception as exc:
            pytest.fail(f"_handle_eof raised unexpectedly: {exc}")

    def test_running_already_false_stays_false(self):
        state = ShellState()
        state.running = False
        _handle_eof(state)
        assert state.running is False