# Sprint 01 — Project Scaffolding & CLI

## Sprint Goal
The `atf` binary is installable via pip and exposes working `init`, `run`, and `status` commands.

## Definition of Ready
- [ ] This is sprint_01 — no prior sprint required
- [ ] acceptance.feature uses only steps from the ATF vocabulary
- [ ] Public internet is reachable (https://the-internet.herokuapp.com)

## Context
This is the first sprint. Nothing exists yet. The goal is to produce a working Python
package named `atf-framework` that installs globally via `pip install -e .` and exposes
an `atf` binary with three sub-commands: `init`, `run`, and `status`. The `init` command
must write `atf.config.json` and `behave.ini` to the current working directory. The
`run` and `status` commands may print "not yet implemented" stubs — they will be built
in subsequent sprints. The package must also ship a pre-baked `atf-state.json` schema
and a `STATE.md` template that `init` copies to the project root.

## Task
Create the complete `atf/` Python package with `pyproject.toml`, `behave.ini`, and all
source files listed below. Implement `atf init` fully. Stub `atf run` and `atf status`.
Write `tests/test_cli.py` with the three representative test cases (Docker mocked).
Ensure `ruff` and `mypy` pass with zero errors.

## Files to create or modify
- `pyproject.toml`
- `behave.ini`
- `README.md`
- `CHANGELOG.md`
- `atf/__init__.py`
- `atf/cli.py`
- `atf/config.py`
- `atf/state.py`
- `atf/runner.py`          (stub — must not crash on import)
- `atf/feedback.py`        (stub — must not crash on import)
- `atf/fixtures.py`        (stub — must not crash on import)
- `atf/environment.py`
- `atf/steps/__init__.py`
- `atf/steps/navigation_steps.py`   (empty steps file, valid Python)
- `atf/steps/form_steps.py`         (empty steps file, valid Python)
- `atf/steps/assertion_steps.py`    (empty steps file, valid Python)
- `atf/steps/api_steps.py`          (empty steps file, valid Python)
- `tests/__init__.py`
- `tests/test_cli.py`
- `.github/workflows/publish.yml`

## Do not touch
- `prompts/`
- `SPEC.md`, `SCOPE.md`, `STACK.md`, `STATE.md`, `atf-state.json`

## Done when
- [ ] `pip install -e .` completes without errors → verified manually
- [ ] `atf --help` outputs text containing `run`, `status`, and `init` → verified manually
- [ ] `atf init` creates `atf.config.json` with all fields from the spec → verified manually
- [ ] `atf init` creates `behave.ini` at the project root → verified manually
- [ ] `atf init` exits non-zero if `atf.config.json` already exists → verified manually
- [ ] `pytest tests/` passes (Docker mocked) → verified manually
- [ ] `ruff check atf/` exits 0 → verified manually
- [ ] `mypy atf/` exits 0 → verified manually
- [ ] State file is initialized → Scenario: "State file is initialized by the framework"
- [ ] Public web target is reachable inside Docker → Scenario: "Public web target is reachable inside Docker"
- [ ] atf run --sprint sprint_01 --feedback passes all scenarios

## Definition of Done
The sprint closes when ATF runs and records status: passed in atf-state.json.
Command: atf run --sprint sprint_01 --feedback
If it fails, read prompts/sprint_01/feedback.md before retrying.

Note: CLI verification items (pip install, atf --help, atf init, pytest, ruff, mypy)
require human validation — they cannot be verified by ATF's Gherkin runner.
