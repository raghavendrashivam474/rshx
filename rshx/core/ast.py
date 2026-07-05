"""
ast.py
------
Abstract Syntax Tree node definitions for RSHX.

These dataclasses represent the structured result of parsing a
command line. They are pure data - no execution logic lives here.

Separation of representation from execution means the parser can
evolve independently from the executor, and future features such
as aliases, variable expansion, and scripting can be implemented
as AST transformations before execution begins.

Node hierarchy
--------------
CommandNode   - a single executable command with arguments
RedirectNode  - a command with stdin/stdout redirection attached
PipelineNode  - an ordered sequence of commands connected by pipes
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto


# ---------------------------------------------------------------------------
# Redirect types
# ---------------------------------------------------------------------------

class RedirectType(Enum):
    """Represents the type of a redirection operator."""
    OUTPUT_OVERWRITE = auto()   # >
    OUTPUT_APPEND    = auto()   # >>
    INPUT            = auto()   # <


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------

@dataclass
class CommandNode:
    """
    Represents a single executable command with its arguments.

    Attributes
    ----------
    name : str
        The command name (executable).
    args : list[str]
        Ordered list of arguments.
    """
    name: str
    args: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True when the command name is empty."""
        return self.name == ""

    def to_argv(self) -> list[str]:
        """Return the full argument vector including the command name."""
        return [self.name, *self.args]


@dataclass
class RedirectNode:
    """
    Wraps a CommandNode with optional stdin and stdout redirections.

    Attributes
    ----------
    command : CommandNode
        The command to execute.
    stdin_file : str | None
        Path to a file to use as stdin. None means inherit.
    stdout_file : str | None
        Path to a file to use as stdout. None means inherit or pipe.
    stdout_mode : RedirectType | None
        OUTPUT_OVERWRITE or OUTPUT_APPEND. None means no redirection.
    """
    command: CommandNode
    stdin_file: str | None = None
    stdout_file: str | None = None
    stdout_mode: RedirectType | None = None

    def has_stdin_redirect(self) -> bool:
        """Return True when stdin is redirected from a file."""
        return self.stdin_file is not None

    def has_stdout_redirect(self) -> bool:
        """Return True when stdout is redirected to a file."""
        return self.stdout_file is not None


@dataclass
class PipelineNode:
    """
    Represents an ordered sequence of commands connected by pipes.

    Attributes
    ----------
    stages : list[RedirectNode]
        Ordered list of command stages. stdout of stage N feeds
        stdin of stage N+1. Only the first stage may have a stdin
        file redirect. Only the last stage may have a stdout file
        redirect.
    """
    stages: list[RedirectNode] = field(default_factory=list)

    def is_single_command(self) -> bool:
        """Return True when the pipeline contains exactly one stage."""
        return len(self.stages) == 1

    def stage_count(self) -> int:
        """Return the number of stages in this pipeline."""
        return len(self.stages)
