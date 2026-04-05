# Sprint 02 — Docker Runner

## Sprint Goal
`atf run --sprint sprint_02` launches a Docker container, executes Gherkin tests,
and writes JSON + HTML reports to `reports/sprint_02/`.

## Definition of Ready
- [ ] sprint_01 has status: passed in atf-state.json
- [ ] STATE.md reflects sprint_01 as completed
- [ ] acceptance.feature uses only steps from the ATF vocabulary
- [ ] Docker daemon is running on the host
- [ ] Public internet is reachable (the-internet.herokuapp.com, jsonplaceholder.typicode.com)

## Context
Sprint 01 delivered a working `atf init` command, the package structure, and CLI stubs.
`atf.config.json` and `behave.ini` exist. The step files and `environment.py` are in
place but the steps are empty. `atf run` is a stub that does nothing.

## Task
Implement `atf/runner.py` fully: pull the Docker image per `pull_policy`, mount the
project directory into the container at `/app`, run `python -m behave` with JSON and
HTML output flags, update `atf-state.json` and `STATE.md` after the run.
Wire `atf run --sprint` in `cli.py` to call `runner.run_sprint()`.
Implement the two basic step definitions needed by this sprint's feature:
- `Given I am a WebUser` / `Given I am an ApiClient` (actor setup)
- `When I navigate to "{url}"`
- `Then I should see "{text}"`
- `When I call GET "{url}"`
- `Then the response status should be {code:d}`
- `Then the response should contain "{text}"`

Also implement `atf/fixtures.py` fully (build_fixture_env, run_fixtures_if_present).

## Files to create or modify
- `atf/runner.py`
- `atf/cli.py`
- `atf/state.py`
- `atf/fixtures.py`
- `atf/steps/navigation_steps.py`
- `atf/steps/assertion_steps.py`
- `atf/steps/api_steps.py`

## Do not touch
- `atf/environment.py`
- `prompts/`
- `SPEC.md`, `SCOPE.md`, `STACK.md`, `STATE.md`, `atf-state.json`

## Done when
- [ ] WebUser navigates inside Docker → Scenario: "WebUser can navigate inside Docker"
- [ ] ApiClient calls public API and asserts response → Scenario: "ApiClient can call a public API"
- [ ] `reports/sprint_02/results.json` is written after the run → verified manually
- [ ] `reports/sprint_02/index.html` is written after the run → verified manually
- [ ] `atf-state.json` is updated with status, last_run, duration_seconds, and scenario counts → verified manually
- [ ] `STATE.md` reflects the updated sprint status → verified manually
- [ ] atf run --sprint sprint_02 --feedback passes all scenarios

## Definition of Done
The sprint closes when ATF runs and records status: passed in atf-state.json.
Command: atf run --sprint sprint_02 --feedback
If it fails, read prompts/sprint_02/feedback.md before retrying.
