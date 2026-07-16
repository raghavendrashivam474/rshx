# Contributing to RSHX

Thank you for your interest in contributing to RSHX.

## Getting Started

\\\powershell
git clone https://github.com/raghavendrashivam474/rshx.git
Set-Location rshx
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
\\\

## Running Tests

\\\powershell
pytest --cov=rshx --cov-report=term-missing -v
\\\

All tests must pass before submitting a pull request.
Coverage should not decrease below the current baseline.

## Code Standards

- Python 3.12+ required
- Type hints on all public functions
- Docstrings on all public modules and classes
- Tests for all new business logic
- No hardcoded version strings — use rshx.__version__

## Pull Request Process

1. Fork the repository
2. Create a feature branch from main
3. Write tests for your changes
4. Ensure all tests pass
5. Update relevant documentation
6. Submit a pull request with a clear description

## Adding a Built-in Command

1. Add the function to rshx/commands/builtins.py
2. Add a help entry to HELP_DATA
3. Register in BUILTIN_REGISTRY
4. Write tests in tests/test_builtins.py

## Writing a Plugin

See docs/plugin_guide.md for the complete plugin development guide.

## Writing a Script

See docs/scripting_guide.md for the .rshx scripting guide.

## Commit Message Format

Prefix commits with the type of change:

- feat:     new feature
- fix:      bug fix
- refactor: code improvement without behaviour change
- test:     test additions or improvements
- docs:     documentation changes
- build:    packaging or dependency changes
- chore:    maintenance tasks
