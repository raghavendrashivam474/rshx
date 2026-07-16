"""
update_docs.py
Temporary script to update documentation files.
Run with: python update_docs.py
Delete after use.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# scripting_guide.md
# ---------------------------------------------------------------------------

Path("docs/scripting_guide.md").write_text("""# RSHX Scripting Guide

## Overview

.rshx files contain sequences of RSHX commands that execute
through the existing shell pipeline.

## Running a Script

Scripts are resolved relative to the current working directory.
Always use the full path or a variable.

    run rshx\\scripts\\hello.rshx
    run rshx\\scripts\\greet.rshx Raghav

Recommended pattern using a variable:

    set SCRIPTS=C:\\Projects\\rshx\\rshx\\scripts
    run %SCRIPTS%\\hello.rshx
    run %SCRIPTS%\\greet.rshx Raghav

Add the variable as a startup command so it is always available:

    startup add set SCRIPTS=C:\\Projects\\rshx\\rshx\\scripts

## Script Format

    # This is a comment

    @name My Script
    @description What this script does
    @continue_on_error false

    pwd
    git status
    pytest

## Directives

| Directive | Values | Default | Description |
|-----------|--------|---------|-------------|
| @name | any string | filename | Script display name |
| @description | any string | empty | Script description |
| @continue_on_error | true / false | false | Continue after failures |

## Positional Arguments

    run greet.rshx Raghav

In the script:

    echo Hello %1

Arguments are available as %1 %2 %3 etc.
Missing arguments expand to empty string.

## Variable Expansion

    set MYDIR=C:\\Projects
    run navigate.rshx

In the script:

    cd %MYDIR%
    pwd

## Alias Expansion

Aliases defined in the session are available in scripts.

    alias gs=git status
    run check.rshx

In check.rshx:

    gs

## Failure Behaviour

Default stops on first failure:

    @continue_on_error false

    pytest
    git push

If pytest fails, git push does not run.

Continue on error:

    @continue_on_error true

    pytest
    git status

Both commands run regardless of pytest result.

## Interactive Shell Behaviour

RSHX reads one command per prompt line. When using the
interactive shell, enter each command separately and wait
for the prompt before entering the next.

Do not paste multiple commands at once as the second line
will be treated as an argument to the first command.

## Execution Summary

After each script run RSHX prints:

    Script: My Script
    Commands executed : 3
    Succeeded         : 3
    Failed            : 0
    Duration          : 1.23s
    Result: SUCCESS
""", encoding="utf-8")

print("docs/scripting_guide.md - done")

# ---------------------------------------------------------------------------
# CHANGELOG.md
# ---------------------------------------------------------------------------

Path("CHANGELOG.md").write_text("""# Changelog

All notable changes to RSHX are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Version 1.0 release candidate
- Cross-system validation
- Final repository polish

---

## [0.8.0] - 2025-07 - Release Sprint 1

### Added
- Single authoritative version source via rshx/__init__.py
- rshx/__main__.py as package entry point
- CLI entry point: rshx = rshx.__main__:main
- Full documentation suite: README, CHANGELOG, ARCHITECTURE,
  CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, ROADMAP
- docs/ directory with plugin, scripting, configuration, testing guides
- 24 new edge case tests in test_edge_cases.py
- Improved plugin error messages with recovery hints
- Improved ScriptError.format() with filename and recovery tip
- pyproject.toml with complete package metadata

### Fixed
- Version banner mismatch - now reads from __version__ at runtime
- pyproject.toml BOM issue - rewritten without BOM
- pyproject.toml build backend - changed to setuptools.build_meta
- CLI entry point - moved from main.py to rshx.__main__:main

---

## [0.7.0] - 2025-07 - Sprint 6

### Added
- .rshx native scripting format
- Script Loader with UTF-8 validation
- Script Parser with directives and line numbers
- Script Runtime reusing existing RSHX pipeline
- Positional arguments via %1 %2 syntax
- Stop-on-error and continue-on-error modes
- Execution summary with structured diagnostics
- run built-in command
- Seven reference scripts

### Fixed
- Positional argument %1 bare syntax expansion
- Environment variable regex updated for digit-only names

---

## [0.6.0] - 2025-07 - Sprint 5

### Added
- Plugin Framework with discovery, loading, lifecycle management
- Plugin Registry integrated into command execution
- Plugin API for safe plugin-shell communication
- Plugin configuration via config.toml
- hello and sysinfo example plugins
- plugin built-in command

### Fixed
- Plugin manifest UTF-8 BOM issue

---

## [0.5.0] - 2025-07 - Sprint 4

### Added
- Persistent configuration via ~/.rshx/config.toml
- Theme system: default, dark, light
- Git branch display in prompt
- Startup commands
- theme, startup, config built-in commands
- Plugin configuration section in config.toml

---

## [0.4.0] - 2025-07 - Sprint 3

### Added
- Alias system with session and persistent storage
- Environment variable system with %VAR% expansion
- Command preprocessor layer
- alias, unalias, set, unset, env built-in commands

### Fixed
- CMD built-ins work via aliases on Windows
- shell=True applied consistently across executor paths

---

## [0.3.0] - 2025-07 - Sprint 2

### Added
- Command pipelines with arbitrary stage count
- Output redirection with overwrite and append
- Input redirection from files
- Abstract Syntax Tree representation
- Graceful syntax error handling

### Fixed
- Windows backslash path handling in parser
- Tab completion inline behaviour
- CMD built-in support in pipelines via shell=True
- Quoted arguments preserved for external commands

---

## [0.2.0] - 2025-07 - Sprint 1

