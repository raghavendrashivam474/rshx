"""
script_types.py
---------------
Data models for the RSHX scripting runtime.

All models are pure data - no execution logic.

Hierarchy
---------
ScriptCommand   - a single command line with source and line number
ScriptDirective - a parsed @directive with key and value
ScriptNode      - the complete parsed script
ScriptError     - a structured error from loader, parser, or runtime
ScriptResult    - the outcome of a complete script execution
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Script components
# ---------------------------------------------------------------------------

@dataclass
class ScriptCommand:
    """
    A single executable command line from a script.

    Attributes
    ----------
    source : str
        The raw command string as it appeared in the script file.
    line_number : int
        The 1-based line number in the source file.
    """
    source: str
    line_number: int


@dataclass
class ScriptDirective:
    """
    A parsed script directive beginning with @.

    Attributes
    ----------
    key : str
        The directive name without the @ prefix.
    value : str
        The directive value as a string.
    line_number : int
        The 1-based line number in the source file.
    """
    key: str
    value: str
    line_number: int


@dataclass
class ScriptNode:
    """
    A fully parsed .rshx script file.

    Attributes
    ----------
    path : str
        Absolute path to the source file.
    name : str
        Human-readable script name from @name directive.
    description : str
        Human-readable description from @description directive.
    continue_on_error : bool
        Whether to continue after a command failure.
    commands : list[ScriptCommand]
        Ordered list of commands to execute.
    directives : list[ScriptDirective]
        All directives parsed from the script.
    """
    path: str
    name: str = ""
    description: str = ""
    continue_on_error: bool = False
    commands: list[ScriptCommand] = field(default_factory=list)
    directives: list[ScriptDirective] = field(default_factory=list)

    def command_count(self) -> int:
        """Return the number of commands in the script."""
        return len(self.commands)

    def is_empty(self) -> bool:
        """Return True when the script contains no commands."""
        return len(self.commands) == 0


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

@dataclass
class ScriptError:
    """
    A structured error from the scripting subsystem.

    Attributes
    ----------
    message : str
        Human-readable error description.
    script_path : str
        Path to the script file. Empty if not yet loaded.
    line_number : int
        Line number where the error occurred. 0 if not applicable.
    command : str
        The command that caused the error. Empty if not applicable.
    exit_code : int
        Process exit code if the error was a command failure.
    """
    message: str
    script_path: str = ""
    line_number: int = 0
    command: str = ""
    exit_code: int = 0

    def format(self) -> str:
        """Return a formatted multi-line error string."""
        lines = [f"Error: {self.message}"]
        if self.script_path:
            lines.append(f"  File   : {self.script_path}")
        if self.line_number:
            lines.append(f"  Line   : {self.line_number}")
        if self.command:
            lines.append(f"  Command: {self.command}")
        if self.exit_code:
            lines.append(f"  Exit   : {self.exit_code}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Execution result
# ---------------------------------------------------------------------------

@dataclass
class ScriptResult:
    """
    The complete outcome of a script execution.

    Attributes
    ----------
    script_name : str
        Script name from @name or derived from filename.
    script_path : str
        Absolute path to the executed script.
    commands_total : int
        Total number of commands in the script.
    commands_executed : int
        Number of commands that were attempted.
    commands_succeeded : int
        Number of commands that completed with exit code 0.
    commands_failed : int
        Number of commands that failed.
    duration : float
        Total execution time in seconds.
    success : bool
        True when no commands failed.
    errors : list[ScriptError]
        All errors encountered during execution.
    """
    script_name: str
    script_path: str
    commands_total: int = 0
    commands_executed: int = 0
    commands_succeeded: int = 0
    commands_failed: int = 0
    duration: float = 0.0
    success: bool = True
    errors: list[ScriptError] = field(default_factory=list)

    def add_error(self, error: ScriptError) -> None:
        """Record a script error and mark the result as failed."""
        self.errors.append(error)
        self.success = False
        self.commands_failed += 1
