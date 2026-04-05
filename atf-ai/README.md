# ATF — Acceptance Testing Framework

[![PyPI version](https://img.shields.io/pypi/v/atf-framework.svg)](https://pypi.org/project/atf-framework/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-driven QA engineer CLI that executes Gherkin acceptance tests inside an official Microsoft Playwright Docker container.

## Installation

```bash
pip install atf-framework
```

For development:

```bash
git clone https://github.com/your-org/atf-framework.git
cd atf-framework
pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize a new project
atf init

# Run acceptance tests for a specific sprint
atf run --sprint sprint_01

# Run all sprints in order
atf run --all

# Check sprint status
atf status
atf status --sprint sprint_01
```

## Commands

| Command | Description |
|---------|-------------|
| `atf init` | Creates `atf.config.json`, `behave.ini`, `atf-state.json`, and `STATE.md` in the current directory |
| `atf run --sprint <name>` | Runs acceptance tests for a sprint inside Docker |
| `atf run --all` | Runs all sprints in alphabetical order, stops on first failure |
| `atf run --feedback` | Writes `prompts/<sprint>/feedback.md` when scenarios fail |
| `atf run --retry` | Re-runs a sprint even if it already passed |
| `atf status` | Shows a table of all sprints with status and scenario counts |
| `atf status --sprint <name>` | Shows detailed view for a single sprint |

## Configuration Reference

`atf init` generates `atf.config.json` with the following fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `baseURL` | string | `http://localhost:3000` | Base URL for web tests |
| `promptsDir` | string | `prompts` | Directory containing feature files |
| `reportsDir` | string | `reports` | Directory for test reports |
| `stateFile` | string | `atf-state.json` | Path to the state tracking file |
| `headless` | boolean | `true` | Run browser in headless mode |
| `timeout` | integer | `30000` | Default timeout in milliseconds |
| `retries` | integer | `1` | Number of retry attempts |
| `screenshots` | string | `only-on-failure` | Screenshot policy |
| `docker.image` | string | `mcr.microsoft.com/playwright/python:latest` | Docker image for test execution |
| `docker.pull_policy` | string | `if-not-present` | When to pull the Docker image (`always`, `if-not-present`, `never`) |

## Sprint Convention

- Feature files live in `prompts/sprint_NN/acceptance.feature`
- Each sprint is a directory named `sprint_01`, `sprint_02`, etc.
- `atf run --all` discovers and runs sprints in alphabetical order
- State is tracked in `atf-state.json` with status: `pending`, `passed`, or `failed`

## Project Structure

```
atf/
├── __init__.py
├── cli.py              # CLI entry point (click)
├── config.py           # Configuration management
├── state.py            # State tracking
├── runner.py           # Docker test runner
├── feedback.py         # Feedback generation
├── fixtures.py         # Test fixtures
├── environment.py      # Behave environment hooks
├── interactions/       # Custom abilities (Screenplay)
│   └── call_an_api.py
└── steps/              # Step definitions
    ├── navigation_steps.py
    ├── form_steps.py
    ├── assertion_steps.py
    └── api_steps.py

prompts/
├── sprint_01/
│   └── acceptance.feature
├── sprint_02/
│   └── acceptance.feature
├── ...
└── steps -> ../atf/steps  # Symlink to step definitions
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/

# Lint
ruff check atf/

# Type check
mypy atf/

# Build for PyPI
pip install hatch
hatch build
```

## Building for PyPI

```bash
hatch build
ls dist/
# atf_framework-0.1.0-py3-none-any.whl
# atf_framework-0.1.0.tar.gz
```

Install from wheel:

```bash
pip install dist/atf_framework-0.1.0-py3-none-any.whl
atf --help
```

## License

MIT
