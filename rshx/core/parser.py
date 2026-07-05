"""
parser.py
---------
Transforms raw input strings into structured AST nodes.

Sprint 2 evolution
------------------
Sprint 1 parser produced a flat ParsedCommand.
Sprint 2 parser produces a PipelineNode containing one or more
RedirectNode stages, each wrapping a CommandNode.

Parsing pipeline
----------------
raw string
    |
    v
_tokenize       - split on pipe and redirect operators
    |
    v
_parse_stage    - build CommandNode + RedirectNode per stage
    |
    v
PipelineNode    - collect all stages

Operator tokens
---------------
|    pipe
>    stdout overwrite
>>   stdout append
<    stdin redirect
"""

from __future__ import annotations
import os
import shlex

from rshx.core.ast import (
    CommandNode,
    RedirectNode,
    PipelineNode,
    RedirectType,
)


# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------

PIPE            = "|"
REDIRECT_OUT    = ">"
REDIRECT_APPEND = ">>"
REDIRECT_IN     = "<"

OPERATORS = {REDIRECT_APPEND, REDIRECT_OUT, REDIRECT_IN, PIPE}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(raw_input: str) -> PipelineNode:
    """
    Parse a raw input string into a PipelineNode.

    Parameters
    ----------
    raw_input : str
        The string entered by the user at the prompt.

    Returns
    -------
    PipelineNode
        A structured execution plan. Returns an empty PipelineNode
        when the input is blank.

    Raises
    ------
    ValueError
        When the input contains syntax errors such as missing
        filenames after redirect operators, empty pipe stages,
        or tokenisation failures.
    """
    stripped = raw_input.strip()

    if not stripped:
        return PipelineNode(stages=[])

    tokens = _tokenize(stripped)
    stages = _build_stages(tokens)

    return PipelineNode(stages=stages)


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """
    Split input text into a flat list of word and operator tokens.

    Handles >> before > to avoid >> being split into two > tokens.
    Uses shlex for word splitting with posix=False on Windows so
    that backslashes in paths are preserved literally.

    Quote preservation
    ------------------
    Quotes are preserved on argument tokens so that external commands
    such as Windows find receive correctly quoted arguments.
    Quotes are only stripped from the command name token itself.

    Parameters
    ----------
    text : str
        Raw input string.

    Returns
    -------
    list[str]
        Flat list of tokens including operators.

    Raises
    ------
    ValueError
        On shlex tokenisation failure (e.g. unclosed quotes).
    """
    # Insert spaces around operators so shlex sees them as separate tokens
    # Handle >> before > to preserve two-character operator
    text = text.replace(">>", " >> ")
    text = text.replace(">", " > ").replace(" >  > ", " >> ")
    text = text.replace("<", " < ")
    text = text.replace("|", " | ")

    posix_mode = os.name != "nt"

    try:
        raw_tokens = shlex.split(text, posix=posix_mode)
    except ValueError as exc:
        raise ValueError(f"Parse error - {exc}") from exc

    # Return tokens as-is — quote stripping is applied selectively
    # in _parse_stage only where needed
    return raw_tokens


def _strip_quotes(token: str) -> str:
    """
    Remove surrounding quotes from a single token.

    Used only for the command name and filenames — not for
    arguments passed to external commands which may require
    their quotes to be preserved.

    Parameters
    ----------
    token : str
        A raw token from shlex.split.

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


# ---------------------------------------------------------------------------
# Stage builder
# ---------------------------------------------------------------------------

def _build_stages(tokens: list[str]) -> list[RedirectNode]:
    """
    Convert a flat token list into an ordered list of RedirectNodes.

    Splits on PIPE tokens to find stage boundaries, then delegates
    each segment to _parse_stage.

    Parameters
    ----------
    tokens : list[str]
        Flat token list from _tokenize.

    Returns
    -------
    list[RedirectNode]
        One RedirectNode per pipeline stage.

    Raises
    ------
    ValueError
        On empty pipe segments or leading/trailing pipe operators.
    """
    segments: list[list[str]] = []
    current: list[str] = []

    for token in tokens:
        if token == PIPE:
            if not current:
                raise ValueError(
                    "Parse error - unexpected pipe operator '|'."
                )
            segments.append(current)
            current = []
        else:
            current.append(token)

    if not current:
        raise ValueError(
            "Parse error - trailing pipe operator '|' with no command."
        )
    segments.append(current)

    return [_parse_stage(segment) for segment in segments]


def _parse_stage(tokens: list[str]) -> RedirectNode:
    """
    Parse a single pipeline stage token segment into a RedirectNode.

    Scans tokens for redirect operators and extracts:
    - The command name (quotes stripped) and arguments (quotes preserved)
    - stdin filename after <
    - stdout filename after > or >>

    Quote handling
    --------------
    - Command name : quotes stripped so 'git' and git are equivalent
    - Arguments    : quotes preserved so find "feat" passes "feat" to find
    - Filenames    : quotes stripped so > "out.txt" works correctly

    Parameters
    ----------
    tokens : list[str]
        Token segment for a single stage (no pipe operators).

    Returns
    -------
    RedirectNode
        Structured representation of this stage.

    Raises
    ------
    ValueError
        When a redirect operator has no following filename, or
        when the command name is missing.
    """
    cmd_tokens: list[str] = []
    stdin_file: str | None = None
    stdout_file: str | None = None
    stdout_mode: RedirectType | None = None

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == REDIRECT_APPEND:
            i += 1
            if i >= len(tokens):
                raise ValueError(
                    "Parse error - '>>' operator requires a filename."
                )
            stdout_file = _strip_quotes(tokens[i])
            stdout_mode = RedirectType.OUTPUT_APPEND

        elif token == REDIRECT_OUT:
            i += 1
            if i >= len(tokens):
                raise ValueError(
                    "Parse error - '>' operator requires a filename."
                )
            stdout_file = _strip_quotes(tokens[i])
            stdout_mode = RedirectType.OUTPUT_OVERWRITE

        elif token == REDIRECT_IN:
            i += 1
            if i >= len(tokens):
                raise ValueError(
                    "Parse error - '<' operator requires a filename."
                )
            stdin_file = _strip_quotes(tokens[i])

        else:
            cmd_tokens.append(token)

        i += 1

    if not cmd_tokens:
        raise ValueError(
            "Parse error - redirect operator with no command."
        )

    # Strip quotes from command name only
    # Arguments preserve their quotes for external commands
    name = _strip_quotes(cmd_tokens[0]).lower()
    args = cmd_tokens[1:]

    command = CommandNode(name=name, args=args)

    return RedirectNode(
        command=command,
        stdin_file=stdin_file,
        stdout_file=stdout_file,
        stdout_mode=stdout_mode,
    )
