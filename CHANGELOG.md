# Changelog

All notable changes to RSHX are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Version 1.0 release candidate
- Cross-system validation
- Final repository polish
## [0.9.5] - 2026-07 - Release Sprint 2, Milestone 5

### Added
- Confirmation prompt for `startup remove` before removing persistent startup commands
- 3 new tests for startup remove confirmation behaviour

### Changed
- Version bumped to 0.9.5 in `__init__.py` and `pyproject.toml`
- Banner now displays v0.9.5

### Fixed
- Double "Goodbye!" message on exit — `cmd_exit` no longer prints its own message
- Goodbye message now printed once by the REPL loop on clean exit via `exit` or Ctrl+D

---
---
## [0.9.4] - 2026-07 - Release Sprint 2, Milestone 4

### Changed
- executor: built-in failures now include reason and help suggestion
- executor: permission errors now include reason and privilege suggestion
- executor: unexpected errors now include reason and syntax suggestion
- executor: non-zero exit code uses print_warning instead of print_info
- parser: redirect errors now include usage examples
- parser: pipe errors now explain the cause and how to fix
- pipeline: validation errors now explain position constraints
- command_queue: execution failures now include reason and syntax suggestion

### Added
- 12 new tests verifying actionable error message content across executor and parser

---
## [0.9.3] - 2026-07 - Release Sprint 2, Milestone 3

### Added
- _handle_interrupt helper responds to Ctrl+C at the prompt with a clear message and Ctrl+D hint
- _handle_eof helper responds to Ctrl+D by setting state.running=False for a clean loop exit
- 6 new tests for _handle_interrupt and _handle_eof in test_repl.py

### Changed
- Goodbye message moved after the main loop so plugin shutdown always executes on exit
- Ctrl+C at the prompt now prints a visible message instead of silently continuing
- Ctrl+D now triggers the same clean shutdown path as the exit built-in

---

## [0.9.2] - 2026-07 - Release Sprint 2, Milestone 2

### Added
- CommandQueue in core/command_queue.py for sequential multi-command execution
- CommandResult tracking per-command success, failure, and interrupt state
- QueueResult summarising full queue runs with aggregation methods
- Stop-on-first-failure behaviour by default (configurable)
- KeyboardInterrupt always halts queue regardless of stop_on_failure setting
- Queue halts immediately when shell_state.running is False
- 29 new unit tests in test_command_queue.py covering all execution paths

### Changed
- repl._execute_raw now delegates execution to CommandQueue
- Removed direct parse/execute imports from repl.py

---

## [0.9.1] - 2026-07 - Release Sprint 2, Milestone 1

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
