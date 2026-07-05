"""
display.py
----------
Centralised output and formatting utilities for RSHX.
"""

import difflib
from colorama import Fore, Style, init as colorama_init


def initialise_display() -> None:
    """Initialise colorama for cross-platform ANSI colour support."""
    colorama_init(autoreset=True)


BANNER: str = r"""
██████╗ ███████╗██╗  ██╗██╗  ██╗
██╔══██╗██╔════╝██║  ██║╚██╗██╔╝
██████╔╝███████╗███████║ ╚███╔╝
██╔══██╗╚════██║██╔══██║ ██╔██╗
██║  ██║███████║██║  ██║██╔╝ ██╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""

VERSION: str = "0.2.0"
TAGLINE: str = "Raghav Shell eXtended"


def print_banner() -> None:
    """Print the RSHX welcome banner to stdout."""
    print(Fore.CYAN + BANNER)
    print(Fore.CYAN + f"  {TAGLINE}  v{VERSION}")
    print(Fore.CYAN + "  Type 'help' to see available commands.\n")
    print(Style.RESET_ALL, end="")


def print_output(message: str) -> None:
    """Print a standard informational message."""
    print(Fore.WHITE + message)


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(Fore.GREEN + message)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(Fore.YELLOW + f"Warning: {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(Fore.RED + f"Error: {message}")


def print_info(message: str) -> None:
    """Print a subtle informational message."""
    print(Style.DIM + message)


def suggest_command(unknown: str, candidates: list[str]) -> None:
    """
    Print a 'did you mean' suggestion when a command is not found.

    Uses difflib to find close matches from the candidates list.
    Prints nothing if no close match is found.

    Parameters
    ----------
    unknown : str
        The unrecognised command entered by the user.
    candidates : list[str]
        List of valid command names to compare against.
    """
    matches = difflib.get_close_matches(
        unknown,
        candidates,
        n=3,
        cutoff=0.6,
    )

    if matches:
        print_output("")
        print_warning(f"Command not found: '{unknown}'")
        print_output("  Did you mean:")
        for match in matches:
            print_output(f"    {match}")
        print_output("")
    else:
        print_error(
            f"Command not found: '{unknown}'. "
            "Check spelling or ensure the program is on your PATH."
        )
