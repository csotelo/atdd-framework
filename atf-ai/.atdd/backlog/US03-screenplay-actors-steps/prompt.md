# Sprint 03 — Screenplay Actors & Full Step Library

## Sprint Goal
The full ATF step vocabulary is implemented: form interactions, element assertions,
API mutations, and header control — all exercised against public test sites.

## Definition of Ready
- [ ] sprint_02 has status: passed in atf-state.json
- [ ] STATE.md reflects sprint_02 as completed
- [ ] acceptance.feature uses only steps from the ATF vocabulary
- [ ] Docker daemon is running on the host
- [ ] Public internet is reachable (the-internet.herokuapp.com, jsonplaceholder.typicode.com)

## Context
Sprint 02 delivered a working Docker runner and basic navigation/assertion steps.
`atf run --sprint sprint_02` passes. `environment.py` already wires `WebUser` and
`ApiClient` actors. The step library covers navigation, basic text assertions, and
GET requests.

## Task
Implement the remaining step definitions to cover the full vocabulary in SPEC.md.
Steps must use the Screenplay pattern via `context.web_user` and `context.api_client`
actors — no direct `context.page` calls inside step definitions.

Steps to add:
- `When I fill in "{field}" with "{value}"`  — fill input by label or name
- `When I click the "{text}" button`         — click button by visible text
- `When I click "{selector}"`                — click by CSS selector
- `When I select "{value}" from "{field}"`   — select option from dropdown
- `When I wait for "{selector}"`             — wait until selector is visible
- `When I wait {seconds:d} seconds`          — sleep N seconds
- `When I call POST "{url}" with body:`      — POST with multiline JSON body
- `When I call DELETE "{url}"`               — DELETE request
- `When I set header "{name}" to "{value}"`  — set request header on ApiClient
- `Then I should not see "{text}"`           — assert text absent
- `Then the element "{selector}" should be visible`
- `Then the element "{selector}" should not be visible`
- `Then the field "{field}" should have value "{value}"`
- `Then there should be {count:d} "{selector}" elements`
- `Then the response field "{field}" should equal "{value}"`

If `screenpy.abilities.MakeAPIRequests` does not exist in the installed version of
screenpy, implement `atf/interactions/call_an_api.py` as a custom ability wrapping
`httpx.Client` and update `atf/environment.py` accordingly.

## Files to create or modify
- `atf/steps/navigation_steps.py`
- `atf/steps/form_steps.py`
- `atf/steps/assertion_steps.py`
- `atf/steps/api_steps.py`
- `atf/interactions/call_an_api.py`   (only if MakeAPIRequests is unavailable)
- `atf/environment.py`                (only if custom ability is needed)

## Do not touch
- `atf/runner.py`
- `atf/cli.py`
- `atf/config.py`
- `atf/state.py`
- `atf/fixtures.py`
- `prompts/`
- `SPEC.md`, `SCOPE.md`, `STACK.md`, `STATE.md`, `atf-state.json`

## Done when
- [ ] Login form filled and submitted successfully → Scenario: "WebUser fills and submits a form"
- [ ] Element visibility assertion works → Scenario: "WebUser sees elements on a page"
- [ ] API field assertion works → Scenario: "ApiClient reads a specific field"
- [ ] `ruff check atf/` exits 0 → verified manually
- [ ] `mypy atf/` exits 0 → verified manually
- [ ] atf run --sprint sprint_03 --feedback passes all scenarios

## Definition of Done
The sprint closes when ATF runs and records status: passed in atf-state.json.
Command: atf run --sprint sprint_03 --feedback
If it fails, read prompts/sprint_03/feedback.md before retrying.
