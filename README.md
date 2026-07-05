# RSHX - Raghav Shell eXtended

A lightweight, extensible command-line shell written in Python.

---

## Vision

RSHX is a custom interactive shell designed to be simple to understand,
easy to extend, and pleasant to use. Sprint 0 establishes the foundation.
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

| Command | Description                          |
|---------|--------------------------------------|
| help    | Show available commands              |
| clear   | Clear the terminal screen            |
| pwd     | Print current working directory      |
| cd      | Change working directory             |
| exit    | Exit RSHX                            |

Any other input is passed to the system as an external command.

---

## Project Structure

\\\
rshx/
├── rshx/
│   ├── commands/
│   │   └── builtins.py     # Built-in command implementations
│   ├── core/
│   │   ├── repl.py         # REPL loop and shell state
│   │   ├── executor.py     # Command execution routing
│   │   └── parser.py       # Input tokenisation
│   └── utils/
│       └── display.py      # Terminal output helpers
├── tests/
│   ├── test_builtins.py
│   ├── test_display.py
│   ├── test_executor.py
│   ├── test_parser.py
│   └── test_repl.py
├── main.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
\\\

---

## Running Tests

\\\powershell
pytest --cov=rshx --cov-report=term-missing -v
\\\

### Coverage — Sprint 0

| Module                      | Coverage | Notes                              |
|-----------------------------|----------|------------------------------------|
| rshx/__init__.py            | 100%     |                                    |
| rshx/commands/builtins.py   | 100%     |                                    |
| rshx/core/executor.py       | 100%     |                                    |
| rshx/core/parser.py         | 100%     |                                    |
| rshx/utils/display.py       | 100%     |                                    |
| rshx/core/repl.py           |  44%     | run_shell loop needs integration tests |
| **Total**                   | **88%**  |                                    |

The run_shell function body (lines 46-70) contains the live PromptSession
loop. This requires terminal simulation to test and is deferred to
Sprint 1 integration tests.

---

## Roadmap

| Sprint | Focus                                      | Status      |
|--------|--------------------------------------------|-------------|
| 0      | Foundation, REPL, built-ins                | Complete    |
| 1      | Command history, autocomplete              | Planned     |
| 2      | Pipes, redirection                         | Planned     |
| 3      | Environment variables, aliases             | Planned     |
| 4      | Plugin system                              | Planned     |
| 5      | Custom scripting language                  | Planned     |

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Write tests for your changes.
4. Submit a pull request.
