"""
display.py
----------
Centralised output and formatting utilities for RSHX.
"""

import difflib
from colorama import Fore, Style, init as colorama_init
from rshx import __version__, __description__


def initialise_display() -> None:
    colorama_init(autoreset=True)


BANNER: str = r"""
██████╗ ███████╗██╗  ██╗██╗  ██╗
██╔══██╗██╔════╝██║  ██║╚██╗██╔╝
██████╔╝███████╗███████║ ╚███╔╝
██╔══██╗╚════██║██╔══██║ ██╔██╗
██║  ██║███████║██║  ██║██╔╝ ██╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""


def print_banner() -> None:
    print(Fore.CYAN + BANNER)
    print(Fore.CYAN + f"  {__description__}  v{__version__}")
    print(Fore.CYAN + "  Type 'help' to see available commands.\n")
    print(Style.RESET_ALL, end="")


def print_output(message: str) -> None:
    print(Fore.WHITE + message)


def print_success(message: str) -> None:
    print(Fore.GREEN + message)


def print_warning(message: str) -> None:
    print(Fore.YELLOW + f"Warning: {message}")


def print_error(message: str, reason: str = "", suggestion: str = "") -> None:
    """
    Print a formatted actionable error message.

    Always starts with 'Error:' for backward compatibility with tests.
    Optional reason and suggestion provide additional guidance.
    """
    print(Fore.RED + f"Error: {message}")
    if reason:
        print(Fore.WHITE + f"  Reason     : {reason}")
    if suggestion:
        print(Fore.CYAN + f"  Suggestion : {suggestion}")


def print_info(message: str) -> None:
    print(Style.DIM + message)


def suggest_command(unknown: str, candidates: list[str]) -> None:
    matches = difflib.get_close_matches(unknown, candidates, n=3, cutoff=0.6)

    if matches:
        print_error(
            f"Command not found: '{unknown}'",
            suggestion=f"Did you mean: {', '.join(matches)}?"
        )
    else:
        print_error(
            f"Command not found: '{unknown}'",
            reason="Check spelling or ensure the program is on your PATH.",
            suggestion="Use 'help' to see available built-in commands."
        )
