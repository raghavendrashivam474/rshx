"""
pipeline.py
-----------
Pipeline validation, construction, and execution coordination.
"""

from __future__ import annotations
import subprocess
from pathlib import Path

from rshx.core.ast import PipelineNode, RedirectNode
from rshx.core.process import start_process, wait_for_processes, report_exit_codes
from rshx.core.redirect import open_stdin, open_stdout, close_handles
from rshx.utils.display import print_error


def validate_pipeline(pipeline: PipelineNode) -> list[str]:
    """
    Validate a PipelineNode and return a list of error messages.

    An empty list means the pipeline is valid and safe to execute.
    """
    errors: list[str] = []

    if not pipeline.stages:
        errors.append("Empty pipeline - no commands to execute.")
        return errors

    for i, stage in enumerate(pipeline.stages):
        if stage.command.is_empty():
            errors.append(f"Stage {i + 1} has an empty command.")

        if stage.has_stdout_redirect() and i < len(pipeline.stages) - 1:
            errors.append(
                f"Stage {i + 1}: '>' or '>>' can only appear on the last "
                "command in a pipeline. Move the redirect to the end."
            )

        if stage.has_stdin_redirect() and i > 0:
            errors.append(
                f"Stage {i + 1}: '<' can only appear on the first "
                "command in a pipeline. Move the redirect to the start."
            )

    return errors


def execute_pipeline(pipeline: PipelineNode, cwd: Path) -> None:
    """
    Execute a validated PipelineNode.
    """
    errors = validate_pipeline(pipeline)
    if errors:
        for error in errors:
            print_error(error)
        return

    stages = pipeline.stages
    procs: list[subprocess.Popen | None] = []
    opened_handles = []

    previous_stdout = None

    for i, stage in enumerate(stages):
        is_last = (i == len(stages) - 1)

        if i == 0:
            stdin_handle = open_stdin(stage)
            if stdin_handle is not None:
                opened_handles.append(stdin_handle)
        else:
            stdin_handle = previous_stdout

        if is_last:
            stdout_handle = open_stdout(stage)
            if stdout_handle is not None:
                opened_handles.append(stdout_handle)
            else:
                stdout_handle = None
        else:
            stdout_handle = subprocess.PIPE

        proc = start_process(
            command=stage.command,
            cwd=cwd,
            stdin=stdin_handle,
            stdout=stdout_handle,
        )

        procs.append(proc)

        if proc is not None and stdout_handle == subprocess.PIPE:
            previous_stdout = proc.stdout
        else:
            previous_stdout = None

    valid_procs = [p for p in procs if p is not None]
    names = [
        stages[i].command.name
        for i, p in enumerate(procs)
        if p is not None
    ]

    codes = wait_for_processes(valid_procs)
    report_exit_codes(codes, names)

    close_handles(*opened_handles)
