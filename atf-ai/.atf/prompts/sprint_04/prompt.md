# Sprint 04 — Feedback & State Tracking

## Sprint Goal
When a sprint fails, ATF writes a structured `feedback.md` that an AI agent can
consume to fix the implementation. `atf status` displays the sprint table correctly.

## Definition of Ready
- [ ] sprint_03 has status: passed in atf-state.json
- [ ] STATE.md reflects sprint_03 as completed
- [ ] acceptance.feature uses only steps from the ATF vocabulary
- [ ] Docker daemon is running on the host
- [ ] Public internet is reachable (the-internet.herokuapp.com, jsonplaceholder.typicode.com)

## Context
Sprint 03 delivered the full step library and all Screenplay actors. `atf run --sprint sprint_03`
passes. The runner writes `reports/sprint_NN/results.json` and `reports/sprint_NN/index.html`.
`atf-state.json` is updated after each run. `feedback.py` is still a stub.

## Task
Implement `atf/feedback.py` fully: read `reports/sprint_NN/results.json`, extract
all failed steps, write `prompts/sprint_NN/feedback.md` following the schema in SPEC.md.
Wire the `--feedback` flag in `cli.py` so `feedback.write_feedback()` is called only
when the flag is set and the run failed.
Also implement population of the `failures` list in `atf-state.json`
(currently left empty after each run).
Implement `atf status` and `atf status --sprint` in `cli.py` with the exact output
format specified in SPEC.md.

## Files to create or modify
- `atf/feedback.py`
- `atf/cli.py`
- `atf/state.py`

## Do not touch
- `atf/runner.py`
- `atf/environment.py`
- `atf/steps/`
- `atf/fixtures.py`
- `prompts/`
- `SPEC.md`, `SCOPE.md`, `STACK.md`, `STATE.md`, `atf-state.json`

## Done when
- [ ] Previously passed sprint is recorded in state file → Scenario: "Previously passed sprint is recorded in state file"
- [ ] WebUser can navigate to confirm Docker runner works → Scenario: "WebUser navigates to confirm app is working"
- [ ] ApiClient can call external API → Scenario: "ApiClient confirms external API works"
- [ ] `feedback.md` written on failure with correct schema → verified manually (trigger with --feedback on a broken sprint)
- [ ] `atf-state.json` `failures` array populated after failed run → verified manually
- [ ] `atf status` prints table with all sprints → verified manually
- [ ] `atf status --sprint sprint_04` prints detailed view → verified manually
- [ ] `ruff check atf/` exits 0 → verified manually
- [ ] `mypy atf/` exits 0 → verified manually
- [ ] atf run --sprint sprint_04 --feedback passes all scenarios

## Definition of Done
The sprint closes when ATF runs and records status: passed in atf-state.json.
Command: atf run --sprint sprint_04 --feedback
If it fails, read prompts/sprint_04/feedback.md before retrying.
