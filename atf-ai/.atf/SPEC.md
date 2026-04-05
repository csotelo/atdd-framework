# ATF — Acceptance Testing Framework
## Specification

### Project Name
`atf-framework` (PyPI) · `atf` (CLI binary)

### Purpose
ATF is an AI-driven QA engineer CLI that executes Gherkin acceptance tests inside
an official Microsoft Playwright Docker container. It eliminates browser installation
on the host, provides structured feedback for AI code-generation loops, and tracks
sprint-level test state across an iterative development workflow.

### One-paragraph description
ATF wraps `behave` + Playwright inside Docker so any developer or AI agent can run
browser and API acceptance tests without configuring a local browser environment.
Given a `prompts/sprint_NN/acceptance.feature` file, `atf run --sprint sprint_NN`
pulls the Playwright image if needed, mounts the project directory, runs all
scenarios, writes JSON + HTML reports, updates `atf-state.json` and `STATE.md`,
and — on failure — writes a structured `feedback.md` that an AI code-generation
tool (e.g. OpenCode) can consume to fix the implementation.

---

## CLI Command Reference

### `atf init`
Creates `atf.config.json` and `behave.ini` in the current working directory.
Exits with an error if `atf.config.json` already exists.

```
atf init
```

### `atf run`
Executes acceptance tests for one or all sprints.

```
atf run --sprint <sprint_id>            Run a single sprint
atf run --sprint <sprint_id> --feedback Write feedback.md on failure
atf run --sprint <sprint_id> --retry    Re-run and overwrite previous results
atf run --all                           Run all sprints alphabetically; stop on first failure
atf run --all --feedback                Same, with feedback on failure
```

Flags:
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--sprint` | str | — | Sprint directory name (e.g. `sprint_01`) |
| `--feedback` | bool | false | Write `feedback.md` when any scenario fails |
| `--retry` | bool | false | Re-run sprint even if status is `passed` |
| `--all` | bool | false | Discover and run all sprints in order |

### `atf status`
Displays sprint status from `atf-state.json`.

```
atf status                    Table of all sprints
atf status --sprint <id>      Detailed view for one sprint
```

Output format for `--sprint`:
```
Sprint:        sprint_02
Status:        failed
Last run:      2026-03-31T14:23:00Z
Duration:      12.4s
Scenarios:     3 total — 2 passed, 1 failed

Failed scenarios:
  ✗ User fills and submits a form
    Step:   Then I should see "You logged into a secure area!"
    Error:  Element not found within 30000ms

Files:
  Feedback:  prompts/sprint_02/feedback.md
  Report:    reports/sprint_02/index.html
  Results:   reports/sprint_02/results.json
```

---

## Screenplay Pattern Rules

ATF uses the [Screenplay pattern](https://serenity-js.org/handbook/design/screenplay-pattern/)
via `screenpy` and `screenpy-playwright`. All test logic is expressed through Actors,
Abilities, and Interactions — never direct Playwright calls in step definitions.

### Python examples

```python
# Actor with browser ability
from screenpy import Actor
from screenpy_playwright import BrowseTheWeb

web_user = Actor.named("WebUser").who_can(BrowseTheWeb.using(page))

# Actor with HTTP ability (custom ability wrapping httpx)
from atf.interactions.call_an_api import CallAnApi
import httpx

api_client = Actor.named("ApiClient").who_can(
    CallAnApi.using(httpx.Client(timeout=30.0))
)
```

### Rules
1. Step definitions access actors via `context.web_user` and `context.api_client`.
2. Direct `context.page` calls are allowed only in `environment.py` hooks.
3. Each step maps to exactly one Interaction or Question.
4. No assertions inside `when` steps; assertions belong in `then` steps.

---

## Sprint Breakdown

| Sprint | Deliverable | Acceptance Criteria |
|--------|-------------|---------------------|
| sprint_01 | CLI scaffolding + `atf init` | `atf --help` shows commands; `atf init` creates `atf.config.json`; state file exists; public URL reachable |
| sprint_02 | Docker runner + basic actors | WebUser navigates inside Docker; ApiClient calls public API; JSON + HTML reports written |
| sprint_03 | Screenplay steps (forms, assertions, API) | WebUser fills/submits login form; element visibility assertions; API field assertions |
| sprint_04 | Feedback + state tracking | State file updated post-run; `feedback.md` written on failure; `atf status` shows correct data |
| sprint_05 | Reports + full pipeline + PyPI | Table interactions; report file assertion; POST API; `ruff`/`mypy` pass; package builds |

---

## `atf.config.json` Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `baseURL` | string | `"http://localhost:3000"` | Base URL for the application under test |
| `promptsDir` | string | `"prompts"` | Directory containing sprint subdirectories |
| `reportsDir` | string | `"reports"` | Output directory for HTML/JSON reports |
| `stateFile` | string | `"atf-state.json"` | Path to the sprint state file |
| `headless` | boolean | `true` | Run browser in headless mode |
| `timeout` | integer | `30000` | Default action timeout in milliseconds |
| `retries` | integer | `1` | Number of retries on scenario failure |
| `screenshots` | string | `"only-on-failure"` | When to capture screenshots: `"always"`, `"never"`, `"only-on-failure"` |
| `docker.image` | string | `"mcr.microsoft.com/playwright/python:latest"` | Docker image to use |
| `docker.pull_policy` | string | `"if-not-present"` | Image pull policy: `"always"`, `"if-not-present"`, `"never"` |

---

## `atf-state.json` Full Schema

```json
{
  "project": "<project name string>",
  "current_sprint": "sprint_01",
  "sprints": {
    "sprint_01": {
      "status": "pending | passed | failed",
      "last_run": "ISO-8601 datetime or null",
      "duration_seconds": "float or null",
      "scenarios": {
        "total": 0,
        "passed": 0,
        "failed": 0
      },
      "failures": [
        {
          "scenario": "Scenario name string",
          "step": "Keyword + step text",
          "error": "Error message string"
        }
      ]
    }
  }
}
```

Fields:
| Field | Type | Description |
|-------|------|-------------|
| `project` | string | Project name, set by `atf init` |
| `current_sprint` | string | Sprint currently targeted for development |
| `sprints.<id>.status` | enum | `pending`, `passed`, `failed` |
| `sprints.<id>.last_run` | string\|null | ISO-8601 UTC timestamp of last run |
| `sprints.<id>.duration_seconds` | float\|null | Wall-clock seconds for last run |
| `sprints.<id>.scenarios.total` | int | Total scenario count |
| `sprints.<id>.scenarios.passed` | int | Passed scenario count |
| `sprints.<id>.scenarios.failed` | int | Failed scenario count |
| `sprints.<id>.failures` | array | List of failure objects (empty if all passed) |
| `failures[].scenario` | string | Scenario name |
| `failures[].step` | string | Full step text including keyword |
| `failures[].error` | string | Error/exception message |

---

## `feedback.md` Schema

```markdown
# ATF Feedback: sprint_NN — FAILED

