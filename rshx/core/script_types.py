"""
script_types.py
---------------
Data models for the RSHX scripting runtime.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ScriptCommand:
    """A single executable command line from a script."""
    source: str
    line_number: int


@dataclass
class ScriptDirective:
    """A parsed script directive beginning with @."""
    key: str
    value: str
    line_number: int


@dataclass
class ScriptNode:
    """A fully parsed .rshx script file."""
    path: str
    name: str = ""
    description: str = ""
    continue_on_error: bool = False
    commands: list[ScriptCommand] = field(default_factory=list)
    directives: list[ScriptDirective] = field(default_factory=list)

    def command_count(self) -> int:
        return len(self.commands)

    def is_empty(self) -> bool:
        return len(self.commands) == 0


@dataclass
class ScriptError:
    """A structured error from the scripting subsystem."""
    message: str
    script_path: str = ""
    line_number: int = 0
    command: str = ""
    exit_code: int = 0

    def format(self) -> str:
        """Return a formatted multi-line diagnostic string."""
        lines = [f"  {self.message}"]
        if self.script_path:
            import pathlib
            lines.append(f"  File    : {pathlib.Path(self.script_path).name}")
        if self.line_number:
            lines.append(f"  Line    : {self.line_number}")
        if self.command:
            lines.append(f"  Command : {self.command}")
        if self.exit_code:
            lines.append(f"  Exit    : {self.exit_code}")
        if self.script_path or self.line_number or self.command:
            lines.append(f"  Tip     : Check the command and try again.")
        return "\n".join(lines)


@dataclass
class ScriptResult:
    """The complete outcome of a script execution."""
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
