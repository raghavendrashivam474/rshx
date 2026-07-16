"""
command_queue.py
----------------
Executes an ordered sequence of commands through the RSHX pipeline.

The CommandQueue is responsible for driving multi-command execution.
It receives a list of pre-dispatched command strings and processes
each one sequentially through the preprocessor, parser, and executor.

Responsibilities
----------------
- Execute commands in order.
- Stop on the first parse or execution exception (default behaviour).
- Track execution results for each command.
- Return a structured QueueResult summarising the run.

Stop-on-failure behaviour
-------------------------
By default the queue halts when any command raises an exception.
KeyboardInterrupt is always treated as an immediate halt regardless
of the stop_on_failure setting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from rshx.core.parser import parse
from rshx.core.executor import execute
from rshx.utils.display import print_error, print_warning

if TYPE_CHECKING:
    from rshx.core.repl import ShellState
    from rshx.core.preprocessor import Preprocessor


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class CommandResult:
    """
    The result of executing a single command within the queue.

    Attributes
    ----------
    command : str
        The original command string as received by the queue.
    success : bool
        True if the command completed without raising an exception.
    interrupted : bool
        True if the command was interrupted by KeyboardInterrupt.
    error : str | None
        Error message if the command failed, otherwise None.
    """
    command: str
    success: bool
    interrupted: bool = False
    error: str | None = None


@dataclass
class QueueResult:
    """
    Summary of a completed CommandQueue run.

    Attributes
    ----------
    results : list[CommandResult]
        Ordered results for each command that was attempted.
    stopped_early : bool
        True if execution halted before all commands were processed.
    """
    results: list[CommandResult] = field(default_factory=list)
    stopped_early: bool = False

    def total(self) -> int:
        """Total number of commands attempted."""
        return len(self.results)

    def succeeded(self) -> int:
        """Number of commands that completed without error."""
        return sum(1 for r in self.results if r.success)

    def failed(self) -> int:
        """Number of commands that raised an exception."""
        return sum(1 for r in self.results if not r.success and not r.interrupted)

    def was_interrupted(self) -> bool:
        """True if any command was interrupted by KeyboardInterrupt."""
        return any(r.interrupted for r in self.results)

    def all_succeeded(self) -> bool:
        """True if every attempted command succeeded."""
        return self.succeeded() == self.total() and self.total() > 0


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

class CommandQueue:
    """
    Executes an ordered list of command strings sequentially.

    Parameters
    ----------
    preprocessor : Preprocessor
        The active session preprocessor for alias and variable expansion.
    shell_state : ShellState
        The active shell state passed through to the executor.
    stop_on_failure : bool
        When True (default), halt the queue on the first exception.
        When False, continue executing remaining commands.
    """

    def __init__(
        self,
        preprocessor: "Preprocessor",
        shell_state: "ShellState",
        stop_on_failure: bool = True,
    ) -> None:
        self._preprocessor = preprocessor
        self._shell_state = shell_state
        self._stop_on_failure = stop_on_failure

    def run(self, commands: list[str]) -> QueueResult:
        """
        Execute the given list of commands sequentially.

        Parameters
        ----------
        commands : list[str]
            Ordered list of command strings.

        Returns
        -------
        QueueResult
            Summary of execution including per-command results.
        """
        queue_result = QueueResult()

        for command in commands:
            if not self._shell_state.running:
                queue_result.stopped_early = True
                break

            result = self._run_one(command)
            queue_result.results.append(result)

            if result.interrupted:
                queue_result.stopped_early = True
                break

            if not result.success and self._stop_on_failure:
                queue_result.stopped_early = len(queue_result.results) < len(commands)
                break

        return queue_result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_one(self, command: str) -> CommandResult:
        """
        Execute a single command string.

        Parameters
        ----------
        command : str
            A single command string.

        Returns
        -------
        CommandResult
            Result of this individual command execution.
        """
        try:
            expanded, warnings = self._preprocessor.process(command)
            for warning in warnings:
                print_warning(warning)

            pipeline = parse(expanded)
            execute(pipeline, self._shell_state)

            return CommandResult(command=command, success=True)

        except KeyboardInterrupt:
            print("\nCommand interrupted.")
            return CommandResult(
                command=command,
                success=False,
                interrupted=True,
            )

        except Exception as exc:
            print_error(
                f"Failed to execute: '{command}'.",
                reason=str(exc),
                suggestion="Check the command syntax and try again.",
            )
            return CommandResult(
                command=command,
                success=False,
                error=str(exc),
            )
