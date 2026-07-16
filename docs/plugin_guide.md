# RSHX Plugin Development Guide

## Overview

Plugins extend RSHX with new commands without modifying core source.

## Structure

\\\
rshx/plugins/myplugin/
    __init__.py
    manifest.toml
    plugin.py
\\\

## manifest.toml

\\\	oml
name = "myplugin"
version = "1.0.0"
description = "What this plugin does."
author = "Your Name"
commands = ["mycmd"]
min_rshx_version = "0.8.0"
\\\

Important: Write manifest.toml as UTF-8 WITHOUT BOM.
Use [System.Text.UTF8Encoding]::new(false) in PowerShell.

## plugin.py

\\\python
_api = None

def initialise(api):
    global _api
    _api = api
    api.register_command("mycmd", _cmd_mycmd, "My command description")

def shutdown():
    pass

def _cmd_mycmd(args, shell_state):
    _api.print_success(f"Hello from myplugin! Args: {args}")
\\\

## Plugin API

| Method | Description |
|--------|-------------|
| register_command(name, handler, description) | Register a command |
| register_help(command, description, usage, examples, notes) | Register help |
| get_config() | Get plugin configuration dict |
| print_output(message) | Standard output |
| print_success(message) | Success output |
| print_error(message) | Error output |
| print_info(message) | Informational output |
| print_warning(message) | Warning output |

## Plugin Configuration

Add to ~/.rshx/config.toml:

\\\	oml
[plugins.myplugin]
enabled = true
mykey = "myvalue"
\\\

Access in plugin:

\\\python
cfg = api.get_config()
value = cfg.get("mykey", "default")
\\\

## Lifecycle

1. RSHX discovers plugin directory on startup
2. manifest.toml is validated
3. plugin.py is imported
4. initialise(api) is called
5. Commands are available to the user
6. shutdown() is called when RSHX exits
