RSHX --- Raghav Shell eXtended
A lightweight, extensible, cross-platform command-line shell written in
Python.
RSHX is a long-term engineering project focused on understanding how
modern command-line shells work by building one from first principles.
Rather than reproducing existing shells feature-for-feature, RSHX
evolves through structured engineering sprints with a strong emphasis on
clean architecture, modularity, automated testing, and extensibility.
---
Vision
RSHX is designed around four engineering principles:
⚙️ Built from First Principles
🧩 Modular by Design
🧪 Engineering Driven
🚀 Extensible for the Future
Every sprint introduces one major architectural capability while
preserving backward compatibility and maintaining clean separation of
concerns.
The long-term vision is to evolve RSHX into a modern developer shell
supporting plugins, scripting, workflow automation, personalization, and
AI-assisted development.
---
Current Architecture
``` text
                           User
                            │
                            ▼
                   Prompt Toolkit UI
                            │
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
 Command History     Auto Completion      Prompt Renderer
                            │
                            ▼
               Configuration Manager
        ┌────────────┬──────────────┬─────────────┐
        ▼            ▼              ▼             ▼
    Theme      Prompt Config    Alias Store   Environment Store
                            │
                            ▼
                 Startup Command Loader
                            │
                            ▼
                 Command Preprocessor
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
    Alias Resolver                   Variable Resolver
                            │
                            ▼
                       Tokenizer
                            ▼
                     Command Parser
                            ▼
                 Abstract Syntax Tree
                            ▼
                  Command Executor
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
    Built-in Engine   Pipeline Engine   Process Manager
                            │
                     Redirect Manager
                            ▼
                    Operating System
```
---
Features
Core Shell
Interactive REPL powered by `prompt_toolkit`
Dynamic shell prompt
Built-in command execution
External command execution
Persistent working directory
Cross-platform command execution
Productivity
Persistent command history
History navigation
Auto suggestions
Built-in completion
Filesystem completion
Windows path completion
Contextual help
Improved error reporting
Command Composition
AST-driven parsing
Multi-stage pipelines
Input redirection
Output redirection
Output append
Structured execution planning
Shell Environment
Session and persistent aliases
Alias expansion
Session and persistent environment variables
Variable expansion
Command preprocessing
Alias support inside pipelines
Variable expansion inside pipelines
Built-in and external command integration
Configuration & Personalization
TOML configuration
Automatic configuration loading
Automatic persistence
Theme system
Prompt customization
Git branch prompt support
Startup commands
Configuration validation
Recovery from corrupted configuration
Default configuration generation
Engineering
Configuration Manager
Theme Manager
Prompt Configuration Manager
Alias Manager
Environment Manager
AST execution engine
Pipeline engine
Redirect abstraction
Process abstraction
Cross-platform parser
Comprehensive automated regression tests
---
Quick Start
Prerequisites
Python 3.13+
Git
Installation
``` powershell
git clone https://github.com/raghavendrashivam474/rshx.git

Set-Location rshx

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt

python main.py
```
---
Built-in Commands
Command            Description
---
`help`             Display help information
`help <command>`   Display command-specific help
`pwd`              Print current directory
`cd`               Change directory
`clear`            Clear terminal
`exit`             Exit RSHX
`alias`            Create or list aliases
`unalias`          Remove aliases
`set`              Create environment variables
`unset`            Remove environment variables
`env`              Display environment variables
`theme`            View or change theme
`startup`          Manage startup commands
`config`           Display configuration information
---
Project Structure
``` text
rshx/
├── main.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
├── .gitattributes
├── rshx/
│   ├── commands/
│   ├── core/
│   │   ├── alias_manager.py
│   │   ├── ast.py
│   │   ├── completer.py
│   │   ├── config.py
│   │   ├── environment.py
│   │   ├── executor.py
│   │   ├── history.py
│   │   ├── parser.py
│   │   ├── pipeline.py
│   │   ├── preprocessor.py
│   │   ├── process.py
│   │   ├── prompt.py
│   │   ├── prompt_config.py
│   │   ├── redirect.py
│   │   ├── repl.py
│   │   └── theme.py
│   └── utils/
└── tests/
```
---
Running Tests
``` powershell
pytest --cov=rshx --cov-report=term-missing -v
```
---
Test Coverage
Metric                                     Value
---
Tests                            355 Passing
Overall Coverage                         93%
Business Logic       100% Reachable Coverage
Remaining uncovered lines belong primarily to the interactive REPL loop
and terminal integration paths that require interactive testing rather
than conventional unit tests.
---
Development Progress
Sprint    Focus                             Status
---
0     Foundation & REPL                 ✅ Complete
1     History, Completion & UX          ✅ Complete
2     AST, Pipelines & Redirection      ✅ Complete
2.1   Platform Compatibility            ✅ Complete
3     Shell Environment                 ✅ Complete
4     Configuration & Personalization   ✅ Complete
5     Plugin Framework                  📋 Planned
6     RSHX Scripting (.rshx)            📋 Planned
7     AI-Assisted Developer Workflows   💡 Vision
---
Development Principles
Build incrementally through structured sprints.
Introduce one architectural capability per sprint.
Prefer clean architecture over rapid feature growth.
Maintain high automated test coverage.
Keep modules loosely coupled.
Separate preprocessing, parsing, execution, and persistence.
Validate through automated and manual testing.
Document architectural decisions.
---
Repository
Property          Value
---
Current Release   v0.5.0
Branch            main
Python            3.13+
Tests             355 Passing
Coverage          93%
License           MIT
---
Future Vision
Planned capabilities include:
Plugin Framework
Shell scripting (`.rshx`)
Workflow automation
AI-assisted developer commands
The architecture established through the first five milestones enables
these features to be implemented as extensions rather than architectural
rewrites.
---
Contributing
Fork the repository.
Create a feature branch.
Follow the established architecture.
Add or update automated tests.
Ensure all tests pass.
Update documentation.
Submit a pull request.
---
License
This project is licensed under the MIT License.
---
Owner
Raghavendra Singh
Engineering Student • Software Developer • Systems Programming
Enthusiast
RSHX is a long-term engineering project dedicated to exploring modern
shell architecture through incremental, engineering-driven development.
GitHub: https://github.com/raghavendrashivam474/rshx