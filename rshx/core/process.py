"""
process.py
----------
Manages the lifecycle of individual child processes within a pipeline.
"""

from __future__ import annotations
import os
import subprocess
from pathlib import Path

from rshx.core.ast import CommandNode
from rshx.utils.display import print_error, print_info


def start_process(
    command: CommandNode,
    cwd: Path,
    stdin=None,
    stdout=None,
) -> subprocess.Popen | None:
    """
    Start a single child process for a pipeline stage.

    On Windows, shell=True is used so that CMD built-ins such as
    dir, echo, and type are available in pipelines and redirection.
    On Unix, shell=False is used for safety.
    """
    argv = command.to_argv()
    use_shell = os.name == "nt"

    try:
        return subprocess.Popen(
            argv if not use_shell else " ".join(argv),
            cwd=cwd,
            stdin=stdin,
            stdout=stdout,
            shell=use_shell,
        )
    except FileNotFoundError:
        print_error(
            f"Command not found: '{command.name}'. "
            "Check spelling or ensure the program is on your PATH."
        )
        return None
    except PermissionError:
        print_error(f"Permission denied: cannot execute '{command.name}'.")
        return None
    except OSError as exc:
        print_error(f"Cannot start '{command.name}': {exc}")
        return None


def wait_for_process(proc: subprocess.Popen) -> int:
    """Wait for a process to finish and return its exit code."""
    try:
        proc.wait()
        return proc.returncode
    except OSError as exc:
        print_error(f"Error waiting for process: {exc}")
        return -1


def wait_for_processes(procs: list[subprocess.Popen]) -> list[int]:
    """
    Wait for a list of processes in reverse order.

    Waiting in reverse order prevents upstream producers from
    blocking when downstream consumers have already finished.
    """
    codes = [0] * len(procs)
    for i in reversed(range(len(procs))):
        if procs[i] is not None:
            codes[i] = wait_for_process(procs[i])
    return codes


def report_exit_codes(codes: list[int], names: list[str]) -> None:
    """Print informational messages for any non-zero exit codes."""
    for code, name in zip(codes, names):
        if code != 0:
            print_info(f"Process '{name}' exited with code {code}.")
