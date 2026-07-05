# RSHX — Raghav Shell eXtended

A lightweight, extensible, cross-platform command-line shell written in Python.

RSHX is a long-term engineering project focused on understanding how modern shells work by building one from first principles. Rather than replicating an existing shell feature-for-feature, RSHX evolves through iterative engineering sprints with a strong emphasis on clean architecture, modularity, testing, and extensibility.

---

# Vision

RSHX is designed around four engineering principles:

* ⚙️ **Built from First Principles**
* 🧩 **Modular by Design**
* 🧪 **Engineering Driven**
* 🚀 **Extensible for the Future**

Every sprint focuses on improving one aspect of the shell while preserving architectural integrity.

The long-term vision is to evolve RSHX from a simple interactive shell into a complete developer productivity platform supporting scripting, plugins, intelligent workflows, and AI-assisted development.

---

# Current Architecture

```text
                         User

                          │

                          ▼

                 Prompt Toolkit UI

                          │

      ┌───────────────────┼───────────────────┐

      ▼                   ▼                   ▼

 Command History     Auto Completion     Prompt Renderer

                          │

                          ▼

                     Tokenizer

                          │

                          ▼

                    Command Parser

                          │

                          ▼

                  Abstract Syntax Tree

                          │

                          ▼

                   Command Executor

                          │

          ┌───────────────┼─────────────────┐

          ▼               ▼                 ▼

     Built-in Engine   Pipeline Engine   Process Manager

                          │

                  Redirect Manager

                          │

                          ▼

                    Operating System
```

---

# Current Features

## Core Shell

* Interactive REPL powered by `prompt_toolkit`
* Dynamic shell prompt
* Built-in command execution
* External command execution
* Persistent working directory
* Clean command parsing pipeline

---

## Productivity

* Command history navigation
* Persistent command history
* History-based auto suggestions
* Built-in command completion
* Filesystem path completion
* Dynamic prompt
* Enhanced contextual help
* Improved command error reporting

---

## Command Composition

* Multi-stage pipelines
* Output redirection (`>`)
* Output append (`>>`)
* Input redirection (`<`)
* Combined pipeline and redirection
* Pipeline validation
* Structured execution planning

Examples:

```text
git log --oneline | find "feat"

dir > listing.txt

whoami >> users.txt

sort < names.txt

git log --oneline | find "fix" > fixes.txt
```

---

## Engineering

* Modular architecture
* Abstract Syntax Tree (AST)
* Pipeline execution engine
* Process lifecycle management
* Redirect management
* Cross-platform filesystem support
* Windows path compatibility
* Comprehensive automated test suite
* Extensive engineering documentation

---

# Quick Start

## Prerequisites

* Python 3.13+
* Git

---

## Installation

```powershell
# Clone repository
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

# Built-in Commands

| Command          | Description                |
| ---------------- | -------------------------- |
| `help`           | Display available commands |
| `help <command>` | Detailed command help      |
| `pwd`            | Print current directory    |
| `cd`             | Change directory           |
| `clear`          | Clear terminal             |
| `exit`           | Exit RSHX                  |

Any unrecognised command is automatically executed as an external system command.

---

# User Experience

## Command History

* Up/Down navigation
* Persistent history across sessions
* History-based auto suggestions

---

## Intelligent Completion

Supports completion for:

* Built-in commands
* Files
* Directories
* Relative paths
* Absolute paths
* Windows paths

Tab cycles through available completions.

---

## Dynamic Prompt

```text
RSHX
C:\Users\Raghav\Projects\rshx >
```

The prompt always reflects the current working directory.

---

# Command Execution Flow

```text
Keyboard Input

        │

        ▼

Prompt Toolkit

        │

History
Completion
Suggestions

        │

        ▼

Tokenizer

        │

        ▼

Parser

        │

        ▼

Pipeline AST

        │

        ▼

Executor

        │

 ┌──────┼───────────────┐

 ▼      ▼               ▼

Built-ins  Pipeline   External Command

                  │

          Process Manager

                  │

          Redirect Manager

                  │

                  ▼

          Operating System
```

---

# Project Structure

```text
rshx/

