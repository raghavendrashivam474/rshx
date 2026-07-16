"""
repl.py
-------
The Read-Evaluate-Print Loop - the heart of RSHX.

Interrupt handling
------------------
Ctrl+C at the prompt clears the current input and prints a short
message so the user knows the shell is still alive and responsive.

Ctrl+D triggers a clean shutdown equivalent to typing 'exit'.
Plugins are shut down and a goodbye message is displayed.

Prompt recovery
---------------
After any interruption the prompt is always redrawn cleanly.
The shell never requires restarting after a Ctrl+C or Ctrl+D.
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
from rshx.core.plugin_registry import PluginRegistry
from rshx.core.plugin_manager import PluginManager
from rshx.core.input_dispatcher import InputDispatcher
from rshx.core.command_queue import CommandQueue
from rshx.utils.display import (
    print_error,
    print_warning,
    print_banner,
    print_info,
    initialise_display,
)


@dataclass
class ShellState:
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
    dispatcher: InputDispatcher,
) -> None:
    for raw in state.config_manager.config.startup_commands:
        _execute_raw(raw, state, preprocessor, dispatcher)


def _execute_raw(
    raw: str,
    state: ShellState,
    preprocessor: Preprocessor,
    dispatcher: InputDispatcher,
) -> None:
    result = dispatcher.dispatch(raw)
    if result.is_empty():
        return

    queue = CommandQueue(preprocessor=preprocessor, shell_state=state)
    queue.run(result.commands)


def _handle_interrupt() -> None:
    """
    Respond to Ctrl+C at the prompt.

    Prints a short message so the user knows the shell received
    the signal and is ready for new input. The prompt redraws
    automatically after this function returns.
    """
    print("\n  (interrupted — press Ctrl+D to exit)")


def _handle_eof(state: ShellState) -> None:
    """
    Respond to Ctrl+D at the prompt.

    Sets running to False so the main loop exits cleanly.
    Plugin shutdown and goodbye message are handled by the
    caller after the loop terminates.
    """
    print("")
    state.running = False


def run_shell() -> None:
    initialise_display()
    print_banner()

    config_manager = ConfigManager()
    config_manager.load()

    errors = config_manager.validate()
    for error in errors:
        print_warning(error)

    registry = PluginRegistry()
    plugin_manager = PluginManager(registry=registry, config_manager=config_manager)
    state = ShellState(config_manager=config_manager, plugin_manager=plugin_manager)
    _initialise_from_config(state)

    preprocessor = Preprocessor(state.alias_manager, state.environment)
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
            raw_input = session.prompt(
                build_prompt(
                    cwd=state.cwd,
                    theme=state.theme,
                    show_cwd=config_manager.config.show_cwd,
                    show_git_branch=config_manager.config.show_git_branch,
                )
            )
            _execute_raw(raw_input, state, preprocessor, dispatcher)
            completer.update_cwd(state.cwd)

        except KeyboardInterrupt:
            _handle_interrupt()
            continue

        except EOFError:
            _handle_eof(state)

    print_info("Goodbye!")
    plugin_manager.shutdown_all()