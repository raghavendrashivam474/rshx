"""
pipeline.py
-----------
Pipeline validation, construction, and execution coordination.

This module is the orchestration layer between the AST produced
by the parser and the process lifecycle managed by process.py.

Responsibilities
----------------
- Validate a PipelineNode before execution.
- Build the stream connections between stages.
- Coordinate process creation via process.py.
- Manage file handles via redirect.py.
- Collect and report exit codes.

The executor delegates to this module for any pipeline that
contains more than one stage or uses redirection.
"""

from __future__ import annotations
import subprocess
from pathlib import Path

from rshx.core.ast import PipelineNode, RedirectNode
from rshx.core.process import start_process, wait_for_processes, report_exit_codes
from rshx.core.redirect import open_stdin, open_stdout, close_handles
from rshx.utils.display import print_error


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_pipeline(pipeline: PipelineNode) -> list[str]:
    """
    Validate a PipelineNode and return a list of error messages.

    An empty list means the pipeline is valid and safe to execute.

    Validation rules
    ----------------
    - Pipeline must contain at least one stage.
    - No stage may have an empty command name.
    - Only the last stage may redirect stdout to a file.
    - Only the first stage may redirect stdin from a file.

    Parameters
    ----------
    pipeline : PipelineNode
        The pipeline to validate.

    Returns
    -------
    list[str]
        A list of human-readable error messages. Empty if valid.
    """
    errors: list[str] = []

    if not pipeline.stages:
        errors.append("Empty pipeline - no commands to execute.")
        return errors

    for i, stage in enumerate(pipeline.stages):
        if stage.command.is_empty():
            errors.append(f"Stage {i + 1} has an empty command.")

        # Only last stage can redirect stdout to file
        if stage.has_stdout_redirect() and i < len(pipeline.stages) - 1:
            errors.append(
                f"Stage {i + 1}: stdout redirection is only allowed "
                "on the last stage of a pipeline."
            )

        # Only first stage can redirect stdin from file
        if stage.has_stdin_redirect() and i > 0:
            errors.append(
                f"Stage {i + 1}: stdin redirection is only allowed "
                "on the first stage of a pipeline."
            )

    return errors


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def execute_pipeline(pipeline: PipelineNode, cwd: Path) -> None:
    """
    Execute a validated PipelineNode.

    Connects stdout of each stage to stdin of the next using
    subprocess.PIPE. Opens file handles for any stdin or stdout
    redirections. Waits for all processes to complete and reports
    non-zero exit codes.

    Parameters
    ----------
    pipeline : PipelineNode
        The pipeline to execute. Must be validated before calling.
    cwd : Path
        Working directory passed to each child process.
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

        # Resolve stdin
        if i == 0:
            stdin_handle = open_stdin(stage)
            if stdin_handle is not None:
                opened_handles.append(stdin_handle)
        else:
            # Receive stdout pipe from previous stage
            stdin_handle = previous_stdout

        # Resolve stdout
        if is_last:
            stdout_handle = open_stdout(stage)
            if stdout_handle is not None:
                opened_handles.append(stdout_handle)
            else:
                stdout_handle = None
        else:
            # Pipe stdout to next stage
            stdout_handle = subprocess.PIPE

        proc = start_process(
            command=stage.command,
            cwd=cwd,
            stdin=stdin_handle,
            stdout=stdout_handle,
        )

        procs.append(proc)

        # Pass this process's stdout pipe to the next stage's stdin
        if proc is not None and stdout_handle == subprocess.PIPE:
            previous_stdout = proc.stdout
        else:
            previous_stdout = None

    # Wait for all processes
    valid_procs = [p for p in procs if p is not None]
    names = [
        stages[i].command.name
        for i, p in enumerate(procs)
        if p is not None
    ]

    codes = wait_for_processes(valid_procs)
    report_exit_codes(codes, names)

    # Close all opened file handles
    close_handles(*opened_handles)
