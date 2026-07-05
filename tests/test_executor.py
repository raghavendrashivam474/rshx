"""
test_executor.py
Unit tests for rshx.core.executor.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.core.executor import execute
from rshx.core.parser import ParsedCommand
from rshx.core.repl import ShellState


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
    os.chdir(tmp_path)
    return ShellState(cwd=tmp_path)


class TestExecuteEmpty:
    def test_empty_command_does_nothing(self, state: ShellState):
        cmd = ParsedCommand(name="", args=[], raw="")
        execute(cmd, state)


class TestExecuteBuiltin:
    def test_builtin_is_dispatched(self, state: ShellState):
        mock_handler = MagicMock()
        cmd = ParsedCommand(name="help", args=[], raw="help")

        with patch("rshx.core.executor.BUILTIN_REGISTRY", {"help": mock_handler}):
            execute(cmd, state)

        mock_handler.assert_called_once_with([], state)


class TestExecuteExternal:
    def test_external_command_calls_subprocess_run(self, state: ShellState):
        cmd = ParsedCommand(name="whoami", args=[], raw="whoami")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("rshx.core.executor.subprocess.run", return_value=mock_result) as mock_run:
            execute(cmd, state)

        mock_run.assert_called_once_with(
            ["whoami"],
            cwd=state.cwd,
            shell=False,
            check=False,
        )

    def test_unknown_command_prints_error(self, state: ShellState, capsys):
        cmd = ParsedCommand(name="nonexistentcmd123", args=[], raw="nonexistentcmd123")
        execute(cmd, state)
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_nonzero_exit_code_prints_info(self, state: ShellState, capsys):
        cmd = ParsedCommand(name="somecommand", args=[], raw="somecommand")

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("rshx.core.executor.subprocess.run", return_value=mock_result):
            execute(cmd, state)

        captured = capsys.readouterr()
        assert "1" in captured.out
