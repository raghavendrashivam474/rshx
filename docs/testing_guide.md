# RSHX Testing Guide

## Running Tests

    .\.venv\Scripts\Activate.ps1
    pytest --cov=rshx --cov-report=term-missing -v

## Test Structure

All test files live in the tests/ directory.
Each module has a corresponding test_module.py file.

## Coverage Baseline

Current coverage: 94% total
Business logic modules: 100%
Deferred: repl.py live REPL loop (requires terminal simulation)

## Writing Tests

Follow the existing patterns:
- One test class per logical grouping
- Use pytest fixtures for shared state
- Use tmp_path for file operations
- Use patch/MagicMock for isolation

## Test Naming Convention

    class TestModuleName:
        def test_what_it_does_when_condition(self):
            ...
