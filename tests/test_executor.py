"""
test_executor.py
Unit tests for rshx.core.executor - Sprint 3.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.core.executor import execute
from rshx.core.ast import CommandNode, RedirectNode, PipelineNode, RedirectType
from rshx.core.repl import ShellState


@pytest.fixture()
def state(tmp_path: Path) -> ShellState:
    os.chdir(tmp_path)
    return ShellState(cwd=tmp_path)


def single_pipeline(name: str, args=None) -> PipelineNode:
    return PipelineNode(stages=[
        RedirectNode(command=CommandNode(name=name, args=args or []))
    ])


class TestExecuteEmpty:
    def test_empty_pipeline_does_nothing(self, state: ShellState):
        execute(PipelineNode(stages=[]), state)


class TestExecuteBuiltin:
    def test_builtin_is_dispatched(self, state: ShellState):
        mock_handler = MagicMock()
        pipeline = single_pipeline("help")
        with patch("rshx.core.executor.BUILTIN_REGISTRY", {"help": mock_handler}):
            execute(pipeline, state)
        mock_handler.assert_called_once_with([], state)


class TestExecuteExternal:
    def test_external_command_calls_subprocess_run(self, state: ShellState):
        """
        On Windows shell=True is used so argv is joined to a string.
        On Unix shell=False is used so argv is a list.
        """
        pipeline = single_pipeline("whoami")
        mock_result = MagicMock()
        mock_result.returncode = 0

        use_shell = os.name == "nt"
        expected_argv = "whoami" if use_shell else ["whoami"]

        with patch("rshx.core.executor.subprocess.run", return_value=mock_result) as mock_run:
            execute(pipeline, state)

        mock_run.assert_called_once_with(
            expected_argv,
            cwd=state.cwd,
            shell=use_shell,
            check=False,
        )

    def test_shell_false_uses_list_argv(self, state: ShellState):
        """
        Covers executor.py line 89 - the Unix branch where shell=False
        and argv remains a list. Mocked to run regardless of platform.
        """
        pipeline = single_pipeline("whoami")
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("rshx.core.executor.os.name", "posix"), \
             patch("rshx.core.executor.subprocess.run", return_value=mock_result) as mock_run:
            execute(pipeline, state)

        call_args = mock_run.call_args
        argv_arg = call_args[0][0]
        assert isinstance(argv_arg, list)
        assert call_args[1]["shell"] is False

    def test_file_not_found_prints_suggestion(self, state: ShellState, capsys):
        """
        Covers executor.py lines 105-106 - FileNotFoundError handler.
        Mocked to run regardless of platform.
        """
        pipeline = single_pipeline("nonexistentcmd")

        with patch(
            "rshx.core.executor.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            execute(pipeline, state)

        captured = capsys.readouterr()
        assert "Error" in captured.out or "Warning" in captured.out

    def test_unknown_command_prints_error_or_exit_code(self, state: ShellState, capsys):
        pipeline = single_pipeline("nonexistentcmd123")
        execute(pipeline, state)
        captured = capsys.readouterr()
        assert (
            "Error" in captured.out
            or "Warning" in captured.out
            or "exited with code" in captured.out
        )

    def test_nonzero_exit_code_prints_info(self, state: ShellState, capsys):
        pipeline = single_pipeline("somecommand")
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("rshx.core.executor.subprocess.run", return_value=mock_result):
            execute(pipeline, state)
        assert "1" in capsys.readouterr().out


class TestExecuteBuiltinException:
    def test_builtin_exception_prints_error(self, state: ShellState, capsys):
        def broken(args, shell_state):
            raise RuntimeError("oops")
        pipeline = single_pipeline("help")
        with patch("rshx.core.executor.BUILTIN_REGISTRY", {"help": broken}):
            execute(pipeline, state)
        assert "Error" in capsys.readouterr().out


class TestExecuteExternalErrors:
    def test_permission_error_prints_error(self, state: ShellState, capsys):
        pipeline = single_pipeline("somebin")
        with patch("rshx.core.executor.subprocess.run", side_effect=PermissionError):
            execute(pipeline, state)
        assert "Permission denied" in capsys.readouterr().out

    def test_unexpected_exception_prints_error(self, state: ShellState, capsys):
        pipeline = single_pipeline("somebin")
        with patch("rshx.core.executor.subprocess.run", side_effect=OSError("disk")):
            execute(pipeline, state)
        assert "Error" in capsys.readouterr().out


class TestExecutePipelineRouting:
    def test_multi_stage_delegates_to_pipeline_executor(self, state: ShellState):
        pipeline = PipelineNode(stages=[
            RedirectNode(command=CommandNode(name="git", args=["status"])),
            RedirectNode(command=CommandNode(name="find", args=["modified"])),
        ])
        with patch("rshx.core.executor.execute_pipeline") as mock_exec:
            execute(pipeline, state)
        mock_exec.assert_called_once_with(pipeline, state.cwd)

    def test_single_stage_with_redirect_delegates_to_pipeline(self, state: ShellState):
        pipeline = PipelineNode(stages=[
            RedirectNode(
                command=CommandNode(name="dir"),
                stdout_file="out.txt",
                stdout_mode=RedirectType.OUTPUT_OVERWRITE,
            )
        ])
        with patch("rshx.core.executor.execute_pipeline") as mock_exec:
            execute(pipeline, state)
        mock_exec.assert_called_once_with(pipeline, state.cwd)

class TestExecutorErrorMessages:
    def test_builtin_exception_includes_suggestion(self, state: ShellState, capsys):
        def broken(args, shell_state):
            raise RuntimeError("something went wrong")
        pipeline = single_pipeline("help")
        with patch("rshx.core.executor.BUILTIN_REGISTRY", {"help": broken}):
            execute(pipeline, state)
        captured = capsys.readouterr().out
        assert "Suggestion" in captured

    def test_builtin_exception_includes_reason(self, state: ShellState, capsys):
        def broken(args, shell_state):
            raise RuntimeError("something went wrong")
        pipeline = single_pipeline("help")
        with patch("rshx.core.executor.BUILTIN_REGISTRY", {"help": broken}):
            execute(pipeline, state)
        captured = capsys.readouterr().out
        assert "Reason" in captured

    def test_permission_error_includes_suggestion(self, state: ShellState, capsys):
        pipeline = single_pipeline("somebin")
        with patch("rshx.core.executor.subprocess.run", side_effect=PermissionError):
            execute(pipeline, state)
        captured = capsys.readouterr().out
        assert "Suggestion" in captured

    def test_permission_error_includes_reason(self, state: ShellState, capsys):
        pipeline = single_pipeline("somebin")
        with patch("rshx.core.executor.subprocess.run", side_effect=PermissionError):
            execute(pipeline, state)
        captured = capsys.readouterr().out
        assert "Reason" in captured

    def test_unexpected_exception_includes_suggestion(self, state: ShellState, capsys):
        pipeline = single_pipeline("somebin")
        with patch("rshx.core.executor.subprocess.run", side_effect=OSError("disk error")):
            execute(pipeline, state)
        captured = capsys.readouterr().out
        assert "Suggestion" in captured

    def test_nonzero_exit_prints_warning_not_error(self, state: ShellState, capsys):
        pipeline = single_pipeline("somecommand")
        mock_result = MagicMock()
        mock_result.returncode = 2
        with patch("rshx.core.executor.subprocess.run", return_value=mock_result):
            execute(pipeline, state)
        captured = capsys.readouterr().out
        assert "Warning" in captured