# RSHX — Raghav Shell eXtended

A lightweight, extensible, cross-platform command-line shell written in Python.

RSHX is a long-term engineering project focused on understanding how modern command-line shells work by building one from first principles. Rather than replicating existing shells feature-for-feature, RSHX evolves through structured engineering sprints with a strong emphasis on clean architecture, modularity, automated testing, and extensibility.

---

# Vision

RSHX is designed around four engineering principles:

* ⚙️ **Built from First Principles**
* 🧩 **Modular by Design**
* 🧪 **Engineering Driven**
* 🚀 **Extensible for the Future**

Every sprint introduces one new architectural capability while preserving clean separation of concerns and maintaining backwards compatibility.

The long-term vision is to evolve RSHX from a simple interactive shell into a modern developer platform supporting plugins, scripting, automation, personalization, and AI-assisted workflows.

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

                 Command Preprocessor

                            │

          ┌─────────────────┴─────────────────┐

          ▼                                   ▼

    Alias Resolver                   Variable Resolver

          │                                   │

          └─────────────────┬─────────────────┘

                            ▼

                       Tokenizer

                            ▼

                     Command Parser

                            ▼

                 Abstract Syntax Tree

                            ▼

                  Command Executor

                            │

         ┌──────────────────┼──────────────────┐

         ▼                  ▼                  ▼

    Built-in Engine   Pipeline Engine   Process Manager

                            │

                     Redirect Manager

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
* Cross-platform command execution

---

## Productivity

* Command history navigation
* Persistent history across sessions
* History-based auto suggestions
* Built-in command completion
* Filesystem path completion
* Windows path completion
* Enhanced contextual help
* Improved command error reporting

---

## Command Composition

* AST-driven parsing
* Multi-stage pipelines (`|`)
* Output redirection (`>`)
* Output append (`>>`)
* Input redirection (`<`)
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

## Shell Environment

* Session-scoped aliases
* Alias expansion
* Alias management
* Session-scoped environment variables
* Variable expansion
* Command preprocessing
* Alias support inside pipelines
* Variable expansion inside pipelines
* Variable expansion inside redirected commands
* Alias support for built-ins
* Alias support for external commands

Examples:

```text
alias gs="git status"

alias ll="dir"

set PROJECT=C:\Projects

gs

cd %PROJECT%

gs | find "modified"

cat %PROJECT%\README.md
```

---

## Engineering

* Modular architecture
* Command preprocessing layer
* Abstract Syntax Tree (AST)
* Dedicated pipeline execution engine
* Process lifecycle abstraction
* Redirect abstraction
* Alias manager
* Environment manager
* Cross-platform parser
* Windows CMD compatibility
* Platform-aware process execution
* Clean separation of concerns
* Comprehensive regression testing
* Extensive engineering documentation

---

# Quick Start

## Prerequisites

* Python 3.13+
* Git

---

## Installation

```powershell
git clone https://github.com/raghavendrashivam474/rshx.git

Set-Location rshx

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt

python main.py
```

---

# Built-in Commands

| Command          | Description                     |
| ---------------- | ------------------------------- |
| `help`           | Display available commands      |
| `help <command>` | Detailed help for a command     |
| `pwd`            | Print current working directory |
| `cd`             | Change working directory        |
| `clear`          | Clear terminal                  |
| `exit`           | Exit RSHX                       |
| `alias`          | Create or list aliases          |
| `unalias`        | Remove aliases                  |
| `set`            | Create environment variables    |
| `unset`          | Remove environment variables    |
| `env`            | Display environment variables   |

Any unrecognised command is automatically executed as an external system command.

---

# User Experience

## Command History

* Navigate using ↑ and ↓
* Persistent command history
* History-based suggestions

---

## Intelligent Completion

Supports completion for:

* Built-in commands
* Files
* Directories
* Relative paths
* Absolute paths
* Windows paths

Repeated presses of **Tab** cycle through available completions.

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

Command Preprocessor

        │

 ┌──────┴─────────┐

 ▼                ▼

Alias Resolver  Variable Resolver

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

 ┌──────┼──────────────┐

 ▼      ▼              ▼

