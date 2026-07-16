"""
input_dispatcher.py
-------------------
The Input Dispatcher is the central entry point for all user input.

Every line typed or pasted into RSHX passes through the dispatcher
before reaching the preprocessor. This decouples the REPL prompt
from command execution and enables future enhancements such as
multi-command paste, macros, and input recording without modifying
the REPL or executor.

Responsibilities
----------------
- Receive raw user input from the prompt.
- Classify the input type.
- Split multi-line pasted input into individual commands.
- Filter empty lines and whitespace-only input.
- Return an ordered list of commands ready for execution.

Input Classification
--------------------
EMPTY       - blank string or whitespace only
SINGLE      - one non-empty command
MULTI       - multiple lines pasted at once

The REPL iterates over the returned command list and processes
each command individually through the existing pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


# ---------------------------------------------------------------------------
# Input classification
# ---------------------------------------------------------------------------

class InputType(Enum):
    """Classification of user input received at the prompt."""
    EMPTY  = auto()   # blank or whitespace only
    SINGLE = auto()   # single command
    MULTI  = auto()   # multiple commands pasted at once


@dataclass
class DispatchResult:
    """
    The result of dispatching a raw input string.

    Attributes
    ----------
    input_type : InputType
        Classification of the raw input.
    commands : list[str]
        Ordered list of individual command strings ready for execution.
        Empty when input_type is EMPTY.
    """
    input_type: InputType
    commands: list[str]

    def is_empty(self) -> bool:
        """Return True when there are no commands to execute."""
        return len(self.commands) == 0

    def command_count(self) -> int:
        """Return the number of commands in this result."""
        return len(self.commands)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

class InputDispatcher:
    """
    Classifies and normalises raw user input.

    The dispatcher is stateless. Each call to dispatch() processes
    one raw input string independently.
    """

    def dispatch(self, raw_input: str) -> DispatchResult:
        """
        Process raw input from the prompt into a DispatchResult.

        Parameters
        ----------
        raw_input : str
            The raw string received from the prompt. May contain
            one or more lines separated by newline characters.

        Returns
        -------
        DispatchResult
            Classified and normalised result ready for execution.
        """
        if not raw_input or not raw_input.strip():
            return DispatchResult(
                input_type=InputType.EMPTY,
                commands=[],
            )

        commands = self._extract_commands(raw_input)

        if not commands:
            return DispatchResult(
                input_type=InputType.EMPTY,
                commands=[],
            )

        if len(commands) == 1:
            return DispatchResult(
                input_type=InputType.SINGLE,
                commands=commands,
            )

        return DispatchResult(
            input_type=InputType.MULTI,
            commands=commands,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_commands(self, raw_input: str) -> list[str]:
        """
        Split raw input into individual command strings.

        Splits on newline characters. Strips whitespace from each
        line. Filters empty lines. Preserves order.

        Parameters
        ----------
        raw_input : str
            Raw input string, possibly containing multiple lines.

        Returns
        -------
        list[str]
            Ordered list of non-empty command strings.
        """
        lines = raw_input.splitlines()
        commands = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                commands.append(stripped)

        return commands
