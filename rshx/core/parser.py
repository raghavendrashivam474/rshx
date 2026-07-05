"""
parser.py
---------
Transforms raw input strings into structured ParsedCommand objects.
"""

import shlex
import os
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
        The original unmodified input string.
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

    Uses posix=False on Windows so that backslashes in paths are
    treated as literal characters rather than escape sequences.

    Parameters
    ----------
    raw_input : str
        The string entered by the user at the prompt.

    Returns
    -------
    ParsedCommand
        A structured command object.

    Raises
    ------
    ValueError
        When the input contains tokenisation errors.
    """
    stripped: str = raw_input.strip()

    if not stripped:
        return ParsedCommand(name="", raw=raw_input)

    # Use posix=False on Windows to preserve backslashes in paths
    posix_mode: bool = os.name != "nt"

    try:
        tokens: list[str] = shlex.split(stripped, posix=posix_mode)
    except ValueError as exc:
        raise ValueError(f"Parse error - {exc}") from exc

    # shlex with posix=False may keep quotes around tokens - strip them
    tokens = [_strip_quotes(t) for t in tokens]

    name: str = tokens[0].lower()
    args: list[str] = tokens[1:]

    return ParsedCommand(name=name, args=args, raw=raw_input)


def _strip_quotes(token: str) -> str:
    """
    Remove surrounding quotes from a token produced by shlex
    when running in non-POSIX mode.

    Parameters
    ----------
    token : str
        A raw token from shlex.split with posix=False.

    Returns
    -------
    str
        The token with surrounding single or double quotes removed.
    """
    if len(token) >= 2:
        if (token[0] == '"' and token[-1] == '"') or \
           (token[0] == "'" and token[-1] == "'"):
            return token[1:-1]
    return token
