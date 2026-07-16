# RSHX Configuration Guide

## Configuration File Location

~/.rshx/config.toml

Created automatically on first launch.

## Full Configuration Reference

\\\	oml
[general]
version = "0.8.0"
theme = "default"

[prompt]
show_cwd = true
show_git_branch = false

[aliases]
gs = "git status"
ll = "dir"

[environment]
PROJECTS = "C:\\Projects"
EDITOR = "code"

[startup]
commands = [
    "alias c=clear",
]

[plugins.hello]
enabled = true

[plugins.sysinfo]
enabled = true
\\\

## Themes

| Theme | Description |
|-------|-------------|
| default | Standard colours |
| dark | Bright colours for dark terminals |
| light | Subdued colours for light terminals |

Change theme:

\\\
theme dark
\\\

## Prompt Options

Show git branch:

\\\	oml
[prompt]
show_git_branch = true
\\\

## Startup Commands

Commands that run automatically when RSHX launches:

\\\
startup add alias gs=git status
startup list
startup remove alias gs=git status
\\\

## Plugin Configuration

\\\	oml
[plugins.myplugin]
enabled = false
mykey = "myvalue"
\\\

## Corruption Recovery

If config.toml is corrupted RSHX:
1. Creates config.toml.bak as a backup
2. Loads default configuration
3. Starts normally
