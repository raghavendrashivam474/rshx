"""
test_builtins.py
Unit tests for rshx.commands.builtins - Sprint 3.
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
    cmd_alias,
    cmd_unalias,
    cmd_set,
    cmd_unset,
    cmd_env,
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
        expected = {
            "help", "clear", "pwd", "cd", "exit",
            "alias", "unalias", "set", "unset", "env",
        }
        assert expected == set(BUILTIN_REGISTRY.keys())


class TestHelpData:
    def test_all_builtins_have_help_entries(self):
        for name in BUILTIN_REGISTRY:
            assert name in HELP_DATA

    def test_each_entry_has_required_keys(self):
        required = {"description", "usage", "examples", "notes"}
        for name, data in HELP_DATA.items():
            assert required == set(data.keys())


class TestCmdHelp:
    def test_help_no_args_shows_all_commands(self, state, capsys):
        cmd_help([], state)
        captured = capsys.readouterr()
        for name in BUILTIN_REGISTRY:
            assert name in captured.out

    def test_help_with_valid_command_shows_detail(self, state, capsys):
        cmd_help(["cd"], state)
        assert "cd" in capsys.readouterr().out

    def test_help_with_invalid_command_shows_error(self, state, capsys):
        cmd_help(["notacommand"], state)
        assert "Error" in capsys.readouterr().out

    def test_help_for_each_builtin(self, state, capsys):
        for name in BUILTIN_REGISTRY:
            cmd_help([name], state)
            assert name in capsys.readouterr().out


class TestCmdPwd:
    def test_prints_current_directory(self, state, capsys):
        cmd_pwd([], state)
        assert str(state.cwd) in capsys.readouterr().out


class TestCmdCd:
    def test_cd_to_valid_subdirectory(self, state, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        cmd_cd(["subdir"], state)
        assert state.cwd == sub

    def test_cd_no_args_goes_to_home(self, state):
        cmd_cd([], state)
        assert state.cwd == Path.home().resolve()

    def test_cd_to_nonexistent_prints_error(self, state, capsys):
        original = state.cwd
        cmd_cd(["does_not_exist"], state)
        assert "Error" in capsys.readouterr().out
        assert state.cwd == original

    def test_cd_too_many_args_prints_error(self, state, capsys):
        cmd_cd(["a", "b"], state)
        assert "Error" in capsys.readouterr().out

    def test_cd_to_file_prints_error(self, state, tmp_path, capsys):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        original = state.cwd
        cmd_cd(["file.txt"], state)
        assert "Error" in capsys.readouterr().out
        assert state.cwd == original


class TestCmdCdPermissionError:
    def test_resolve_permission_error(self, state, tmp_path, capsys):
        (tmp_path / "locked").mkdir()
        original = state.cwd
        with patch("rshx.commands.builtins.Path.resolve", side_effect=PermissionError):
            cmd_cd(["locked"], state)
        assert "Error" in capsys.readouterr().out
        assert state.cwd == original

    def test_chdir_permission_error(self, state, tmp_path, capsys):
        sub = tmp_path / "locked"
        sub.mkdir()
        with patch("rshx.commands.builtins.os.chdir", side_effect=PermissionError):
            cmd_cd([str(sub)], state)
        assert "Error" in capsys.readouterr().out


class TestCmdClear:
    def test_clear_calls_os_system(self, state):
        with patch("rshx.commands.builtins.os.system") as mock_system:
            cmd_clear([], state)
        expected = "cls" if os.name == "nt" else "clear"
        mock_system.assert_called_once_with(expected)


class TestCmdExit:
    def test_exit_sets_running_false(self, state, capsys):
        cmd_exit([], state)
        assert state.running is False


class TestCmdAlias:
    def test_alias_creates_alias(self, state, capsys):
        cmd_alias(["gs=git status"], state)
        assert state.alias_manager.get("gs") == "git status"

    def test_alias_no_args_lists_aliases(self, state, capsys):
        state.alias_manager.set("gs", "git status")
        cmd_alias([], state)
        assert "gs" in capsys.readouterr().out

    def test_alias_no_args_empty_shows_info(self, state, capsys):
        cmd_alias([], state)
        assert "No aliases" in capsys.readouterr().out

    def test_alias_show_single(self, state, capsys):
        state.alias_manager.set("gs", "git status")
        cmd_alias(["gs"], state)
        assert "git status" in capsys.readouterr().out

    def test_alias_show_missing_prints_error(self, state, capsys):
        cmd_alias(["missing"], state)
        assert "Error" in capsys.readouterr().out

    def test_alias_empty_name_prints_error(self, state, capsys):
        cmd_alias(["=git status"], state)
        assert "Error" in capsys.readouterr().out

    def test_alias_empty_value_prints_error(self, state, capsys):
        cmd_alias(["gs="], state)
        assert "Error" in capsys.readouterr().out

    def test_alias_invalid_name_with_space_prints_error(self, state, capsys):
        """
        Covers builtins.py lines 237-238.
        alias_manager.set raises ValueError when the name contains
        whitespace. cmd_alias must catch and display it.
        """
        cmd_alias(["g s=git status"], state)
        assert "Error" in capsys.readouterr().out


class TestCmdUnalias:
    def test_unalias_removes_alias(self, state, capsys):
        state.alias_manager.set("gs", "git status")
        cmd_unalias(["gs"], state)
        assert state.alias_manager.get("gs") is None

    def test_unalias_missing_prints_error(self, state, capsys):
        cmd_unalias(["missing"], state)
        assert "Error" in capsys.readouterr().out

    def test_unalias_no_args_prints_error(self, state, capsys):
        cmd_unalias([], state)
        assert "Error" in capsys.readouterr().out


class TestCmdSet:
    def test_set_creates_variable(self, state, capsys):
        cmd_set(["PROJECTS=C:\\Projects"], state)
        assert state.environment.get("PROJECTS") == "C:\\Projects"

    def test_set_no_args_lists_variables(self, state, capsys):
        state.environment.set("EDITOR", "code")
        cmd_set([], state)
        assert "EDITOR" in capsys.readouterr().out

    def test_set_no_args_empty_shows_info(self, state, capsys):
        cmd_set([], state)
        assert "No variables" in capsys.readouterr().out

    def test_set_invalid_syntax_prints_error(self, state, capsys):
        cmd_set(["NOEQUALS"], state)
        assert "Error" in capsys.readouterr().out

    def test_set_empty_name_prints_error(self, state, capsys):
        cmd_set(["=value"], state)
        assert "Error" in capsys.readouterr().out

    def test_set_invalid_variable_name_prints_error(self, state, capsys):
        cmd_set(["1INVALID=value"], state)
        assert "Error" in capsys.readouterr().out


class TestCmdUnset:
    def test_unset_removes_variable(self, state, capsys):
        state.environment.set("EDITOR", "code")
        cmd_unset(["EDITOR"], state)
        assert state.environment.get("EDITOR") is None

    def test_unset_missing_prints_error(self, state, capsys):
        cmd_unset(["MISSING"], state)
        assert "Error" in capsys.readouterr().out

    def test_unset_no_args_prints_error(self, state, capsys):
        cmd_unset([], state)
        assert "Error" in capsys.readouterr().out


class TestCmdEnv:
    def test_env_no_args_lists_all(self, state, capsys):
        state.environment.set("EDITOR", "code")
        cmd_env([], state)
        assert "EDITOR" in capsys.readouterr().out

    def test_env_no_args_empty_shows_info(self, state, capsys):
        cmd_env([], state)
        assert "No variables" in capsys.readouterr().out

    def test_env_single_variable(self, state, capsys):
        state.environment.set("EDITOR", "code")
        cmd_env(["EDITOR"], state)
        assert "code" in capsys.readouterr().out

    def test_env_undefined_variable_prints_error(self, state, capsys):
        cmd_env(["MISSING"], state)
        assert "Error" in capsys.readouterr().out

    def test_env_no_args_lists_multiple_variables(self, state, capsys):
        state.environment.set("EDITOR", "code")
        state.environment.set("PROJECTS", "C:\\Projects")
        cmd_env([], state)
        captured = capsys.readouterr()
        assert "EDITOR" in captured.out
        assert "PROJECTS" in captured.out
