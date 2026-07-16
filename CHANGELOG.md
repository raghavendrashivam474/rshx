# Changelog

All notable changes to RSHX are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.8.0] - 2025-07 - Release Sprint 1

### Changed
- Single authoritative version source via rshx/__init__.py
- Version banner now reads from __version__ at runtime
- pyproject.toml updated with complete package metadata and CLI entry point
- Documentation refresh across all guides

### Fixed
- Version banner mismatch across sprints (permanent fix)

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
- Version banner corrected to v0.7.0

---

## [0.6.0] - 2025-07 - Sprint 5

### Added
- Plugin Framework
- Plugin Manager with full lifecycle management
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
- Theme system with default, dark, light themes
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

---

## [0.3.0] - 2025-07 - Sprint 2

### Added
- Command pipelines with arbitrary stage count
- Output redirection with overwrite and append
- Input redirection from files
- Abstract Syntax Tree representation
- Graceful syntax error handling

### Fixed
- Windows backslash path handling
- Tab completion inline behaviour
- CMD built-in support in pipelines

---

## [0.2.0] - 2025-07 - Sprint 1

### Added
- Command history with Up/Down arrow navigation
- Persistent history saved to ~/.rshx/history
- Tab completion for built-in commands and paths
- Dynamic two-line prompt
- Enhanced help system with per-command detail
- Did-you-mean suggestions

---

## [0.1.0] - 2025-07 - Sprint 0

### Added
- Interactive REPL using prompt_toolkit
- Built-in commands: help, clear, pwd, cd, exit
- External command execution via subprocess
- Working directory state management
- Display utilities with colorama
- Input parsing using shlex
