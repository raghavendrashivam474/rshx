"""
script_runtime.py
-----------------
Executes a parsed ScriptNode using the existing RSHX pipeline.

Positional arguments
--------------------
Script arguments are available as both:
- %1 %2 %3  (no closing percent - simple replacement)
- %1% %2% %3% (standard variable syntax)

The runtime injects positional args into the environment as
variables named '1', '2', '3' etc so that %1% works via the
existing variable expander. For bare %N references without a
closing %, the runtime performs a simple string substitution
before passing the command to the preprocessor.
"""

from __future__ import annotations
import time
import io
import sys
import re
from typing import TYPE_CHECKING

from rshx.core.script_types import ScriptNode, ScriptResult, ScriptError
from rshx.core.parser import parse
from rshx.core.executor import execute

if TYPE_CHECKING:
    from rshx.core.repl import ShellState
    from rshx.core.preprocessor import Preprocessor

# Pattern for bare positional args: %1 %2 %3 (no closing %)
_POSITIONAL_PATTERN = re.compile(r"%([0-9]+)(?!%)")


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

            # Expand bare %N positional references before preprocessor
            source = _expand_positional_bare(cmd.source, args)

            success = _execute_command(
                source, cmd.line_number, node,
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

def _expand_positional_bare(source: str, args: list[str]) -> str:
    """
    Replace bare %N references (without closing %) with arg values.

    Handles %1 %2 %3 style where no closing percent is used.
    Missing args expand to empty string.

    Parameters
    ----------
    source : str
        The command source string.
    args : list[str]
        Positional arguments list (0-indexed internally).

    Returns
    -------
    str
        Command with bare positional references expanded.
    """
    def replace(match: re.Match) -> str:
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(args):
            return args[idx]
        return ""

    return _POSITIONAL_PATTERN.sub(replace, source)


def _execute_command(
    source: str,
    line_number: int,
    node: ScriptNode,
    shell_state: "ShellState",
    preprocessor: "Preprocessor",
    result: ScriptResult,
) -> bool:
    """Execute a single script command through the full RSHX pipeline."""
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

    if output:
        sys.stdout.write(output)

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
    """Set positional arguments as %1%, %2%, ... in the environment."""
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