### Added
- Command history with Up/Down arrow navigation
- Persistent history saved to ~/.rshx/history
- Tab completion for built-in commands and paths
- Dynamic two-line prompt with configurable display
- Enhanced help system with per-command detail
- Did-you-mean suggestions for unknown commands

### Fixed
- Windows path backslash handling in completer
- Case-insensitive path completion

---

## [0.1.0] - 2025-07 - Sprint 0

### Added
- Interactive REPL using prompt_toolkit
- Built-in commands: help, clear, pwd, cd, exit
- External command execution via subprocess
- Working directory state management
- Display utilities with colorama for coloured output
- Input parsing using shlex
""", encoding="utf-8")

print("CHANGELOG.md - done")

# ---------------------------------------------------------------------------
# README.md
# ---------------------------------------------------------------------------

Path("README.md").write_text("""# RSHX - Raghav Shell eXtended

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
    .venv\\Scripts\\Activate.ps1
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

    set SCRIPTS=C:\\Projects\\rshx\\rshx\\scripts
    run %SCRIPTS%\\release.rshx

Add to startup so the variable is always available:

    startup add set SCRIPTS=C:\\Projects\\rshx\\rshx\\scripts

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
""", encoding="utf-8")

print("README.md - done")

# ---------------------------------------------------------------------------
# ARCHITECTURE.md
# ---------------------------------------------------------------------------

Path("ARCHITECTURE.md").write_text("""# RSHX Architecture

## Overview

RSHX is a layered command-line shell built in Python.
Each layer has a single, clearly defined responsibility.

## Execution Pipeline

    User
      |
      v
    Prompt Session  (prompt_toolkit - history, completion, key bindings)
      |
      v
    Script Runtime  (.rshx files feed into the same pipeline)
      |
      v
    Command Preprocessor
      |-- Alias Resolver       (AliasManager)
      |-- Variable Resolver    (Environment)
      |-- Positional Args      (script_runtime._expand_positional_bare)
      |
      v
    Parser          (shlex tokeniser -> PipelineNode AST)
      |
      v
    AST             (CommandNode, RedirectNode, PipelineNode)
      |
      v
    Executor
      |-- Built-in Registry   (BUILTIN_REGISTRY)
      |-- Plugin Registry     (PluginRegistry)
      |-- External Commands   (subprocess with shell=True on Windows)
      |-- Pipeline Executor   (pipeline.py)
           |-- Process Manager  (process.py)
           |-- Redirect Manager (redirect.py)
      |
      v
    Operating System

## Module Map

    rshx/
    |-- __init__.py              Single version source (__version__ = 0.8.0)
    |-- __main__.py              CLI entry point (rshx = rshx.__main__:main)
    |
    |-- commands/
    |   |-- builtins.py          All 15 built-in command implementations
    |
    |-- core/
    |   |-- repl.py              REPL loop and ShellState
    |   |-- parser.py            Input tokenisation and AST construction
    |   |-- executor.py          Command routing
    |   |-- ast.py               AST node definitions
    |   |-- pipeline.py          Pipeline execution orchestration
    |   |-- process.py           Child process lifecycle
    |   |-- redirect.py          File handle management
    |   |-- preprocessor.py      Alias and variable expansion
    |   |-- alias_manager.py     Alias registry
    |   |-- environment.py       Variable registry with %VAR% expansion
    |   |-- history.py           Persistent command history
    |   |-- completer.py         Tab completion
    |   |-- prompt.py            Legacy prompt (Sprint 0)
    |   |-- prompt_config.py     Configurable prompt with git branch
    |   |-- config.py            TOML configuration manager
    |   |-- theme.py             Visual theme definitions
    |   |-- plugin_api.py        Safe plugin interface
    |   |-- plugin_loader.py     Plugin discovery and loading
    |   |-- plugin_manager.py    Plugin lifecycle management
    |   |-- plugin_registry.py   Plugin command registry
    |   |-- script_types.py      Script data models
    |   |-- script_loader.py     Script file loading
    |   |-- script_parser.py     Script parsing
    |   |-- script_runtime.py    Script execution
    |
    |-- plugins/
    |   |-- hello/               Example greeting plugin
    |   |-- sysinfo/             Example system info plugin
    |
    |-- scripts/
    |   |-- hello.rshx           Demo script
    |   |-- greet.rshx           Positional argument demo
    |   |-- project_check.rshx   Project verification script
    |   |-- release_check.rshx   Release verification script
    |   |-- stoptest.rshx        Stop-on-error demo
    |   |-- continuetest.rshx    Continue-on-error demo
    |   |-- vartest.rshx         Variable expansion demo
    |
    |-- utils/
    |   |-- display.py           Terminal output utilities

## Key Design Decisions

### Single Version Source
rshx/__init__.py defines __version__. All other files read from it.
A test verifies rshx/__init__.py and pyproject.toml always match.

### Layered Architecture
Each layer communicates only with adjacent layers.
The parser never knows about aliases.
The executor never reads configuration files.

### Single ShellState
All mutable session state lives in one ShellState dataclass.
Scripts and interactive commands share the same state instance.

### Plugin API Boundary
Plugins never import from rshx.core directly.
All plugin-shell communication goes through PluginAPI.

### Script as Input Source
.rshx scripts feed into the same pipeline as interactive input.
The script runtime does not duplicate any execution logic.

### Windows Compatibility
shell=True used on Windows so CMD built-ins work in pipelines.
posix=False used in shlex so backslashes are preserved in paths.
All TOML files written as UTF-8 without BOM.

### Configuration Hierarchy
Configuration file: ~/.rshx/config.toml
History file: ~/.rshx/history
Both created automatically on first launch.
""", encoding="utf-8")

print("ARCHITECTURE.md - done")
print()
print("All documentation updated successfully.")
