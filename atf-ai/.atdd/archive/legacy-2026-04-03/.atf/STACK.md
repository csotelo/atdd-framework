# ATF — Stack

## Runtime

| Component | Version | Rationale |
|-----------|---------|-----------|
| **Python** | 3.11+ | Native `tomllib`, modern `match` statement, `Self` type, `ExceptionGroup`; ships in the Playwright Docker image |
| **typer** | 0.12+ | Type-safe CLI with auto `--help` generation from type annotations; no boilerplate argument parsing |
| **rich** | 13+ | Colored terminal output, tables, and progress indicators with zero extra dependencies |
| **docker (SDK)** | 7+ | Python SDK for Docker Engine API; programmatic container lifecycle without shelling out |
| **httpx** | 0.27+ | Modern HTTP client with sync + async support; used by the `ApiClient` actor; replaces `requests` |

## Test execution (runs inside Docker)

| Component | Version | Rationale |
|-----------|---------|-----------|
| **behave** | 1.2.6+ | Gherkin BDD for Python; stable API, Docker-friendly (no daemon required), integrates with `behave.ini` |
| **screenpy** | 4.2+ | Screenplay pattern for Python; enforces Actor/Ability/Interaction separation in step definitions |
| **screenpy-playwright** | 0.1+ | `BrowseTheWeb` ability for screenpy actors backed by Playwright's sync API |
| **behave-html-formatter** | 1.0+ | HTML test reports without Allure; single-file output, works inside Docker with no extra config |

## Build & tooling

| Component | Version | Rationale |
|-----------|---------|-----------|
| **hatchling** | latest | Modern PEP 517 build backend; no `setup.py`; used with `hatch build` for PyPI publishing |
| **ruff** | 0.4+ | Fast Python linter + formatter (replaces flake8 + isort + pyupgrade); single tool, zero config drift |
| **mypy** | 1.10+ | Static type checker; strict mode; catches type errors before Docker execution |
| **pytest** | 8.0+ | Unit test runner for `tests/`; Docker mocked with `unittest.mock.patch` |

## Infrastructure

| Component | Rationale |
|-----------|-----------|
| **mcr.microsoft.com/playwright/python:latest** | Official Microsoft image; pre-installs Chromium, Firefox, and WebKit plus all system dependencies; eliminates all browser setup on the host |
| **GitHub Actions** | CI/CD; trusted publisher flow for PyPI means no API tokens stored in secrets |
| **PyPI (Trusted Publisher)** | OIDC-based publish via `pypa/gh-action-pypi-publish`; triggered on `v*` tags |

## Dependency graph

```
atf (host CLI)
├── typer          — CLI parsing
├── rich           — terminal output
├── docker         — container lifecycle
└── httpx          — used by ApiClient actor on host

Docker container (mcr.microsoft.com/playwright/python:latest)
├── Python 3.11 (pre-installed)
├── Playwright + Chromium (pre-installed)
├── behave         — Gherkin runner
├── screenpy       — Screenplay pattern
├── screenpy-playwright  — BrowseTheWeb ability
└── behave-html-formatter — HTML reports
    (all installed via pip in the image or via volume-mounted requirements)
```

## Decision log

- **httpx over requests**: async-capable for future enhancements; cleaner API; already
  used by modern Python tooling (FastAPI test client, etc.)
- **behave over pytest-bdd**: Docker-friendly `behave.ini` configuration; `--format json`
  output is stable and well-documented; no pytest plugin chain inside Docker
- **behave-html-formatter over Allure**: Allure requires a separate server or CLI tool;
  `behave-html-formatter` produces a self-contained HTML file with no extra setup
- **hatchling over setuptools**: no `setup.py` / `setup.cfg` split; single `pyproject.toml`
  is the canonical source of truth; `hatch build` works identically locally and in CI
- **Docker SDK over subprocess**: typed return values, proper error handling via
  `docker.errors.ContainerError`; no shell injection risk; pull_policy is explicit
