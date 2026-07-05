"""
test_builtins.py
Unit tests for rshx.commands.builtins.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from rshx.commands.builtins import (
    cmd_cd,
    cmd_clear,
    cmd_pwd,
    cmd_exit,
    cmd_help,
    BUILTIN_REGISTRY,
    HELP_DATA,
)
from rshx.core.repl import ShellState


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
    os.chdir(tmp_path)
    return ShellState(cwd=tmp_path)


class TestBuiltinRegistry:
    def test_all_expected_builtins_are_registered(self):
        expected = {"help", "clear", "pwd", "cd", "exit"}
        assert expected == set(BUILTIN_REGISTRY.keys())


class TestHelpData:
    def test_all_builtins_have_help_entries(self):
        for name in BUILTIN_REGISTRY:
            assert name in HELP_DATA

    def test_each_entry_has_required_keys(self):
        required = {"description", "usage", "examples", "notes"}
        for name, data in HELP_DATA.items():
            assert required == set(data.keys()), f"Missing keys in help for '{name}'"


class TestCmdHelp:
    def test_help_no_args_shows_all_commands(self, state: ShellState, capsys):
        cmd_help([], state)
        captured = capsys.readouterr()
        for name in BUILTIN_REGISTRY:
            assert name in captured.out

    def test_help_with_valid_command_shows_detail(self, state: ShellState, capsys):
        cmd_help(["cd"], state)
        captured = capsys.readouterr()
        assert "cd" in captured.out
        assert "Usage" in captured.out or "usage" in captured.out.lower()
        assert "Examples" in captured.out or "examples" in captured.out.lower()

    def test_help_with_invalid_command_shows_error(self, state: ShellState, capsys):
        cmd_help(["notacommand"], state)
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_help_for_each_builtin(self, state: ShellState, capsys):
        for name in BUILTIN_REGISTRY:
            cmd_help([name], state)
            captured = capsys.readouterr()
            assert name in captured.out


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


class TestCmdCdPermissionError:
    def test_cd_resolve_permission_error_prints_error(
        self, state: ShellState, tmp_path: Path, capsys
    ):
        sub = tmp_path / "locked"
        sub.mkdir()
        original_cwd = state.cwd

        with patch("rshx.commands.builtins.Path.resolve", side_effect=PermissionError):
            cmd_cd(["locked"], state)

        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert state.cwd == original_cwd

    def test_cd_chdir_permission_error_prints_error(
        self, state: ShellState, tmp_path: Path, capsys
    ):
        sub = tmp_path / "locked"
        sub.mkdir()

        with patch("rshx.commands.builtins.os.chdir", side_effect=PermissionError):
            cmd_cd([str(sub)], state)

        captured = capsys.readouterr()
        assert "Error" in captured.out


class TestCmdClear:
    def test_clear_calls_os_system(self, state: ShellState):
        with patch("rshx.commands.builtins.os.system") as mock_system:
            cmd_clear([], state)
        expected = "cls" if os.name == "nt" else "clear"
        mock_system.assert_called_once_with(expected)


class TestCmdExit:
    def test_exit_sets_running_false(self, state: ShellState, capsys):
        assert state.running is True
        cmd_exit([], state)
        assert state.running is False
