"""
main.py
Entry point for RSHX.
"""

import sys

if sys.version_info < (3, 12):
    print(
        f"RSHX requires Python 3.12 or newer. "
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}."
    )
    sys.exit(1)

from rshx.core.repl import run_shell


def main() -> None:
    """Application entry point."""
    run_shell()


if __name__ == "__main__":
    main()