├── main.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
├── .gitattributes
│
├── rshx/
│
│   ├── commands/
│   │   ├── __init__.py
│   │   └── builtins.py
│   │
│   ├── core/
│   │   ├── ast.py
│   │   ├── completer.py
│   │   ├── executor.py
│   │   ├── history.py
│   │   ├── parser.py
│   │   ├── pipeline.py
│   │   ├── process.py
│   │   ├── prompt.py
│   │   ├── redirect.py
│   │   └── repl.py
│   │
│   └── utils/
│       └── display.py
│
└── tests/
    ├── test_ast.py
    ├── test_ast_parser.py
    ├── test_builtins.py
    ├── test_completer.py
    ├── test_display.py
    ├── test_executor.py
    ├── test_history.py
    ├── test_parser.py
    ├── test_pipeline.py
    ├── test_process.py
    ├── test_prompt.py
    ├── test_redirect.py
    └── test_repl.py
```

---

# Running Tests

```powershell
pytest --cov=rshx --cov-report=term-missing -v
```

---

# Test Coverage

| Module      | Coverage |
| ----------- | -------: |
| AST         |     100% |
| Built-ins   |     100% |
| Parser      |     100% |
| Executor    |     100% |
| Pipeline    |     98%* |
| Process     |     100% |
| Redirect    |     100% |
| History     |     100% |
| Completer   |     100% |
| Prompt      |     100% |
| Display     |     100% |
| REPL        |    37%** |
| **Overall** |  **94%** |

* One defensive branch is intentionally unreachable due to pipeline validation rules.

** Remaining uncovered lines belong to the live `PromptSession` loop and custom key bindings, which require terminal simulation rather than conventional unit testing.

---

# Engineering Highlights

* AST-driven command execution
* Structured pipeline representation
* Registry-based built-in dispatch
* Dedicated pipeline execution engine
* Process lifecycle abstraction
* Redirect abstraction
* Cross-platform parser
* Windows CMD compatibility
* Platform-aware process execution
* Separation of parsing and execution
* Comprehensive regression testing

---

# Development Progress

| Sprint  | Focus                                     | Status     |
| ------- | ----------------------------------------- | ---------- |
| **0**   | Foundation, REPL, Built-ins               | ✅ Complete |
| **1**   | History, Completion, Help, Prompt         | ✅ Complete |
| **2**   | AST, Pipelines, Redirection               | ✅ Complete |
| **2.1** | Platform compatibility & regression fixes | ✅ Complete |
| **3**   | Environment Variables & Aliases           | 📋 Planned |
| **4**   | Configuration System & Themes             | 📋 Planned |
| **5**   | Plugin Framework                          | 📋 Planned |
| **6**   | Shell Scripting (.rshx)                   | 📋 Planned |
| **7**   | AI-Assisted Developer Commands            | 💡 Vision  |

---

# Development Principles

RSHX is developed using an engineering-first workflow.

* Build incrementally through structured sprints.
* Prefer architectural quality over rapid feature growth.
* Maintain high automated test coverage.
* Separate parsing, execution, and orchestration.
* Document architectural decisions.
* Perform manual testing after every sprint.
* Convert discovered defects into permanent regression tests.

---

# Repository

| Property        | Value           |
| --------------- | --------------- |
| Current Release | **v0.3.1**      |
| Branch          | **main**        |
| Python          | **3.13+**       |
| Tests           | **193 Passing** |
| Coverage        | **94%**         |
| License         | **MIT**         |

---

# Future Vision

Future development will continue building on the architecture established through Sprint 2.

Planned capabilities include:

* Environment variables
* Aliases
* Configuration system
* Themes
* Plugin framework
* Shell scripting
* Background jobs
* Job control
* AI-assisted workflows

Because RSHX now uses an AST-based execution model, future capabilities can be implemented as extensions rather than architectural rewrites.

---

# Contributing

Contributions are welcome.

Before submitting a pull request:

1. Fork the repository.
2. Create a feature branch.
3. Follow the established architecture.
4. Write or update automated tests.
5. Ensure all tests pass.
6. Update documentation where necessary.
7. Submit a pull request describing the change clearly.

---

# License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

# Owner

**Raghavendra Singh**

Engineering Student • Software Developer • Systems Programming Enthusiast

RSHX is a long-term engineering project focused on understanding and building modern shell architecture from first principles. The project emphasizes clean software design, modular architecture, automated testing, and iterative engineering, serving both as a practical developer tool and an exploration of operating systems, process management, command parsing, and shell execution models.

**GitHub:** https://github.com/raghavendrashivam474/rshx
