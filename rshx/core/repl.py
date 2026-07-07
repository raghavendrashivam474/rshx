"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Sprint 4 changes
----------------
- ConfigManager loaded at startup.
- Aliases and variables restored from configuration.
- Startup commands executed before the prompt appears.
- Theme loaded from configuration.
- Prompt built using prompt_config with theme and config options.
- Alias and variable changes persisted via ConfigManager.
"""

from dataclasses import dataclass, field
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings

from rshx.core.config import ConfigManager
from rshx.core.theme import get_theme, Theme
from rshx.core.alias_manager import AliasManager
from rshx.core.environment import Environment
from rshx.core.preprocessor import Preprocessor
from rshx.core.history import get_history
from rshx.core.completer import RshxCompleter
from rshx.core.prompt_config import build_prompt
from rshx.core.parser import parse
from rshx.core.executor import execute
from rshx.utils.display import (
    print_error,
    print_warning,
    print_info,
    print_banner,
    initialise_display,
)


# ---------------------------------------------------------------------------
# Shell state
# ---------------------------------------------------------------------------

@dataclass
class ShellState:
    """
    Mutable state for the lifetime of the shell session.

    Attributes
    ----------
    cwd : Path
        Current working directory.
    running : bool
        When False the REPL exits.
    alias_manager : AliasManager
        Session alias registry.
    environment : Environment
        Session environment variable registry.
    config_manager : ConfigManager
        Persistent configuration manager.
    theme : Theme
        Active display theme.
    """
    cwd: Path = field(default_factory=Path.cwd)
    running: bool = True
    alias_manager: AliasManager = field(default_factory=AliasManager)
    environment: Environment = field(default_factory=Environment)
    config_manager: ConfigManager = field(default_factory=ConfigManager)
    theme: Theme = field(default_factory=lambda: get_theme("default"))


# ---------------------------------------------------------------------------
# Key bindings
# ---------------------------------------------------------------------------

def _build_key_bindings() -> KeyBindings:
    """Tab cycles through completions or triggers completion."""
    bindings = KeyBindings()

    @bindings.add("tab")
    def handle_tab(event):
        buffer = event.app.current_buffer
        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=True)

    return bindings


# ---------------------------------------------------------------------------
# Startup initialisation
# ---------------------------------------------------------------------------

def _initialise_from_config(state: ShellState) -> None:
    """
    Restore aliases, variables, and theme from configuration.

    Called once at startup before the prompt appears.
    """
    cfg = state.config_manager.config

    # Restore theme
    state.theme = get_theme(cfg.theme)

    # Restore aliases
    for name, value in cfg.aliases.items():
        try:
            state.alias_manager.set(name, value)
        except ValueError:
            print_warning(f"Skipping invalid alias from config: {name}")

    # Restore environment variables
    for name, value in cfg.environment.items():
        try:
            state.environment.set(name, value)
        except ValueError:
            print_warning(f"Skipping invalid variable from config: {name}")


def _run_startup_commands(
    state: ShellState,
    preprocessor: Preprocessor,
) -> None:
    """
    Execute startup commands defined in configuration.

    Each command is preprocessed and parsed exactly as if the user
    had typed it at the prompt.
    """
    for raw in state.config_manager.config.startup_commands:
        try:
            expanded, warnings = preprocessor.process(raw)
            for warning in warnings:
                print_warning(warning)
            pipeline = parse(expanded)
            execute(pipeline, state)
        except Exception as exc:
            print_error(f"Startup command failed: '{raw}' - {exc}")


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_shell() -> None:
    """Start and run the RSHX interactive shell."""
    initialise_display()
    print_banner()

    # Load configuration
    state: ShellState = ShellState()
    state.config_manager.load()

    # Validate configuration
    errors = state.config_manager.validate()
    for error in errors:
        print_warning(error)

    # Restore persistent state
    _initialise_from_config(state)

    preprocessor: Preprocessor = Preprocessor(
        alias_manager=state.alias_manager,
        environment=state.environment,
    )

    # Execute startup commands
    _run_startup_commands(state, preprocessor)

    completer: RshxCompleter = RshxCompleter(cwd_provider=lambda: state.cwd)

    session: PromptSession = PromptSession(
        history=get_history(),
        completer=completer,
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=False,
        key_bindings=_build_key_bindings(),
    )

    while state.running:
        try:
            raw_input: str = session.prompt(
                build_prompt(
                    cwd=state.cwd,
                    theme=state.theme,
                    show_cwd=state.config_manager.config.show_cwd,
                    show_git_branch=state.config_manager.config.show_git_branch,
                )
            )

        except KeyboardInterrupt:
            print()
            continue

        except EOFError:
            print()
            break

        try:
            expanded, warnings = preprocessor.process(raw_input)
        except Exception as exc:
            print_error(f"Preprocessor error: {exc}")
            continue

        for warning in warnings:
            print_warning(warning)

        try:
            pipeline = parse(expanded)
        except ValueError as exc:
            print_error(str(exc))
            continue

        execute(pipeline, state)
        completer.update_cwd(state.cwd)
