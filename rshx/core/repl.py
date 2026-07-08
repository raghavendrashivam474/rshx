"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Sprint 5 changes
----------------
- ShellState now holds a PluginManager instance.
- Plugin discovery and loading runs during startup.
- Plugin shutdown called on exit.
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
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.plugin_manager import PluginManager
from rshx.utils.display import (
    print_error,
    print_warning,
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
    running : bool
    alias_manager : AliasManager
    environment : Environment
    config_manager : ConfigManager
    theme : Theme
    plugin_manager : PluginManager
    """
    cwd: Path = field(default_factory=Path.cwd)
    running: bool = True
    alias_manager: AliasManager = field(default_factory=AliasManager)
    environment: Environment = field(default_factory=Environment)
    config_manager: ConfigManager = field(default_factory=ConfigManager)
    theme: Theme = field(default_factory=lambda: get_theme("default"))
    plugin_manager: PluginManager = field(default_factory=lambda: PluginManager(
        registry=PluginRegistry(),
        config_manager=ConfigManager(),
    ))


# ---------------------------------------------------------------------------
# Key bindings
# ---------------------------------------------------------------------------

def _build_key_bindings() -> KeyBindings:
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
    cfg = state.config_manager.config
    state.theme = get_theme(cfg.theme)

    for name, value in cfg.aliases.items():
        try:
            state.alias_manager.set(name, value)
        except ValueError:
            print_warning(f"Skipping invalid alias from config: {name}")

    for name, value in cfg.environment.items():
        try:
            state.environment.set(name, value)
        except ValueError:
            print_warning(f"Skipping invalid variable from config: {name}")


def _run_startup_commands(
    state: ShellState,
    preprocessor: Preprocessor,
) -> None:
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
    config_manager = ConfigManager()
    config_manager.load()

    errors = config_manager.validate()
    for error in errors:
        print_warning(error)

    # Build plugin infrastructure
    registry = PluginRegistry()
    plugin_manager = PluginManager(
        registry=registry,
        config_manager=config_manager,
    )

    # Build shell state
    state = ShellState(
        config_manager=config_manager,
        plugin_manager=plugin_manager,
    )

    # Restore persistent state
    _initialise_from_config(state)

    preprocessor = Preprocessor(
        alias_manager=state.alias_manager,
        environment=state.environment,
    )

    # Discover and load plugins
    plugin_manager.discover_and_load_all()

    # Execute startup commands
    _run_startup_commands(state, preprocessor)

    completer = RshxCompleter(cwd_provider=lambda: state.cwd)

    session = PromptSession(
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
                    show_cwd=config_manager.config.show_cwd,
                    show_git_branch=config_manager.config.show_git_branch,
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

    # Shutdown plugins cleanly
    plugin_manager.shutdown_all()
