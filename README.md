# RSHX — Raghav Shell eXtended

A lightweight, extensible command-line shell written in Python.

---

## Vision

RSHX is a modern interactive shell built to explore how command-line environments work while providing a clean, modular architecture for future expansion.

Rather than recreating existing shells feature-for-feature, RSHX focuses on building a developer-friendly shell from first principles, gradually evolving through iterative engineering sprints.

Current capabilities include command execution, command history, intelligent tab completion, contextual help, and a modular execution pipeline. Future releases will introduce pipes, aliases, scripting, plugins, and AI-assisted workflows.

---

## Features

### Core Shell

* Interactive REPL powered by `prompt_toolkit`
* Built-in command execution
* External system command execution
* Persistent working directory state
* Dynamic shell prompt

### Productivity

* Command history navigation
* Persistent command history across sessions
* Built-in command tab completion
* Filesystem path completion
* Auto suggestions from command history
* Enhanced contextual help system
* Improved command error messages

### Engineering

* Modular architecture
* Comprehensive automated test suite
* Cross-platform filesystem handling
* Windows path compatibility
* Clean separation of concerns
* Extensive project documentation

---

## Quick Start

### Prerequisites

* Python 3.13+
* Git

### Installation

```powershell
# Clone the repository
git clone https://github.com/raghavendrashivam474/rshx.git

Set-Location rshx

# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements-dev.txt

# Launch RSHX
python main.py
```

---

## Built-in Commands

| Command          | Description                      |
| ---------------- | -------------------------------- |
| `help`           | Display help information         |
| `help <command>` | Show detailed help for a command |
| `pwd`            | Print current working directory  |
| `cd`             | Change current working directory |
| `clear`          | Clear the terminal               |
| `exit`           | Exit RSHX                        |

Any unrecognised command is automatically executed as an external system command.

---

## User Experience

### Command History

```text
↑
↓

Navigate previously executed commands
```

History is automatically saved and restored between sessions.

---

### Tab Completion

Supports completion for:

* Built-in commands
* Files and directories
* Relative paths
* Absolute paths
* Windows-style paths

Repeated presses of **Tab** cycle through available matches.

---

### Dynamic Prompt

```text
RSHX
C:\Users\Raghav\Projects\rshx >
```

The prompt always reflects the current working directory.

---

## Project Structure

```text
rshx/
├── rshx/
│   ├── commands/
│   │   └── builtins.py
│   │
│   ├── core/
│   │   ├── repl.py
│   │   ├── parser.py
│   │   ├── executor.py
│   │   ├── history.py
│   │   ├── completer.py
│   │   └── prompt.py
│   │
│   └── utils/
│       └── display.py
│
├── tests/
│   ├── test_builtins.py
│   ├── test_completer.py
│   ├── test_display.py
│   ├── test_executor.py
│   ├── test_history.py
│   ├── test_parser.py
│   ├── test_prompt.py
│   └── test_repl.py
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .gitattributes
└── README.md
```

---

## Running Tests

```powershell
pytest --cov=rshx --cov-report=term-missing -v
```

---

## Test Coverage

| Module            | Coverage |
| ----------------- | -------: |
| Built-in Commands |     100% |
| Parser            |     100% |
| Executor          |     100% |
| History           |     100% |
| Completer         |     100% |
| Prompt            |     100% |
| Display Utilities |     100% |
| REPL              |     37%* |
| **Overall**       |  **90%** |

*The remaining uncovered lines belong primarily to the live `PromptSession` event loop and custom key bindings, which require terminal simulation and integration testing rather than conventional unit tests.

---

## Engineering Highlights

* Typed command parsing using `ParsedCommand`
* Centralised shell session state
* Registry-based built-in command dispatch
* External command execution via `subprocess`
* Cross-platform parser supporting Windows paths
* Custom filesystem completion engine
* Configurable history persistence
* Centralised display utilities

---

## Roadmap

| Sprint | Focus                                 | Status     |
| ------ | ------------------------------------- | ---------- |
| **0**  | Foundation, REPL, Built-ins           | ✅ Complete |
| **1**  | History, Completion, Help, Prompt, UX | ✅ Complete |
| **2**  | Pipes & Redirection                   | 🔄 Planned |
| **3**  | Environment Variables & Aliases       | 📋 Planned |
| **4**  | Configuration System & Themes         | 📋 Planned |
| **5**  | Plugin Framework                      | 📋 Planned |
| **6**  | Shell Scripting (.rshx)               | 📋 Planned |
| **7**  | AI-Assisted Developer Commands        | 💡 Vision  |

---

## Development Principles

RSHX is developed around a few core principles:

* Build incrementally through well-defined sprints.
* Prioritise clean architecture over rapid feature growth.
* Maintain high automated test coverage.
* Keep modules loosely coupled and easy to extend.
* Document engineering decisions alongside implementation.
* Validate features through both automated and interactive testing.

---

## Repository

* **Branch:** `main`
* **Current Release:** `v0.2.1`
* **Python:** 3.13+
* **Tests:** 91 Passing
* **Coverage:** 90%

---

## Contributing

Contributions are welcome.

Before submitting a pull request:

1. Fork the repository.
2. Create a feature branch.
3. Follow the existing project architecture.
4. Write or update tests for new functionality.
5. Ensure all tests pass.
6. Update documentation where appropriate.
7. Submit a pull request with a clear description of the changes.

---

## License

This project is licensed under the MIT License.
