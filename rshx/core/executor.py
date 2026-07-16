"""
executor.py
-----------
Routes parsed pipelines to the correct execution strategy.

Sprint 5 change
---------------
After checking built-ins, the executor now checks the plugin
registry before falling back to external system commands.

Routing order
-------------
1. Empty pipeline   -> do nothing
2. Single stage, no redirection, built-in -> built-in handler
3. Single stage, no redirection, plugin   -> plugin registry
4. Single stage, no redirection, external -> subprocess.run
5. Multi-stage or redirection             -> pipeline executor
"""

from __future__ import annotations
import os
import subprocess
from typing import TYPE_CHECKING

from rshx.commands.builtins import BUILTIN_REGISTRY
from rshx.core.ast import PipelineNode, RedirectNode
from rshx.core.pipeline import execute_pipeline
from rshx.utils.display import print_error, print_warning, suggest_command

if TYPE_CHECKING:
    from rshx.core.repl import ShellState


def execute(pipeline: PipelineNode, shell_state: "ShellState") -> None:
    """
    Execute a PipelineNode against the current shell state.
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

    # 1. Built-in commands
    if command.name in BUILTIN_REGISTRY:
        _execute_builtin(stage, shell_state)
        return

    # 2. Plugin commands
    plugin_manager = getattr(shell_state, "plugin_manager", None)
    if plugin_manager is not None:
        registry = plugin_manager._registry
        if registry.has(command.name):
            registry.dispatch(command.name, command.args, shell_state)
            return

    # 3. External commands
    _execute_external(stage, shell_state)


def _execute_builtin(
    stage: RedirectNode,
    shell_state: "ShellState",
) -> None:
    command = stage.command
    handler = BUILTIN_REGISTRY[command.name]
    try:
        handler(command.args, shell_state)
    except Exception as exc:
        print_error(
            f"Built-in '{command.name}' failed unexpectedly.",
            reason=str(exc),
            suggestion=f"Run 'help {command.name}' for correct usage.",
        )


def _execute_external(
    stage: RedirectNode,
    shell_state: "ShellState",
) -> None:
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
            print_warning(
                f"'{command.name}' exited with code {result.returncode}."
            )

    except FileNotFoundError:
        candidates = list(BUILTIN_REGISTRY.keys())
        suggest_command(command.name, candidates)

    except PermissionError:
        print_error(
            f"Permission denied: '{command.name}'.",
            reason="The file exists but cannot be executed.",
            suggestion="Check file permissions or run with elevated privileges.",
        )

    except Exception as exc:
        print_error(
            f"Failed to run '{command.name}'.",
            reason=str(exc),
            suggestion="Check the command name and arguments are correct.",
        )