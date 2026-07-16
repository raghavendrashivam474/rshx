"""
confirmation.py
---------------
Reusable confirmation dialog for destructive operations.

Destructive commands that permanently modify configuration or
state should request confirmation before executing. This module
provides a single consistent confirmation mechanism that all
built-in commands can use.

Default behaviour
-----------------
Pressing Enter without typing anything defaults to No.
The user must explicitly type y or yes to confirm.

Usage
-----
    from rshx.core.confirmation import confirm

    if confirm("Remove all startup commands?"):
        cfg.startup_commands.clear()
    else:
        print_info("  Cancelled.")
"""

from __future__ import annotations


def confirm(
    message: str,
    default: bool = False,
) -> bool:
    """
    Display a yes/no confirmation prompt and return the user's choice.

    Parameters
    ----------
    message : str
        The question to ask the user.
    default : bool
        The default answer when the user presses Enter without input.
        False means the default is No. True means the default is Yes.
        Defaults to False (safe default).

    Returns
    -------
    bool
        True if the user confirmed. False otherwise.
    """
    hint = "[y/N]" if not default else "[Y/n]"
    prompt_text = f"  {message} {hint} "

    try:
        response = input(prompt_text).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    if not response:
        return default

    return response in ("y", "yes")


def confirm_destructive(action: str, target: str = "") -> bool:
    """
    Display a standardised confirmation prompt for destructive actions.

    Parameters
    ----------
    action : str
        Description of the destructive action e.g. "Remove all aliases".
    target : str
        Optional specific target e.g. "startup commands".

    Returns
    -------
    bool
        True if confirmed. False if cancelled.
    """
    from rshx.utils.display import print_warning

    if target:
        print_warning(f"This will {action}: {target}")
    else:
        print_warning(f"This will {action}.")

    return confirm("Are you sure?", default=False)
