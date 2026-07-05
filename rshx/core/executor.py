"""
executor.py
-----------
Routes parsed pipelines to the correct execution strategy.

Sprint 2 changes
----------------
- Accepts PipelineNode instead of ParsedCommand.
- Single-command pipelines without redirection execute via the
  original built-in or subprocess path.
- Multi-stage pipelines or any pipeline with redirection are
  delegated to pipeline.execute_pipeline.

The executor remains a thin routing layer. All orchestration
logic lives in pipeline.py.
"""

from __future__ import annotations
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.commands.builtins import BUILTIN_REGISTRY
from rshx.core.ast import PipelineNode, RedirectNode
from rshx.core.pipeline import execute_pipeline
from rshx.utils.display import print_error, print_info, suggest_command

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute(pipeline: PipelineNode, shell_state: "ShellState") -> None:
    """
    Execute a PipelineNode against the current shell state.

    Routing logic
    -------------
    - Empty pipeline  -> do nothing.
    - Single stage, no redirection, built-in command -> built-in handler.
    - Single stage, no redirection, external command -> subprocess.run.
    - Everything else -> pipeline executor.

    Parameters
    ----------
    pipeline : PipelineNode
        The structured execution plan from the parser.
    shell_state : ShellState
        Mutable shell state providing cwd and running flag.
    """
    if not pipeline.stages:
        return

    # Single command with no redirection - use fast path
    if pipeline.is_single_command():
        stage = pipeline.stages[0]
        if not stage.has_stdin_redirect() and not stage.has_stdout_redirect():
            _execute_single(stage, shell_state)
            return

    # Multi-stage pipeline or redirection - delegate to pipeline executor
    execute_pipeline(pipeline, shell_state.cwd)


# ---------------------------------------------------------------------------
# Single command fast path
# ---------------------------------------------------------------------------

def _execute_single(
    stage: RedirectNode,
    shell_state: "ShellState",
) -> None:
    """
    Execute a single command with no redirection.

    Checks built-in registry first, falls back to subprocess.
    """
    command = stage.command

    if command.name in BUILTIN_REGISTRY:
        _execute_builtin(stage, shell_state)
    else:
        _execute_external(stage, shell_state)


def _execute_builtin(
    stage: RedirectNode,
    shell_state: "ShellState",
) -> None:
    """Dispatch to the appropriate built-in command handler."""
    command = stage.command
    handler = BUILTIN_REGISTRY[command.name]
    try:
        handler(command.args, shell_state)
    except Exception as exc:
        print_error(
            f"Built-in '{command.name}' raised an unexpected error: {exc}"
        )


def _execute_external(
    stage: RedirectNode,
    shell_state: "ShellState",
) -> None:
    """Run a single external command via subprocess.run."""
    command = stage.command
    argv = command.to_argv()

    try:
        result = subprocess.run(
            argv,
            cwd=shell_state.cwd,
            shell=False,
            check=False,
        )

        if result.returncode != 0:
            print_info(
                f"Process '{command.name}' exited with code {result.returncode}."
            )

    except FileNotFoundError:
        candidates = list(BUILTIN_REGISTRY.keys())
        suggest_command(command.name, candidates)

    except PermissionError:
        print_error(
            f"Permission denied: cannot execute '{command.name}'."
        )

    except Exception as exc:
        print_error(
            f"Unexpected error while running '{command.name}': {exc}"
        )
