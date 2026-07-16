# RSHX Architecture

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