Built-ins Pipeline External Commands

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
│   │   ├── alias_manager.py
│   │   ├── ast.py
│   │   ├── completer.py
│   │   ├── environment.py
│   │   ├── executor.py
│   │   ├── history.py
│   │   ├── parser.py
│   │   ├── pipeline.py
│   │   ├── preprocessor.py
│   │   ├── process.py
│   │   ├── prompt.py
│   │   ├── redirect.py
│   │   └── repl.py
│   │
│   └── utils/
│       └── display.py
│
└── tests/
    ├── test_alias_manager.py
    ├── test_ast.py
    ├── test_ast_parser.py
    ├── test_builtins.py
    ├── test_completer.py
    ├── test_display.py
    ├── test_environment.py
    ├── test_executor.py
    ├── test_history.py
    ├── test_parser.py
    ├── test_pipeline.py
    ├── test_preprocessor.py
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

| Module              | Coverage |
| ------------------- | -------: |
| Alias Manager       |     100% |
| Environment Manager |     100% |
| Preprocessor        |     100% |
| AST                 |     100% |
| Built-ins           |     100% |
| Parser              |     100% |
| Executor            |     100% |
| History             |     100% |
| Completer           |     100% |
| Prompt              |     100% |
| Process             |     100% |
| Redirect            |     100% |
| Pipeline            |     98%* |
| REPL                |    37%** |
| **Overall**         |  **95%** |

* One defensive branch remains intentionally unreachable because invalid pipelines are rejected during validation.

** Remaining uncovered lines belong to the interactive `PromptSession` event loop and custom key bindings, which require terminal simulation rather than conventional unit testing.

---

# Engineering Highlights

* Command preprocessing architecture
* Alias resolution layer
* Environment variable expansion
* AST-driven command execution
* Dedicated pipeline execution engine
* Process lifecycle abstraction
* Redirect abstraction
* Registry-based built-in dispatch
* Cross-platform parser
* Windows CMD compatibility
* Platform-aware process execution
* Separation of preprocessing, parsing, and execution
* Comprehensive regression testing

---

# Development Progress

| Sprint  | Focus                                          | Status     |
| ------- | ---------------------------------------------- | ---------- |
| **0**   | Foundation, REPL & Built-ins                   | ✅ Complete |
| **1**   | History, Completion, Prompt & Help             | ✅ Complete |
| **2**   | AST, Pipelines & Redirection                   | ✅ Complete |
| **2.1** | Platform Compatibility & Regression Fixes      | ✅ Complete |
| **3**   | Environment Variables, Aliases & Preprocessing | ✅ Complete |
| **4**   | Configuration & Personalization                | 📋 Planned |
| **5**   | Plugin Framework                               | 📋 Planned |
| **6**   | RSHX Scripting (.rshx)                         | 📋 Planned |
| **7**   | AI-Assisted Developer Workflows                | 💡 Vision  |

---

# Development Principles

RSHX is developed using an engineering-first workflow.

* Build incrementally through structured sprints.
* Introduce one architectural capability per sprint.
* Prefer clean architecture over rapid feature growth.
* Maintain high automated test coverage.
* Separate preprocessing, parsing, and execution.
* Document engineering decisions alongside implementation.
* Perform manual verification after every sprint.
* Convert discovered defects into permanent regression tests.

---

# Repository

| Property        | Value           |
| --------------- | --------------- |
| Current Release | **v0.4.2**      |
| Branch          | **main**        |
| Python          | **3.13+**       |
| Tests           | **282 Passing** |
| Coverage        | **95%**         |
| License         | **MIT**         |

---

# Future Vision

The next development milestones focus on extending the shell without disrupting the architecture established during the first four development phases.

Planned capabilities include:

* Persistent configuration system
* Themes and prompt customization
* Plugin framework
* Shell scripting (`.rshx`)
* Workflow automation
* AI-assisted developer commands

Because RSHX now separates preprocessing, parsing, execution, and process management into independent layers, these future capabilities can be added as extensions rather than architectural rewrites.

---

# Contributing

Contributions are welcome.

Before submitting a pull request:

1. Fork the repository.
2. Create a feature branch.
3. Follow the established architecture.
4. Write or update automated tests.
5. Ensure all tests pass.
6. Update documentation where appropriate.
7. Submit a pull request describing your changes clearly.

---

# License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

# Owner

**Raghavendra Singh**

Engineering Student • Software Developer • Systems Programming Enthusiast

RSHX is a long-term engineering project dedicated to understanding modern shell architecture through incremental, engineering-driven development. The project explores command parsing, process management, shell environments, workflow automation, and extensible system design while serving as both a practical developer tool and an educational exploration of operating system concepts.

**GitHub:** https://github.com/raghavendrashivam474/rshx
