# RSHX Scripting Guide

## Overview

.rshx files contain sequences of RSHX commands that execute
through the existing shell pipeline.

## Running a Script

    run myscript.rshx
    run myscript.rshx arg1 arg2

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

## Failure Behaviour

Default stops on first failure. Use @continue_on_error true to continue.

## Execution Summary

After each script run RSHX prints:

    Script: My Script
    Commands executed : 3
    Succeeded         : 3
    Failed            : 0
    Duration          : 1.23s
    Result: SUCCESS
