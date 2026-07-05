# RSHX — Raghav Shell eXtended

A lightweight, extensible command-line shell written in Python.

---

## Vision

RSHX is a custom interactive shell designed to be simple to understand,
easy to extend, and pleasant to use.  Sprint 0 establishes the foundation.
Future sprints will add command history, autocomplete, scripting, plugins,
and more.

---

## Quick Start

### Prerequisites
- Python 3.12 or newer
- Git

### Installation

\\\powershell
# Clone the repository
git clone https://github.com/your-username/rshx.git
Set-Location rshx

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements-dev.txt

# Run RSHX
python main.py
\\\

---

## Built-in Commands

| Command | Description                        |
|---------|------------------------------------|
| help    | Show available commands            |
| clear   | Clear the terminal screen          |
| pwd     | Print current working directory    |
| cd      | Change working directory           |
| exit    | Exit RSHX                          |

Any other input is passed to the system as an external command.

---

## Project Structure

\\\
rshx/
+-- rshx/
¦   +-- commands/
¦   ¦   +-- builtins.py     # Built-in command implementations
¦   +-- core/
¦   ¦   +-- repl.py         # REPL loop and shell state
¦   ¦   +-- executor.py     # Command execution logic
¦   ¦   +-- parser.py       # Input parsing
¦   +-- utils/
¦       +-- display.py      # Output and formatting utilities
+-- tests/                  # Pytest test suite
+-- main.py                 # Entry point
+-- requirements.txt
+-- README.md
\\\

---

## Running Tests

\\\powershell
pytest --cov=rshx --cov-report=term-missing
\\\

---

## Roadmap

| Sprint | Focus                                      |
|--------|--------------------------------------------|
| 0      | Foundation, REPL, built-ins (current)     |
| 1      | Command history, autocomplete              |
| 2      | Pipes, redirection                         |
| 3      | Environment variables, aliases             |
| 4      | Plugin system                              |
| 5      | Custom scripting language                  |

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Write tests for your changes.
4. Submit a pull request.
