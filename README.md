# RSHX - Raghav Shell eXtended

A lightweight, extensible command-line shell written in Python.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.8.0-orange.svg)](CHANGELOG.md)

---

## Features

| Feature | Description |
|---------|-------------|
| Interactive REPL | prompt_toolkit with history and completion |
| Pipelines | Multi-stage command composition |
| Redirection | Output overwrite, append, and input redirect |
| Aliases | Persistent command shortcuts |
| Variables | Environment variable expansion |
| Persistent Config | TOML configuration at ~/.rshx/config.toml |
| Themes | default, dark, light |
| Plugin Framework | Extensible command system |
| Scripting | Native .rshx workflow scripts |

---

## Quick Start

### Install from source

    git clone https://github.com/raghavendrashivam474/rshx.git
    cd rshx
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python main.py

### Install as package

    pip install -e .
    rshx

---

## Built-in Commands

| Command | Description |
|---------|-------------|
| help [command] | Show help |
| clear | Clear screen |
| pwd | Print working directory |
| cd [path] | Change directory |
| alias [name=value] | Manage aliases |
| unalias name | Remove alias |
| set [NAME=value] | Manage variables |
| unset NAME | Remove variable |
| env [NAME] | Display variables |
| theme [name] | Set or display theme |
| startup [add/remove/list] | Manage startup commands |
| config | Show config file path |
| plugin [list/info/enable/disable/reload] | Manage plugins |
| run script.rshx [args] | Execute script |
| exit | Exit RSHX |

---

## Pipelines and Redirection

    git log --oneline | find "feat"
    git status > status.txt
    git log >> history.txt
    sort < names.txt

---

## Scripting

    # release.rshx
    @name Release Check
    @continue_on_error false

    pytest
    git status
    git log --oneline -5

Run using a variable for convenience:

    set SCRIPTS=C:\Projects\rshx\rshx\scripts
    run %SCRIPTS%\release.rshx

Add to startup so the variable is always available:

    startup add set SCRIPTS=C:\Projects\rshx\rshx\scripts

---

## Plugins

Place plugins in rshx/plugins/:

    rshx/plugins/myplugin/
        manifest.toml
        plugin.py

    plugin list
    plugin enable myplugin
    plugin disable myplugin

---

## Configuration

Configuration file: ~/.rshx/config.toml

Created automatically on first launch.
See docs/configuration_guide.md for the full reference.

---

## Documentation

| Document | Description |
|----------|-------------|
| ARCHITECTURE.md | System design and module map |
| CHANGELOG.md | Version history |
| ROADMAP.md | Future plans |
| CONTRIBUTING.md | How to contribute |
| docs/plugin_guide.md | Plugin development |
| docs/scripting_guide.md | .rshx scripting |
| docs/configuration_guide.md | Configuration reference |
| docs/testing_guide.md | Testing guide |

---

## Testing

    pytest --cov=rshx --cov-report=term-missing -v

Current: 563 tests, 94% coverage.

---

## Project Structure

    rshx/
    |-- __init__.py            Single version source
    |-- __main__.py            CLI entry point
    |-- commands/builtins.py   All built-in commands
    |-- core/                  Core shell modules
    |-- plugins/               Example plugins
    |-- scripts/               Reference .rshx scripts
    |-- utils/display.py       Terminal output utilities
    tests/                     Test suite
    docs/                      Documentation guides
    main.py                    Legacy entry point

---

## License

MIT License. See LICENSE for details.

---

*Raghavendra Singh - RSHX v0.8.0*