## Timestamp
<ISO-8601 UTC datetime>

## Failed Scenario
Scenario: <scenario name>

## Step that failed
<keyword + step text>

## Error
<full error message>

## Screenshot
<absolute path to PNG file>

## All failures (<N> total)

1. [<scenario name>] <step text>
2. [<scenario name>] <step text>
```

Notes:
- Written by `feedback.py` running on the host, not inside Docker.
- Written only when `--feedback` flag is passed to `atf run`.
- Screenshot path points to `reports/sprint_NN/failed_<safe_scenario_name>.png`.
- Only the first failure gets the full detail block; all failures are listed at the end.

---

## `STATE.md` Schema

```markdown
# ATF — Project State

| Sprint    | Status  | Deliverable               | Last run             |
|-----------|---------|---------------------------|----------------------|
| sprint_01 | pending | Project scaffolding       | —                    |
| sprint_02 | pending | Docker runner             | —                    |
| sprint_03 | pending | Screenplay + steps        | —                    |
| sprint_04 | pending | Feedback + state          | —                    |
| sprint_05 | pending | Reports + PyPI            | —                    |
```

Updated after every `atf run` invocation (pass or fail).

---

## Docker Integration

ATF never installs Playwright or browsers on the host. Instead:

1. `runner.py` calls `docker.from_env()` to get a Docker SDK client.
2. It calls `client.containers.run(...)` with:
   - `image`: the Playwright Python image from config
   - `volumes`: `{os.getcwd(): {"bind": "/app", "mode": "rw"}}` — mounts the entire
     project directory into the container at `/app`
   - `working_dir`: `/app`
   - `command`: `python -m behave prompts/sprint_NN/acceptance.feature ...`
3. Behave inside the container reads `behave.ini` (at `/app/behave.ini`), which
   points `steps_dir` and `environment_file` at `/app/atf/steps/` and
   `/app/atf/environment.py` respectively — no installation required inside Docker.
4. Reports (`results.json`, `index.html`) are written to `/app/reports/sprint_NN/`
   inside the container, which maps to `./reports/sprint_NN/` on the host.
5. Screenshots land at `/app/reports/sprint_NN/failed_<name>.png`.
6. After the container exits, `feedback.py` runs on the host and reads those files.

---

## Step Vocabulary

```gherkin
# Actors
Given I am a WebUser
Given I am an ApiClient

# Navigation
When I navigate to "{url}"

# Forms
When I fill in "{field}" with "{value}"
When I click the "{text}" button
When I click "{selector}"
When I select "{value}" from "{field}"

# Waiting
When I wait for "{selector}"
When I wait {seconds:d} seconds

# API
When I call GET "{url}"
When I call POST "{url}" with body:
  """
  json body
  """
When I call DELETE "{url}"
When I set header "{name}" to "{value}"

# Assertions — UI
Then I should see "{text}"
Then I should not see "{text}"
Then the element "{selector}" should be visible
Then the element "{selector}" should not be visible
Then the field "{field}" should have value "{value}"
Then there should be {count:d} "{selector}" elements

# Assertions — API
Then the response status should be {code:d}
Then the response should contain "{text}"
Then the response field "{field}" should equal "{value}"

# State assertions
Given the state file exists
Then sprint "{sprint}" should have status "{status}"

# Report assertions
Then a report file should exist at "{path}"
```
