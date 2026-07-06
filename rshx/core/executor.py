"""
executor.py
-----------
Routes parsed pipelines to the correct execution strategy.
"""

from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from rshx.commands.builtins import BUILTIN_REGISTRY
from rshx.core.ast import PipelineNode, RedirectNode
from rshx.core.pipeline import execute_pipeline
from rshx.utils.display import print_error, print_info, suggest_command

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


def execute(pipeline: PipelineNode, shell_state: "ShellState") -> None:
    """
    Execute a PipelineNode against the current shell state.

    Routing logic
    -------------
    - Empty pipeline                              -> do nothing
    - Single stage, no redirection, built-in      -> built-in handler
    - Single stage, no redirection, external      -> subprocess.run
    - Multi-stage or any redirection              -> pipeline executor
    """
    if not pipeline.stages:
        return

    if pipeline.is_single_command():
        stage = pipeline.stages[0]
        if not stage.has_stdin_redirect() and not stage.has_stdout_redirect():
            _execute_single(stage, shell_state)
            return

    execute_pipeline(pipeline, shell_state.cwd)


def _execute_single(
    stage: RedirectNode,
    shell_state: "ShellState",
) -> None:
    """Execute a single command with no redirection."""
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
    """
    Run a single external command via subprocess.run.

    Uses shell=True on Windows so that CMD built-ins such as
    dir, echo, and type are available alongside PATH executables.
    """
    command = stage.command
    use_shell = os.name == "nt"

    if use_shell:
        argv = " ".join(command.to_argv())
    else:
        argv = command.to_argv()

    try:
        result = subprocess.run(
            argv,
            cwd=shell_state.cwd,
            shell=use_shell,
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
