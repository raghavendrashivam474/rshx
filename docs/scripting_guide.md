# RSHX Scripting Guide

## Overview

.rshx files contain sequences of RSHX commands that execute
through the existing shell pipeline.

## Running a Script

Scripts are resolved relative to the current working directory.
Always use the full path or a variable.

    run rshx\scripts\hello.rshx
    run rshx\scripts\greet.rshx Raghav

Recommended pattern using a variable:

    set SCRIPTS=C:\Projects\rshx\rshx\scripts
    run %SCRIPTS%\hello.rshx
    run %SCRIPTS%\greet.rshx Raghav

Add the variable as a startup command so it is always available:

    startup add set SCRIPTS=C:\Projects\rshx\rshx\scripts

## Script Format

    # This is a comment

    @name My Script
    @description What this script does
    @continue_on_error false

    pwd
    git status
    pytest

## Directives

| Directive | Values | Default | Description |
|-----------|--------|---------|-------------|
| @name | any string | filename | Script display name |
| @description | any string | empty | Script description |
| @continue_on_error | true / false | false | Continue after failures |

## Positional Arguments

    run greet.rshx Raghav

In the script:

    echo Hello %1

Arguments are available as %1 %2 %3 etc.
Missing arguments expand to empty string.

## Variable Expansion

    set MYDIR=C:\Projects
    run navigate.rshx

In the script:

    cd %MYDIR%
    pwd

## Alias Expansion

Aliases defined in the session are available in scripts.

    alias gs=git status
    run check.rshx

In check.rshx:

    gs

## Failure Behaviour

Default stops on first failure:

    @continue_on_error false

    pytest
    git push

If pytest fails, git push does not run.

Continue on error:

    @continue_on_error true

    pytest
    git status

Both commands run regardless of pytest result.

## Interactive Shell Behaviour

RSHX reads one command per prompt line. When using the
interactive shell, enter each command separately and wait
for the prompt before entering the next.

Do not paste multiple commands at once as the second line
will be treated as an argument to the first command.

## Execution Summary

After each script run RSHX prints:

    Script: My Script
    Commands executed : 3
    Succeeded         : 3
    Failed            : 0
    Duration          : 1.23s
    Result: SUCCESS
