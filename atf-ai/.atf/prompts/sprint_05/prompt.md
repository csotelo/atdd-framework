# Sprint 05 — Reports, Full Pipeline & PyPI

## Sprint Goal
The full ATF pipeline works end-to-end: `atf run --all` runs all sprints in order,
HTML reports are generated, and the package builds cleanly for PyPI distribution.

## Definition of Ready
- [ ] sprint_04 has status: passed in atf-state.json
- [ ] STATE.md reflects sprint_04 as completed
- [ ] acceptance.feature uses only steps from the ATF vocabulary
- [ ] Docker daemon is running on the host
- [ ] Public internet is reachable (the-internet.herokuapp.com, jsonplaceholder.typicode.com)

## Context
All four previous sprints pass. The full step library is implemented. Feedback and state
tracking work. This is the final sprint: polish the implementation, add the remaining
step definitions, ensure the package builds cleanly for PyPI, and verify the full
end-to-end pipeline with `atf run --all`.

## Task
1. Add the `Then a report file should exist at "{path}"` step to `assertion_steps.py`
   (checks that a file exists on the host at the given path relative to `/app`).
2. Add the `Given the state file exists` and `Then sprint "{sprint}" should have status "{status}"`
   steps to `assertion_steps.py` if not already present.
3. Implement `atf run --all` in `cli.py`: use `discover_sprints()` to find sprints
   alphabetically, run each in order, stop after the first sprint with any failure,
   print a summary table at the end.
4. Implement `atf run --retry` flag: re-run the sprint even if its status is `passed`.
5. Ensure `hatch build` produces a valid wheel and sdist (`dist/` directory, no errors).
6. Verify `ruff check atf/` and `mypy atf/` both exit 0.
7. Write a complete `README.md` with: install badge, quick start (`atf init` + `atf run`),
   config reference table, sprint convention section, PyPI badge.
8. Update `CHANGELOG.md` with the 0.1.0 release date.

## Files to create or modify
- `atf/cli.py`
- `atf/steps/assertion_steps.py`
- `README.md`
- `CHANGELOG.md`

## Do not touch
- `atf/runner.py`
- `atf/environment.py`
- `atf/feedback.py`
- `atf/fixtures.py`
- `atf/state.py`
- `atf/steps/navigation_steps.py`
- `atf/steps/form_steps.py`
- `atf/steps/api_steps.py`
- `prompts/`
- `SPEC.md`, `SCOPE.md`, `STACK.md`, `STATE.md`, `atf-state.json`

## Done when
- [ ] WebUser interacts with a table → Scenario: "WebUser can interact with a table"
- [ ] Report file is generated and assertable → Scenario: "Report file is generated after run"
- [ ] ApiClient can POST data and get 201 → Scenario: "ApiClient posts data"
- [ ] `atf run --all` runs sprints 01–05 and prints summary table → verified manually
- [ ] `atf run --sprint sprint_01 --retry` re-runs regardless of status → verified manually
- [ ] `hatch build` exits 0 and produces files in `dist/` → verified manually
- [ ] `pip install dist/atf_framework-0.1.0-py3-none-any.whl` succeeds → verified manually
- [ ] `ruff check atf/` exits 0 → verified manually
- [ ] `mypy atf/` exits 0 → verified manually
- [ ] `README.md` contains install instructions, quick start, config reference → verified manually
- [ ] atf run --sprint sprint_05 --feedback passes all scenarios

## Definition of Done
The sprint closes when ATF runs and records status: passed in atf-state.json.
Command: atf run --sprint sprint_05 --feedback
If it fails, read prompts/sprint_05/feedback.md before retrying.
