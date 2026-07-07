"""
theme.py
--------
Defines shell themes and manages colour application.

A theme controls the colours used for all terminal output.
Adding a new theme requires only adding an entry to THEMES.
No other module needs to change.

Available themes
----------------
default   - cyan prompt, standard colours
dark      - bright colours on dark background
light     - subdued colours for light terminals
"""

from __future__ import annotations
from dataclasses import dataclass
from colorama import Fore, Style


# ---------------------------------------------------------------------------
# Theme definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Theme:
    """
    Colour configuration for a single theme.

    All fields are ANSI colour code strings compatible with colorama.
    """
    name: str
    prompt_shell: str
    prompt_cwd: str
    prompt_arrow: str
    success: str
    error: str
    warning: str
    info: str
    output: str
    banner: str


# ---------------------------------------------------------------------------
# Built-in themes
# ---------------------------------------------------------------------------

THEMES: dict[str, Theme] = {
    "default": Theme(
        name="default",
        prompt_shell=Fore.GREEN,
        prompt_cwd=Fore.CYAN,
        prompt_arrow=Fore.WHITE,
        success=Fore.GREEN,
        error=Fore.RED,
        warning=Fore.YELLOW,
        info=Style.DIM,
        output=Fore.WHITE,
        banner=Fore.CYAN,
    ),
    "dark": Theme(
        name="dark",
        prompt_shell=Fore.LIGHTGREEN_EX,
        prompt_cwd=Fore.LIGHTCYAN_EX,
        prompt_arrow=Fore.LIGHTWHITE_EX,
        success=Fore.LIGHTGREEN_EX,
        error=Fore.LIGHTRED_EX,
        warning=Fore.LIGHTYELLOW_EX,
        info=Fore.LIGHTBLACK_EX,
        output=Fore.LIGHTWHITE_EX,
        banner=Fore.LIGHTCYAN_EX,
    ),
    "light": Theme(
        name="light",
        prompt_shell=Fore.BLUE,
        prompt_cwd=Fore.MAGENTA,
        prompt_arrow=Fore.BLACK,
        success=Fore.GREEN,
        error=Fore.RED,
        warning=Fore.YELLOW,
        info=Style.DIM,
        output=Fore.BLACK,
        banner=Fore.BLUE,
    ),
}

DEFAULT_THEME_NAME: str = "default"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_theme(name: str) -> Theme:
    """
    Return a Theme by name, falling back to default if not found.

    Parameters
    ----------
    name : str
        Theme name to look up.

    Returns
    -------
    Theme
        The requested theme or the default theme.
    """
    return THEMES.get(name, THEMES[DEFAULT_THEME_NAME])


def list_themes() -> list[str]:
    """Return sorted list of available theme names."""
    return sorted(THEMES.keys())


def is_valid_theme(name: str) -> bool:
    """Return True when the theme name is recognised."""
    return name in THEMES
