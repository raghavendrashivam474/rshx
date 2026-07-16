# RSHX — Raghav Shell eXtended

A lightweight, extensible, cross-platform command-line shell written in Python.

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.8.3-orange.svg)](CHANGELOG.md)

---

# Overview

RSHX (Raghav Shell eXtended) is a modern command-line shell built from first principles to explore shell architecture through disciplined engineering.

Rather than replicating existing shells feature-for-feature, RSHX evolves through structured development sprints, emphasizing clean architecture, modular design, extensive automated testing, and long-term maintainability.

Current development has completed the planned feature roadmap through native scripting and entered the product hardening phase in preparation for Version 1.0.

---

# Core Features

## Interactive Shell

* Interactive REPL powered by `prompt_toolkit`
* Dynamic working-directory prompt
* Persistent command history
* Auto-suggestions
* Intelligent tab completion
* Contextual help system

---

## Command Execution

* Built-in commands
* External system commands
* Multi-stage pipelines
* Input redirection
* Output overwrite
* Output append
* AST-driven execution planning

---

## Shell Environment

* Persistent aliases
* Session aliases
* Persistent environment variables
* Variable expansion
* Command preprocessing
* Startup commands
* Cross-command shared shell state

---

## Configuration & Personalization

* TOML-based configuration
* Automatic configuration loading
* Automatic configuration generation
* Theme management
* Prompt customization
* Persistent settings
* Configuration validation

---

## Plugin Framework

* Plugin discovery
* Plugin manifests
* Plugin enable / disable
* Plugin reload
* Plugin metadata
* Dynamic command registration

---

## Native Scripting

* Native `.rshx` scripts
* Script metadata directives
* Positional arguments
* Shared shell environment
* Alias expansion
* Variable expansion
* Plugin command support
* Pipeline execution
* Redirection support
* Execution summaries

---

# Installation

## Clone Repository

```powershell
git clone https://github.com/raghavendrashivam474/rshx.git

cd rshx
```

---

## Create Virtual Environment

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

---

## Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Launch Development Version

```powershell
python main.py
```

---

## Install as Package

```powershell
pip install -e .

rshx
```

---

# Built-in Commands

| Command                                    | Description                     |
| ------------------------------------------ | ------------------------------- |
| `help [command]`                           | Display help information        |
| `clear`                                    | Clear terminal                  |
| `pwd`                                      | Print current working directory |
| `cd [path]`                                | Change working directory        |
| `alias [name=value]`                       | Create or list aliases          |
| `unalias <name>`                           | Remove alias                    |
| `set NAME=value`                           | Create environment variable     |
| `unset NAME`                               | Remove environment variable     |
| `env [NAME]`                               | Display variables               |
| `theme [name]`                             | View or change active theme     |
| `startup [add/remove/list]`                | Manage startup commands         |
| `config`                                   | Show configuration information  |
| `plugin [list/info/enable/disable/reload]` | Manage plugins                  |
| `run <script>.rshx [args]`                 | Execute an RSHX script          |
| `exit`                                     | Exit RSHX                       |

---

# Pipelines & Redirection

RSHX supports Unix-style command composition.

```text
git log --oneline | find "feat"

git status > status.txt

git log >> history.txt

sort < names.txt
```

---

# RSHX Scripting

Example script:

```text
# release_check.rshx

@name Release Check
@continue_on_error false

pytest

git status

git log --oneline -5
```

Execute:

```text
run rshx\scripts\release_check.rshx
```

Recommended workflow:

```text
set SCRIPTS=C:\Projects\rshx\rshx\scripts

startup add set SCRIPTS=C:\Projects\rshx\rshx\scripts

run %SCRIPTS%\release_check.rshx
```

---

# Plugin Development

Plugins reside inside:

```text
rshx/plugins/
```

Example layout:

```text
myplugin/

├── manifest.toml

└── plugin.py
```

Plugin management:

```text
plugin list

plugin info sysinfo

plugin enable sysinfo

plugin disable sysinfo

plugin reload
```

---

# Configuration

Configuration is stored in:

```text
~/.rshx/config.toml
```

Generated automatically on first launch.

Supports:

* Themes
* Prompt settings
* Startup commands
* Persistent aliases
* Environment variables
* Plugin settings

---

# Documentation

| Document                      | Purpose                     |
| ----------------------------- | --------------------------- |
| `ARCHITECTURE.md`             | Overall system architecture |
| `CHANGELOG.md`                | Release history             |
| `ROADMAP.md`                  | Future roadmap              |
| `CONTRIBUTING.md`             | Contribution guide          |
| `SECURITY.md`                 | Security policy             |
| `CODE_OF_CONDUCT.md`          | Community guidelines        |
| `docs/plugin_guide.md`        | Plugin development          |
| `docs/scripting_guide.md`     | RSHX scripting              |
| `docs/configuration_guide.md` | Configuration reference     |
| `docs/testing_guide.md`       | Testing guide               |

---

# Testing

Run the complete automated test suite:

```powershell
pytest --cov=rshx --cov-report=term-missing -v
```

Current quality metrics:

* **563 automated tests**
* **94% overall coverage**
* **100% coverage across core business logic**
* Extensive regression and edge-case testing

---

# Project Structure

```text
rshx/

├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
├── CHANGELOG.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
│
├── docs/
│   ├── plugin_guide.md
│   ├── scripting_guide.md
│   ├── configuration_guide.md
│   └── testing_guide.md
│
├── rshx/
│   ├── __init__.py          # Single version source
│   ├── __main__.py          # CLI entry point
│   ├── commands/
│   ├── core/
│   ├── plugins/
│   ├── scripts/
│   └── utils/
│
└── tests/
```

---

# Development Progress

| Version    | Milestone                                       | Status        |
| ---------- | ----------------------------------------------- | ------------- |
| **v0.1.0** | Sprint 0 — Foundation                           | ✅ Complete    |
| **v0.2.0** | Sprint 1 — Interactive UX                       | ✅ Complete    |
| **v0.3.0** | Sprint 2 — Pipelines & Redirection              | ✅ Complete    |
| **v0.4.0** | Sprint 3 — Shell Environment                    | ✅ Complete    |
| **v0.5.0** | Sprint 4 — Configuration & Personalization      | ✅ Complete    |
| **v0.6.0** | Sprint 5 — Plugin Framework                     | ✅ Complete    |
| **v0.7.0** | Sprint 6 — Native Scripting                     | ✅ Complete    |
| **v0.8.0** | Release Sprint 1 — Product Hardening            | ✅ Complete    |
| **v0.8.3** | Release Sprint 1.1 — Release Polish *(Current)* | ✅ In Progress |

---

# Current Status

* **Current Version:** v0.8.3
* **Branch:** `main`
* **Python:** 3.13+
* **Tests:** 563 Passing
* **Coverage:** 94%
* **License:** MIT

RSHX has completed its planned feature roadmap and is currently focused on final release polish before Version 1.0. Remaining work includes cross-system validation, packaging improvements, and a final release readiness review.

---

# Contributing

Contributions are welcome.

Before opening a pull request:

1. Fork the repository.
2. Create a feature branch.
3. Follow the existing architecture.
4. Add or update automated tests.
5. Ensure all tests pass.
6. Update documentation where necessary.
7. Submit a clear pull request describing your changes.

---

# License

This project is licensed under the **MIT License**.

See the `LICENSE` file for complete details.

---

# Owner

**Raghavendra Singh**

Engineering Student • Software Developer • Systems Programming Enthusiast

RSHX is a long-term engineering project exploring modern shell architecture through incremental, engineering-driven development. The project emphasizes clean design, extensibility, automated testing, and release discipline while serving as a practical platform for learning systems programming concepts.

**GitHub:** https://github.com/raghavendrashivam474/rshx
