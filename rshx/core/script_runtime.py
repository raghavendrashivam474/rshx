"""
script_runtime.py
-----------------
Executes a parsed ScriptNode using the existing RSHX pipeline.

The runtime delegates all command processing to the existing
Preprocessor, Parser, and Executor. It does not duplicate
any command execution logic.

Exit code tracking
------------------
The executor does not return exit codes directly. The runtime
tracks failures by monitoring whether the last executed command
produced a non-zero exit message via a lightweight stdout capture
approach. For built-in commands success is assumed unless an
exception is raised. For external commands on Windows with
shell=True, a non-zero exit code prints an info message but does
not raise. The runtime treats any command that results in an
exception as failed. Future sprints can add explicit exit code
propagation from the executor.
"""

from __future__ import annotations
import time
import io
import sys
from typing import TYPE_CHECKING

from rshx.core.script_types import ScriptNode, ScriptResult, ScriptError
from rshx.core.parser import parse
from rshx.core.executor import execute

if TYPE_CHECKING:
    from rshx.core.repl import ShellState
    from rshx.core.preprocessor import Preprocessor


def run_script(
    node: ScriptNode,
    shell_state: "ShellState",
    preprocessor: "Preprocessor",
    script_args: list[str] | None = None,
) -> ScriptResult:
    """
    Execute a parsed ScriptNode using the existing RSHX pipeline.

    Parameters
    ----------
    node : ScriptNode
        The parsed script to execute.
    shell_state : ShellState
        The active shell state shared with the interactive session.
    preprocessor : Preprocessor
        The active Preprocessor with alias and variable access.
    script_args : list[str] | None
        Positional arguments (%1, %2, ...) passed to the script.

    Returns
    -------
    ScriptResult
        Structured execution result with statistics and errors.
    """
    script_name = node.name or _derive_name(node.path)

    result = ScriptResult(
        script_name=script_name,
        script_path=node.path,
        commands_total=node.command_count(),
    )

    if node.is_empty():
        return result

    args = script_args or []
    _inject_args(shell_state, args)

    start_time = time.monotonic()

    try:
        for cmd in node.commands:
            if not shell_state.running:
                break

            result.commands_executed += 1
            success = _execute_command(
                cmd.source, cmd.line_number, node,
                shell_state, preprocessor, result
            )

            if success:
                result.commands_succeeded += 1
            else:
                if not node.continue_on_error:
                    break

    finally:
        result.duration = time.monotonic() - start_time
        _remove_args(shell_state, args)

    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _execute_command(
    source: str,
    line_number: int,
    node: ScriptNode,
    shell_state: "ShellState",
    preprocessor: "Preprocessor",
    result: ScriptResult,
) -> bool:
    """
    Execute a single script command through the full RSHX pipeline.

    Captures stdout to detect non-zero exit code messages printed
    by the executor. Returns True on success, False on failure.
    """
    try:
        expanded, warnings = preprocessor.process(source)
    except Exception as exc:
        result.add_error(ScriptError(
            message=f"Preprocessor error: {exc}",
            script_path=node.path,
            line_number=line_number,
            command=source,
        ))
        return False

    try:
        pipeline = parse(expanded)
    except ValueError as exc:
        result.add_error(ScriptError(
            message=f"Parse error: {exc}",
            script_path=node.path,
            line_number=line_number,
            command=source,
        ))
        return False

    if not pipeline.stages:
        return True

    # Capture stdout to detect "exited with code N" messages
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured

    try:
        execute(pipeline, shell_state)
    except Exception as exc:
        sys.stdout = old_stdout
        result.add_error(ScriptError(
            message=f"Execution error: {exc}",
            script_path=node.path,
            line_number=line_number,
            command=source,
        ))
        return False
    finally:
        sys.stdout = old_stdout

    output = captured.getvalue()

    # Print captured output to real stdout so user sees it
    if output:
        sys.stdout.write(output)

    # Check for non-zero exit code indicator in captured output
    if "exited with code" in output:
        result.add_error(ScriptError(
            message="Command exited with non-zero exit code.",
            script_path=node.path,
            line_number=line_number,
            command=source,
            exit_code=1,
        ))
        return False

    return True


def _inject_args(shell_state: "ShellState", args: list[str]) -> None:
    """Set positional arguments as %1, %2, ... in the environment."""
    for i, arg in enumerate(args, start=1):
        try:
            shell_state.environment._variables[str(i)] = arg
        except Exception:
            pass


def _remove_args(shell_state: "ShellState", args: list[str]) -> None:
    """Remove positional argument variables from the environment."""
    for i in range(1, len(args) + 1):
        shell_state.environment._variables.pop(str(i), None)


def _derive_name(path: str) -> str:
    """Derive a display name from the script file path."""
    from pathlib import Path
    return Path(path).stem if path else "script"
