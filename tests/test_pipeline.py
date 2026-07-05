"""
test_pipeline.py
Unit tests for rshx.core.pipeline.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rshx.core.ast import CommandNode, RedirectNode, PipelineNode, RedirectType
from rshx.core.pipeline import validate_pipeline, execute_pipeline


def make_stage(name, args=None, stdin_file=None, stdout_file=None, stdout_mode=None):
    return RedirectNode(
        command=CommandNode(name=name, args=args or []),
        stdin_file=stdin_file,
        stdout_file=stdout_file,
        stdout_mode=stdout_mode,
    )


class TestValidatePipeline:
    def test_valid_single_stage(self):
        p = PipelineNode(stages=[make_stage("git")])
        assert validate_pipeline(p) == []

    def test_valid_two_stage_pipeline(self):
        p = PipelineNode(stages=[make_stage("git"), make_stage("find")])
        assert validate_pipeline(p) == []

    def test_empty_pipeline_returns_error(self):
        p = PipelineNode(stages=[])
        assert len(validate_pipeline(p)) > 0

    def test_empty_command_name_returns_error(self):
        p = PipelineNode(stages=[make_stage("")])
        assert len(validate_pipeline(p)) > 0

    def test_stdout_redirect_on_non_last_stage_returns_error(self):
        stages = [
            make_stage("git", stdout_file="out.txt", stdout_mode=RedirectType.OUTPUT_OVERWRITE),
            make_stage("find"),
        ]
        p = PipelineNode(stages=stages)
        assert len(validate_pipeline(p)) > 0

    def test_stdin_redirect_on_non_first_stage_returns_error(self):
        stages = [
            make_stage("git"),
            make_stage("find", stdin_file="input.txt"),
        ]
        p = PipelineNode(stages=stages)
        assert len(validate_pipeline(p)) > 0

    def test_stdout_redirect_on_last_stage_is_valid(self):
        stages = [
            make_stage("git"),
            make_stage("find", stdout_file="out.txt", stdout_mode=RedirectType.OUTPUT_OVERWRITE),
        ]
        p = PipelineNode(stages=stages)
        assert validate_pipeline(p) == []

    def test_stdin_redirect_on_first_stage_is_valid(self):
        p = PipelineNode(stages=[make_stage("sort", stdin_file="input.txt")])
        assert validate_pipeline(p) == []


class TestExecutePipeline:
    def test_single_stage_executes(self, tmp_path: Path):
        p = PipelineNode(stages=[make_stage("whoami")])
        with patch("rshx.core.pipeline.start_process") as mock_start:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = None
            mock_start.return_value = mock_proc
            execute_pipeline(p, tmp_path)
        mock_start.assert_called_once()

    def test_invalid_pipeline_prints_error(self, tmp_path: Path, capsys):
        p = PipelineNode(stages=[])
        execute_pipeline(p, tmp_path)
        assert "Error" in capsys.readouterr().out

    def test_output_redirect_to_file(self, tmp_path: Path):
        out_file = tmp_path / "out.txt"
        stage = make_stage(
            "whoami",
            stdout_file=str(out_file),
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        p = PipelineNode(stages=[stage])
        with patch("rshx.core.pipeline.start_process") as mock_start:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = None
            mock_start.return_value = mock_proc
            execute_pipeline(p, tmp_path)
        mock_start.assert_called_once()

    def test_failed_process_start_handled(self, tmp_path: Path):
        p = PipelineNode(stages=[make_stage("nonexistentcmd")])
        with patch("rshx.core.pipeline.start_process", return_value=None):
            execute_pipeline(p, tmp_path)

    def test_two_stage_pipe_connects_stdout_to_stdin(self, tmp_path: Path):
        """Second stage receives stdout pipe from first stage."""
        stages = [make_stage("git"), make_stage("find")]
        p = PipelineNode(stages=stages)

        mock_proc_a = MagicMock()
        mock_proc_a.returncode = 0
        mock_proc_a.stdout = MagicMock()

        mock_proc_b = MagicMock()
        mock_proc_b.returncode = 0
        mock_proc_b.stdout = None

        with patch(
            "rshx.core.pipeline.start_process",
            side_effect=[mock_proc_a, mock_proc_b],
        ) as mock_start:
            execute_pipeline(p, tmp_path)

        assert mock_start.call_count == 2
        second_call_kwargs = mock_start.call_args_list[1][1]
        assert second_call_kwargs["stdin"] == mock_proc_a.stdout

    def test_close_handles_called_after_execution(self, tmp_path: Path):
        """File handles opened for redirection should be closed."""
        out_file = tmp_path / "out.txt"
        stage = make_stage(
            "whoami",
            stdout_file=str(out_file),
            stdout_mode=RedirectType.OUTPUT_OVERWRITE,
        )
        p = PipelineNode(stages=[stage])

        with patch("rshx.core.pipeline.start_process") as mock_start, \
             patch("rshx.core.pipeline.close_handles") as mock_close:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = None
            mock_start.return_value = mock_proc
            execute_pipeline(p, tmp_path)

        mock_close.assert_called_once()

    def test_none_proc_excluded_from_wait(self, tmp_path: Path):
        """Stages that fail to start are excluded from wait."""
        stages = [make_stage("bad_cmd"), make_stage("find")]
        p = PipelineNode(stages=stages)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = None

        with patch(
            "rshx.core.pipeline.start_process",
            side_effect=[None, mock_proc],
        ), patch("rshx.core.pipeline.wait_for_processes") as mock_wait:
            mock_wait.return_value = [0]
            execute_pipeline(p, tmp_path)

        waited = mock_wait.call_args[0][0]
        assert mock_proc in waited

    def test_last_stage_with_no_stdout_redirect_inherits_terminal(self, tmp_path: Path):
        """
        Last stage with no stdout redirect passes None as stdout
        so the process inherits the terminal. previous_stdout is
        then set to None (line 124) since stdout_handle is not PIPE.
        """
        stages = [make_stage("git"), make_stage("find")]
        p = PipelineNode(stages=stages)

        mock_proc_a = MagicMock()
        mock_proc_a.returncode = 0
        mock_proc_a.stdout = MagicMock()

        mock_proc_b = MagicMock()
        mock_proc_b.returncode = 0
        mock_proc_b.stdout = None

        with patch(
            "rshx.core.pipeline.start_process",
            side_effect=[mock_proc_a, mock_proc_b],
        ) as mock_start:
            execute_pipeline(p, tmp_path)

        # Last stage stdout_handle is None so previous_stdout set to None
        last_call_kwargs = mock_start.call_args_list[1][1]
        assert last_call_kwargs["stdout"] is None
