"""
parser.py
---------
Responsible for transforming a raw input string into a structured
command representation that the executor and built-in handlers
can consume.

Keeps parsing logic fully decoupled from execution logic so that
future sprints can extend parsing (pipes, redirects, variables)
without touching the executor.
"""

import shlex
from dataclasses import dataclass, field


@dataclass
class ParsedCommand:
    """
    Represents a single parsed command ready for execution.

    Attributes
    ----------
    name : str
        The command name (first token), lowercased.
    args : list[str]
        Ordered list of arguments following the command name.
    raw : str
        The original, unmodified input string for diagnostics.
    """
    name: str
    args: list[str] = field(default_factory=list)
    raw: str = ""

    def is_empty(self) -> bool:
        """Return True when the command name is an empty string."""
        return self.name == ""


def parse(raw_input: str) -> ParsedCommand:
    """
    Parse a raw input string into a ParsedCommand.

    Uses shlex.split for POSIX-style tokenisation so that quoted
    strings are treated as single tokens.

    Parameters
    ----------
    raw_input : str
        The string entered by the user at the prompt.

    Returns
    -------
    ParsedCommand
        A structured command object.  Returns an empty command when
        the input contains only whitespace.

    Raises
    ------
    ValueError
        When the input string contains mismatched quotes or other
        shlex tokenisation errors.
    """
    stripped: str = raw_input.strip()

    if not stripped:
        return ParsedCommand(name="", raw=raw_input)

    try:
        tokens: list[str] = shlex.split(stripped)
    except ValueError as exc:
        raise ValueError(f"Parse error — {exc}") from exc

    name: str = tokens[0].lower()
    args: list[str] = tokens[1:]

    return ParsedCommand(name=name, args=args, raw=raw_input)
