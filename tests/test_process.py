"""
test_process.py
Unit tests for rshx.core.process.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.core.ast import CommandNode
from rshx.core.process import (
    start_process,
    wait_for_process,
    wait_for_processes,
    report_exit_codes,
)


class TestStartProcess:
    def test_returns_popen_for_valid_command(self, tmp_path: Path):
        cmd = CommandNode(name="whoami")
        proc = start_process(cmd, tmp_path)
        if proc:
            proc.wait()
            assert isinstance(proc, subprocess.Popen)

    def test_returns_none_for_unknown_command(self, tmp_path: Path, capsys):
        cmd = CommandNode(name="nonexistentcmd999")
        result = start_process(cmd, tmp_path)
        assert result is None
        assert "Error" in capsys.readouterr().out

    def test_returns_none_on_permission_error(self, tmp_path: Path, capsys):
        cmd = CommandNode(name="whoami")
        with patch("subprocess.Popen", side_effect=PermissionError):
            result = start_process(cmd, tmp_path)
        assert result is None
        assert "Error" in capsys.readouterr().out

    def test_returns_none_on_os_error(self, tmp_path: Path, capsys):
        cmd = CommandNode(name="whoami")
        with patch("subprocess.Popen", side_effect=OSError("fail")):
            result = start_process(cmd, tmp_path)
        assert result is None
        assert "Error" in capsys.readouterr().out


class TestWaitForProcess:
    def test_returns_exit_code_zero(self, tmp_path: Path):
        cmd = CommandNode(name="whoami")
        proc = start_process(cmd, tmp_path)
        if proc:
            code = wait_for_process(proc)
            assert code == 0

    def test_returns_minus_one_on_os_error(self, capsys):
        mock_proc = MagicMock()
        mock_proc.wait.side_effect = OSError("fail")
        result = wait_for_process(mock_proc)
        assert result == -1
        assert "Error" in capsys.readouterr().out


class TestWaitForProcesses:
    def test_returns_list_of_exit_codes(self):
        mock_a = MagicMock()
        mock_a.wait.return_value = None
        mock_a.returncode = 0
        mock_b = MagicMock()
        mock_b.wait.return_value = None
        mock_b.returncode = 1
        codes = wait_for_processes([mock_a, mock_b])
        assert codes == [0, 1]

    def test_empty_list_returns_empty(self):
        assert wait_for_processes([]) == []


class TestReportExitCodes:
    def test_prints_nonzero_exit_code(self, capsys):
        report_exit_codes([1], ["mycommand"])
        captured = capsys.readouterr()
        assert "mycommand" in captured.out
        assert "1" in captured.out

    def test_no_output_for_zero_exit_code(self, capsys):
        report_exit_codes([0], ["mycommand"])
        assert capsys.readouterr().out == ""

    def test_multiple_codes_reported(self, capsys):
        report_exit_codes([0, 1, 2], ["a", "b", "c"])
        captured = capsys.readouterr()
        assert "b" in captured.out
        assert "c" in captured.out
