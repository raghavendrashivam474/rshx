"""
test_builtins.py
Unit tests for rshx.commands.builtins.
"""

import os
from pathlib import Path

import pytest

from rshx.commands.builtins import (
    cmd_cd,
    cmd_pwd,
    cmd_exit,
    cmd_help,
    BUILTIN_REGISTRY,
)
from rshx.core.repl import ShellState


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
    """Return a fresh ShellState rooted at a temporary directory."""
    os.chdir(tmp_path)
    return ShellState(cwd=tmp_path)


class TestBuiltinRegistry:
    def test_all_expected_builtins_are_registered(self):
        expected = {"help", "clear", "pwd", "cd", "exit"}
        assert expected == set(BUILTIN_REGISTRY.keys())


class TestCmdPwd:
    def test_prints_current_directory(self, state: ShellState, capsys):
        cmd_pwd([], state)
        captured = capsys.readouterr()
        assert str(state.cwd) in captured.out


class TestCmdCd:
    def test_cd_to_valid_subdirectory(self, state: ShellState, tmp_path: Path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        cmd_cd(["subdir"], state)
        assert state.cwd == sub

    def test_cd_no_args_goes_to_home(self, state: ShellState):
        cmd_cd([], state)
        assert state.cwd == Path.home().resolve()

    def test_cd_to_nonexistent_directory_prints_error(self, state: ShellState, capsys):
        original_cwd = state.cwd
        cmd_cd(["does_not_exist"], state)
        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert state.cwd == original_cwd

    def test_cd_too_many_args_prints_error(self, state: ShellState, capsys):
        cmd_cd(["a", "b"], state)
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_cd_to_file_prints_error(self, state: ShellState, tmp_path: Path, capsys):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        original_cwd = state.cwd
        cmd_cd(["file.txt"], state)
        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert state.cwd == original_cwd


class TestCmdExit:
    def test_exit_sets_running_false(self, state: ShellState, capsys):
        assert state.running is True
        cmd_exit([], state)
        assert state.running is False


class TestCmdHelp:
    def test_help_output_contains_all_builtins(self, state: ShellState, capsys):
        cmd_help([], state)
        captured = capsys.readouterr()
        for name in BUILTIN_REGISTRY:
            assert name in captured.out
