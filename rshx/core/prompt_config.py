"""
prompt_config.py
----------------
Builds the shell prompt from configuration and theme values.

Uses prompt_toolkit named colour tags (ansigreen, ansicyan etc.)
rather than raw ANSI escape codes so the HTML remains well-formed.
"""

from __future__ import annotations
from pathlib import Path
from prompt_toolkit.formatted_text import HTML

from rshx.core.theme import Theme


# Mapping from colorama Fore codes to prompt_toolkit named colour tags
_ANSI_TO_TAG: dict[str, str] = {
    "\x1b[30m": "ansiblack",
    "\x1b[31m": "ansired",
    "\x1b[32m": "ansigreen",
    "\x1b[33m": "ansiyellow",
    "\x1b[34m": "ansiblue",
    "\x1b[35m": "ansimagenta",
    "\x1b[36m": "ansicyan",
    "\x1b[37m": "ansiwhite",
    "\x1b[90m": "ansibrightblack",
    "\x1b[91m": "ansibrightred",
    "\x1b[92m": "ansibrightgreen",
    "\x1b[93m": "ansibrightyellow",
    "\x1b[94m": "ansibrightblue",
    "\x1b[95m": "ansibrightmagenta",
    "\x1b[96m": "ansibrightcyan",
    "\x1b[97m": "ansibrightwhite",
}


def _colour_tag(ansi_code: str) -> str:
    """Convert a colorama ANSI code to a prompt_toolkit colour tag name."""
    return _ANSI_TO_TAG.get(ansi_code, "ansiwhite")


def build_prompt(
    cwd: Path,
    theme: Theme,
    show_cwd: bool = True,
    show_git_branch: bool = False,
    shell_name: str = "RSHX",
) -> HTML:
    """
    Build the shell prompt as a prompt_toolkit HTML object.

    Parameters
    ----------
    cwd : Path
        Current working directory.
    theme : Theme
        Active theme providing colour codes.
    show_cwd : bool
        Whether to show the current directory in the prompt.
    show_git_branch : bool
        Whether to append the current git branch to the shell name.
    shell_name : str
        The shell label shown in the prompt.

    Returns
    -------
    HTML
        Formatted prompt for prompt_toolkit.
    """
    shell_colour = _colour_tag(theme.prompt_shell)
    cwd_colour = _colour_tag(theme.prompt_cwd)
    arrow_colour = _colour_tag(theme.prompt_arrow)

    branch_suffix = ""
    if show_git_branch:
        branch = _get_git_branch(cwd)
        if branch:
            branch_suffix = f" [{branch}]"

    cwd_line = ""
    if show_cwd:
        cwd_str = str(cwd)
        cwd_line = (
            f"<{cwd_colour}>{cwd_str}</{cwd_colour}>"
            f"<{arrow_colour}> &gt; </{arrow_colour}>"
        )

    prompt_html = (
        f"<{shell_colour}><b>{shell_name}</b>"
        f"{branch_suffix}</{shell_colour}>\n"
        f"{cwd_line}"
    )

    return HTML(prompt_html)


def _get_git_branch(cwd: Path) -> str | None:
    """
    Return the current git branch name or None.

    Reads from .git/HEAD directly to avoid spawning a subprocess.
    Returns None if not inside a git repository.
    """
    try:
        path = cwd
        for _ in range(10):
            git_head = path / ".git" / "HEAD"
            if git_head.exists():
                content = git_head.read_text(encoding="utf-8").strip()
                if content.startswith("ref: refs/heads/"):
                    return content[len("ref: refs/heads/"):]
                return content[:7]
            parent = path.parent
            if parent == path:
                break
            path = parent
    except OSError:
        pass
    return None
