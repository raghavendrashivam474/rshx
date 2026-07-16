"""
rshx/__main__.py
Allows running RSHX as a module: python -m rshx
"""

from rshx.core.repl import run_shell


def main() -> None:
    """Application entry point."""
    import sys
    if sys.version_info < (3, 12):
        print(
            f"RSHX requires Python 3.12 or newer. "
            f"You are running Python {sys.version_info.major}.{sys.version_info.minor}."
        )
        sys.exit(1)
    run_shell()


if __name__ == "__main__":
    main()
