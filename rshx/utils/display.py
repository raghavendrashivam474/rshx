"""
display.py
Centralised output and formatting utilities for RSHX.
"""

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

VERSION: str = "0.1.0"
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
