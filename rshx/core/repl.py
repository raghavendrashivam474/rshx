"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Release Sprint 2 changes
------------------------
- All user input now passes through the InputDispatcher before
  execution. The REPL no longer communicates directly with the
  preprocessor. Instead it iterates over the command list returned
  by the dispatcher.
- Multi-command paste support: pasting multiple lines executes
  each line as a separate command in order.
- Improved Ctrl+C and Ctrl+D handling.
- Empty input is handled cleanly without warnings.
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
from rshx.core.input_dispatcher import InputDispatcher
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
    plugin_manager : PluginManager
        Plugin lifecycle manager.
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
    """Restore aliases, variables, and theme from configuration."""
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
    dispatcher: InputDispatcher,
) -> None:
    """Execute startup commands defined in configuration."""
    for raw in state.config_manager.config.startup_commands:
        _execute_raw(raw, state, preprocessor, dispatcher)


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------

def _execute_raw(
    raw: str,
    state: ShellState,
    preprocessor: Preprocessor,
    dispatcher: InputDispatcher,
) -> None:
    """
    Dispatch a raw input string through the full execution pipeline.

    Used for both interactive input and startup commands.

    Parameters
    ----------
    raw : str
        Raw command string from the prompt or startup config.
    state : ShellState
        Current shell state.
    preprocessor : Preprocessor
        Active preprocessor with alias and variable access.
    dispatcher : InputDispatcher
        Active input dispatcher for classification.
    """
    result = dispatcher.dispatch(raw)

    if result.is_empty():
        return

    for command in result.commands:
        if not state.running:
            break

        try:
            expanded, warnings = preprocessor.process(command)
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


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_shell() -> None:
    """Start and run the RSHX interactive shell."""
    initialise_display()
    print_banner()

    config_manager = ConfigManager()
    config_manager.load()

    errors = config_manager.validate()
    for error in errors:
        print_warning(error)

    registry = PluginRegistry()
    plugin_manager = PluginManager(
        registry=registry,
        config_manager=config_manager,
    )

    state = ShellState(
        config_manager=config_manager,
        plugin_manager=plugin_manager,
    )

    _initialise_from_config(state)

    preprocessor = Preprocessor(
        alias_manager=state.alias_manager,
        environment=state.environment,
    )

    dispatcher = InputDispatcher()

    plugin_manager.discover_and_load_all()

    _run_startup_commands(state, preprocessor, dispatcher)

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
            # Ctrl+C - cancel current line, return to clean prompt
            print()
            continue

        except EOFError:
            # Ctrl+D - clean exit
            print()
            break

        _execute_raw(raw_input, state, preprocessor, dispatcher)
        completer.update_cwd(state.cwd)

    plugin_manager.shutdown_all()
