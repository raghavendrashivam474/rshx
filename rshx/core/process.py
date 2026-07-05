"""
process.py
----------
Manages the lifecycle of individual child processes within a pipeline.

Responsibilities
----------------
- Create a subprocess.Popen instance for a single pipeline stage.
- Connect stdin and stdout streams as directed by the pipeline.
- Wait for processes to complete.
- Collect and return exit codes.

Future capabilities such as background jobs, process groups, and
signal handling should be implemented here without touching
pipeline.py or executor.py.
"""

from __future__ import annotations
import subprocess
from pathlib import Path
from typing import IO

from rshx.core.ast import CommandNode
from rshx.utils.display import print_error, print_info


# ---------------------------------------------------------------------------
# Process creation
# ---------------------------------------------------------------------------

def start_process(
    command: CommandNode,
    cwd: Path,
    stdin=None,
    stdout=None,
) -> subprocess.Popen | None:
    """
    Start a single child process for a pipeline stage.

    Parameters
    ----------
    command : CommandNode
        The command and arguments to execute.
    cwd : Path
        Working directory for the process.
    stdin : file | int | None
        stdin stream. subprocess.PIPE, a file handle, or None.
    stdout : file | int | None
        stdout stream. subprocess.PIPE, a file handle, or None.

    Returns
    -------
    subprocess.Popen | None
        The started process, or None if the process could not start.
    """
    argv = command.to_argv()

    try:
        return subprocess.Popen(
            argv,
            cwd=cwd,
            stdin=stdin,
            stdout=stdout,
            shell=False,
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


# ---------------------------------------------------------------------------
# Process completion
# ---------------------------------------------------------------------------

def wait_for_process(proc: subprocess.Popen) -> int:
    """
    Wait for a process to finish and return its exit code.

    Parameters
    ----------
    proc : subprocess.Popen
        The process to wait for.

    Returns
    -------
    int
        The process exit code. Returns -1 if waiting fails.
    """
    try:
        proc.wait()
        return proc.returncode
    except OSError as exc:
        print_error(f"Error waiting for process: {exc}")
        return -1


def wait_for_processes(procs: list[subprocess.Popen]) -> list[int]:
    """
    Wait for a list of processes to finish.

    Waits in reverse order so that upstream processes finish after
    downstream consumers have read all available output.

    Parameters
    ----------
    procs : list[subprocess.Popen]
        List of running processes in pipeline order.

    Returns
    -------
    list[int]
        Exit codes in pipeline order.
    """
    codes = [0] * len(procs)
    for i in reversed(range(len(procs))):
        if procs[i] is not None:
            codes[i] = wait_for_process(procs[i])
    return codes


def report_exit_codes(codes: list[int], names: list[str]) -> None:
    """
    Print informational messages for any non-zero exit codes.

    Parameters
    ----------
    codes : list[int]
        Exit codes in pipeline order.
    names : list[str]
        Command names in pipeline order, for display purposes.
    """
    for code, name in zip(codes, names):
        if code != 0:
            print_info(f"Process '{name}' exited with code {code}.")
