"""
script_parser.py
----------------
Converts raw .rshx source text into a structured ScriptNode.

Parsing rules
-------------
- Lines beginning with # are comments and are ignored.
- Blank lines are ignored.
- Lines beginning with @ are directives.
- All other lines are commands.
- Line numbers are 1-based and preserved for diagnostics.

Supported directives
--------------------
@name <value>
@description <value>
@continue_on_error true|false

Unknown directives produce a warning message in the errors list.
Malformed directive values produce a structured parse error.

The Script Parser must not execute commands.
"""

from __future__ import annotations
from rshx.core.script_types import (
    ScriptNode,
    ScriptCommand,
    ScriptDirective,
    ScriptError,
)

KNOWN_DIRECTIVES = {"name", "description", "continue_on_error"}
COMMENT_PREFIX = "#"
DIRECTIVE_PREFIX = "@"


def parse_script(
    source: str,
    script_path: str = "",
) -> tuple[ScriptNode, list[ScriptError]]:
    """
    Parse raw .rshx source text into a ScriptNode.

    Parameters
    ----------
    source : str
        Raw UTF-8 source text from a .rshx file.
    script_path : str
        Path to the source file used in error messages.

    Returns
    -------
    tuple[ScriptNode, list[ScriptError]]
        (ScriptNode, errors) where errors is empty on clean parse.
        Always returns a ScriptNode even when errors are present.
    """
    node = ScriptNode(path=script_path)
    errors: list[ScriptError] = []

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith(COMMENT_PREFIX):
            continue

        if line.startswith(DIRECTIVE_PREFIX):
            directive, directive_errors = _parse_directive(
                line, line_number, script_path
            )
            errors.extend(directive_errors)
            if directive is not None:
                node.directives.append(directive)
                _apply_directive(node, directive, errors, script_path)
            continue

        node.commands.append(
            ScriptCommand(source=line, line_number=line_number)
        )

    return node, errors


# ---------------------------------------------------------------------------
# Directive handling
# ---------------------------------------------------------------------------

def _parse_directive(
    line: str,
    line_number: int,
    script_path: str,
) -> tuple[ScriptDirective | None, list[ScriptError]]:
    """
    Parse a single directive line into a ScriptDirective.

    Format: @key value

    Parameters
    ----------
    line : str
        The raw directive line including the @ prefix.
    line_number : int
        Source line number for diagnostics.
    script_path : str
        Script file path for diagnostics.

    Returns
    -------
    tuple[ScriptDirective | None, list[ScriptError]]
    """
    errors: list[ScriptError] = []
    content = line[1:].strip()

    if not content:
        errors.append(ScriptError(
            message="Empty directive — expected '@key value'.",
            script_path=script_path,
            line_number=line_number,
            command=line,
        ))
        return None, errors

    parts = content.split(None, 1)
    key = parts[0].lower()
    value = parts[1].strip() if len(parts) > 1 else ""

    if key not in KNOWN_DIRECTIVES:
        errors.append(ScriptError(
            message=f"Unknown directive '@{key}'.",
            script_path=script_path,
            line_number=line_number,
            command=line,
        ))

    return ScriptDirective(key=key, value=value, line_number=line_number), errors


def _apply_directive(
    node: ScriptNode,
    directive: ScriptDirective,
    errors: list[ScriptError],
    script_path: str,
) -> None:
    """
    Apply a parsed directive to the ScriptNode.

    Parameters
    ----------
    node : ScriptNode
        The script node being built.
    directive : ScriptDirective
        The directive to apply.
    errors : list[ScriptError]
        Error list to append validation failures to.
    script_path : str
        Script path for error messages.
    """
    key = directive.key
    value = directive.value
    line = directive.line_number

    if key == "name":
        node.name = value

    elif key == "description":
        node.description = value

    elif key == "continue_on_error":
        if value.lower() == "true":
            node.continue_on_error = True
        elif value.lower() == "false":
            node.continue_on_error = False
        else:
            errors.append(ScriptError(
                message=(
                    f"Invalid value for @continue_on_error: '{value}'. "
                    "Expected 'true' or 'false'."
                ),
                script_path=script_path,
                line_number=line,
                command=f"@{key} {value}",
            ))
