# SPEC — ATF (Acceptance Testing Framework)

# ATF — Acceptance Testing Framework
## Functional Description

---

## What is ATF

ATF is a command-line tool that acts as an automated QA engineer.
It takes a Gherkin feature file describing what a sprint must do,
runs those tests inside an isolated environment, and tells you
pass or fail with a structured report.

It is written in Python, installable from PyPI, and works with
any web project regardless of technology stack.

---

## How it fits in the workflow

A human writes a plain-language project description.
Claude reads it and produces all planning artifacts.
OpenCode reads those artifacts and builds the software.
ATF reads the acceptance criteria and verifies the software works.

```
Human description
    → Claude produces: SPEC, SCOPE, STACK, STATE, prompts per sprint
    → OpenCode reads each prompt and builds the sprint deliverable
    → ATF reads the acceptance tests and verifies the deliverable
        → PASS: move to next sprint
        → FAIL: ATF writes a feedback report → OpenCode fixes → ATF retries
```

ATF does not generate code. ATF does not plan. ATF only verifies.

---

## How tests run

ATF uses the official Microsoft Playwright Docker image to run tests.
The user's project is mounted as a read-write volume inside the container.
The test results, reports, and screenshots land on the host via that mount.

The user never installs a browser. The user never configures Playwright.
Docker handles all of that.

---

## What ATF produces per sprint run

When tests pass:
- Updated status file showing the sprint passed
- HTML report in the reports folder
- JSON report in the reports folder

When tests fail:
- Same reports
- A feedback file in the sprint folder describing exactly what failed,
  which step failed, the error message, and a screenshot path

---

## CLI commands and behavior

### atf init

Creates two files in the current directory:
- `atf.config.json` with all default settings
- `behave.ini` with the test runner configuration pointing to the
  step definitions bundled inside the ATF package

The user must run this once before using any other command.

### atf run --sprint SPRINT_NAME

Runs the acceptance tests for one sprint.
Reads the feature file at `prompts/SPRINT_NAME/acceptance.feature`.
Runs it inside Docker.
Updates the state file and STATE.md with the result.

Options:
- `--feedback`: if tests fail, writes a structured feedback file at
  `prompts/SPRINT_NAME/feedback.md` so OpenCode can read it and fix the code
- `--retry`: re-runs the full sprint from scratch, overwriting the previous result.
  Retries up to the number configured in `atf.config.json` retries field.
  One retry means one additional attempt beyond the initial run.

### atf run --all

Discovers all sprints by scanning the prompts folder alphabetically.
Only directories that contain an acceptance.feature file are considered.
Runs them in order. Stops after the first sprint where any scenario fails.
Does not stop mid-sprint. Completes the current sprint before stopping.
Exits with a non-zero process exit code if any sprint failed.

### atf status

Displays a color-coded table in the terminal with one row per sprint.
Columns: sprint name, status, deliverable description, last run timestamp.
Status colors: green for passed, red for failed, yellow for pending.

### atf status --sprint SPRINT_NAME

Displays detailed information for one sprint:
- Sprint name and status
- Last run timestamp and duration in seconds
- Total scenarios, how many passed, how many failed
- For each failed scenario: the scenario name, the step that failed, the error message
- Paths to the feedback file, HTML report, and JSON report

---

## Configuration file — atf.config.json

Fields and their purpose:

| Field | Type | Default | Purpose |
|---|---|---|---|
| baseURL | string | http://localhost:3000 | Base URL passed to tests as environment variable |
| promptsDir | string | prompts | Directory where sprint folders live |
| reportsDir | string | reports | Directory where reports are written |
| stateFile | string | atf-state.json | Path to the sprint state file |
| headless | boolean | true | Whether browser runs without UI |
| timeout | number | 30000 | Milliseconds before a step times out |
| retries | number | 1 | How many times --retry re-runs a sprint |
| screenshots | string | only-on-failure | When to capture screenshots |
| docker.image | string | mcr.microsoft.com/playwright/python:latest | Docker image for test execution |
| docker.pull_policy | string | if-not-present | When to pull the image: always, if-not-present, never |

---

## State file — atf-state.json

Tracks the outcome of every sprint run.
Updated automatically after every `atf run` command.

Per sprint, the state file stores:
- status: pending, passed, or failed
- last_run: ISO timestamp of the last run
- duration_seconds: how long the run took
- scenarios.total: total number of scenarios
- scenarios.passed: how many passed
- scenarios.failed: how many failed
- failures: list of objects, each with scenario name, step that failed, error message

---

## STATE.md

The STATE.md is the memory of the project. It is updated after every sprint run
and serves as context for the next agent session — whether that is Claude, OpenCode,
or a human picking up the project later.

It is not just a status table. It is a living document that accumulates knowledge.

### STATE.md structure

```
# PROJECT STATE — [Project Name]
_Last updated: Sprint NN — YYYY-MM-DD_

## Confirmed stack
One line per technology in use.

## Current status
- Active sprint: SNN
- Last checkpoint passed: SNN [Sprint title]
- Status: IN PROGRESS | RELEASE READY | BLOCKED
- Blockers: none | description of blocker

## Completed modules
Checklist of all sprints with [x] for completed and [ ] for pending.
One line per sprint with sprint ID and title.

## Technical decisions
Bullet list of architectural and implementation decisions made so far.
Each decision explains what was decided and why.
Written so that a new agent can understand the project without reading all the code.

## Key files generated
Grouped by module or sprint.
Each entry is a file path followed by a one-line description of what it contains.

## Implemented endpoints
Grouped by module.
Each entry is the HTTP method, path, and one-line description.

## Resolved problems
Grouped by sprint session.
Each entry describes the problem encountered, the decision taken, and the outcome.
Written so that future agents do not repeat the same mistakes.

## Inter-agent notes
Free-form notes left by the current agent for the next agent.
What to do next, what to watch out for, what was left unfinished.
```

### STATE.md example (based on real project)

```markdown
# PROJECT STATE — Multi-tenancy Core App
_Last updated: S8-Agent — 2026-04-02_

## Confirmed stack
- Django 5.x + DRF + Unfold
- VueJS 3 + TailwindCSS
- FastAPI (hexagonal architecture)
- PostgreSQL + Redis + MongoDB
- Celery + Django Channels
- Docker Compose (HA-ready)

## Current status
- Active sprint: S8 COMPLETED
- Last checkpoint passed: S8 Final integration
- Status: RELEASE READY
- Blockers: none

## Completed modules
- [x] S0 Foundation
- [x] S1 Core Models
- [x] S2 Auth
- [x] S3 Tenant Management
- [x] S4 API Tokens
- [x] S5 FastAPI
- [x] S6 Frontend
- [x] S7 Celery + Docker
- [x] S8 Final integration

## Technical decisions
- django-split-settings for modular settings (base/dev/prod)
- threading.local for tenant context (not django-tenant library)
- Monorepo with docker-compose
- Tenant and UserTenantRole as separate models (not inheritance)
- CustomUser with email as USERNAME_FIELD
- TenantAwareManager with get_queryset() filtering by tenant_id
- TenantMiddleware extracts tenant from JWT or X-Tenant-ID header
- Emails sent via Celery tasks (CELERY_TASK_ALWAYS_EAGER in dev)
- is_superadmin() uses request.user.is_superuser directly (not thread-local)
  so it works both in real requests and in tests
- Soft delete: is_active=False instead of deleting records
- MongoDB 4.4 instead of 7+ because test environment CPU lacks AVX support

## Key files generated

### Auth
- backend/apps/users/views.py — Auth views (register, login, verify, reset)
- backend/apps/users/serializers.py — DRF serializers
- backend/apps/users/tasks.py — Celery email tasks
- backend/config/celery.py — Celery configuration

### Tenants (S3)
- backend/apps/tenants/permissions.py — IsTenantOwner, IsTenantAdmin, IsTenantMember
- backend/apps/tenants/views.py — TenantViewSet, TenantMemberViewSet
- backend/tests/tenants/test_tenants.py — 28 tests passing

### API Tokens (S4)
- backend/apps/api_tokens/models.py — APIToken with generate/revoke methods
- backend/tests/api_tokens/test_tokens.py — 11 tests passing

## Implemented endpoints

### Auth
- POST /api/auth/register/ — User registration
- POST /api/auth/login/ — JWT login, returns tenant list
- GET /api/auth/verify-email/?token=xxx — Email verification
- POST /api/auth/forgot-password/ — Request password reset
- POST /api/auth/reset-password/ — Reset with token

### Tenants
- GET /api/tenants/ — List user tenants (UserScope filtered)
- POST /api/tenants/ — Create tenant (caller becomes Owner)
- PATCH /api/tenants/{id}/ — Update (Owner only)
- DELETE /api/tenants/{id}/ — Soft delete (Owner only)
- POST /api/tenants/{id}/members/ — Add member (Admin+)
- PATCH /api/tenants/{id}/members/{user_id}/role/ — Change role (Owner only)

## Resolved problems

### S2 Docker setup
- Problem: django-stubs conflicted with mypy
  Decision: Remove stubs from dev.txt, keep mypy for linting
- Problem: MongoDB 7+ requires AVX CPU support
  Decision: Use mongo:4.4 image instead
- Problem: Django could not connect to PostgreSQL
  Decision: Set POSTGRES_HOST=postgres (service name, not localhost)

## Inter-agent notes
- Project is RELEASE READY, all sprints completed
- Next step if continuing: add rate limiting tests for FastAPI layer
- Superuser credentials: admin@example.com / admin123 (dev only)
- All services run on: Django :8000, FastAPI :8001, Vue :3000
```

### Rules for STATE.md updates

ATF updates STATE.md after every sprint run with:
- The sprint status (passed or failed)
- The last run timestamp
- Any failures encountered

ATF does NOT write the technical decisions, key files, or inter-agent notes sections.
Those are written by OpenCode at the end of each sprint execution.
ATF only owns the status, timestamp, and blockers sections.

This separation means STATE.md is jointly maintained:
- OpenCode writes what was built and decided
- ATF writes whether it passed verification
- Together they form a complete picture of the project state

---

## Sprint folder structure

Each sprint lives in its own folder inside the prompts directory:

```
prompts/
└── sprint_01/
    ├── prompt.md            ← OpenCode reads this to build the sprint
    ├── acceptance.feature   ← ATF reads this to verify the sprint
    ├── feedback.md          ← ATF writes this on failure (only with --feedback)
    └── fixtures/            ← optional data needed before tests run
        ├── setup.sh         ← runs on the host before Docker starts
        ├── seed.json        ← passed into Docker as an environment variable
        └── seed.sql         ← path passed into Docker as an environment variable
```

---

## prompt.md — format and content per sprint

Each prompt.md follows this structure:

```
# Sprint NN — Title

## Context
What exists at this point in the project. What the previous sprint built.

## Task
The specific thing OpenCode must build in this sprint.
Written as a clear instruction, not a checklist.

## Files to create or modify
List of file paths, one per line.

## Must not touch
Files that OpenCode must leave unchanged.

## Done when
Checklist of verifiable outcomes. The last item is always:
- atf run --sprint sprint_NN passes all scenarios
```

### prompt.md content for each sprint

**sprint_01 — Project scaffolding**

Context: Empty project directory. Nothing exists yet.

Task: Create the full project structure for the ATF framework.
Set up pyproject.toml so the `atf` binary is installable via pip.
Implement the `atf init`, `atf --help`, and `atf status` commands
so they run without errors and produce the correct output.

Files to create: pyproject.toml, atf/__init__.py, atf/cli.py,
atf/config.py, atf/state.py, README.md, CHANGELOG.md.

Must not touch: prompts/, reports/, atf-state.json if it exists.

Done when:
- pip install -e . succeeds
- atf --help shows all commands
- atf init creates atf.config.json and behave.ini
- atf status reads atf-state.json and displays a table
- atf run --sprint sprint_01 passes all scenarios

---

**sprint_02 — Docker runner**

Context: The CLI scaffolding exists. atf init and atf status work.
There is no test execution yet.

Task: Implement the Docker runner so that `atf run --sprint` launches
the Microsoft Playwright Docker image with the project mounted,
runs behave against the sprint feature file, captures output,
and updates atf-state.json and STATE.md with the result.

Files to create or modify: atf/runner.py, atf/fixtures.py, atf/cli.py.

Must not touch: atf/environment.py, atf/steps/, prompts/.

Done when:
- atf run --sprint sprint_02 pulls the Docker image if not present
- atf run --sprint sprint_02 executes the feature file inside Docker
- test output is visible in the terminal
- atf-state.json is updated after the run
- atf run --sprint sprint_02 passes all scenarios

---

**sprint_03 — Screenplay actors and step definitions**

Context: The Docker runner works. Tests execute but fail because
there are no step definitions and no browser setup.

Task: Implement environment.py with Behave hooks that create a WebUser
actor with browser ability and an ApiClient actor with HTTP ability.
Implement all step definitions listed in the step vocabulary so that
navigation, form interaction, and API call steps work correctly.

Files to create or modify: atf/environment.py, atf/steps/__init__.py,
atf/steps/navigation_steps.py, atf/steps/form_steps.py,
atf/steps/assertion_steps.py, atf/steps/api_steps.py.

Must not touch: atf/runner.py, atf/cli.py, prompts/.

Done when:
- A WebUser actor can navigate, fill forms, click buttons, and assert text
- An ApiClient actor can call GET and POST and assert response status and body
- atf run --sprint sprint_03 passes all scenarios against the public test sites

---

**sprint_04 — Feedback and state tracking**

Context: Tests run and pass. But when they fail there is no structured
feedback, and atf status shows incomplete information.

Task: Implement feedback.py so that on failure it reads the JSON report,
extracts failed scenarios and steps, and writes a structured feedback.md
in the sprint folder. Update state.py to store the full schema including
duration, scenario counts, and failures. Make atf status --sprint show
the detailed view.

Files to create or modify: atf/feedback.py, atf/state.py, atf/cli.py,
atf/runner.py.

Must not touch: atf/environment.py, atf/steps/, prompts/.

Done when:
- atf run --sprint sprint_04 --feedback writes feedback.md when a test fails
- atf-state.json contains duration, scenario counts, and failures after each run
- atf status --sprint sprint_04 shows the detailed view with all fields
- atf run --sprint sprint_04 passes all scenarios

---

**sprint_05 — Reports and PyPI publishing**

Context: The full pipeline works locally. Reports are generated as JSON
but not as HTML. The package is not yet publishable to PyPI.

Task: Configure the Docker command to also produce an HTML report using
behave-html-formatter. Implement atf run --all with alphabetical sprint
discovery and stop-on-first-failure behavior. Configure pyproject.toml
and GitHub Actions for PyPI publishing via Trusted Publisher.

Files to create or modify: atf/runner.py, atf/cli.py, pyproject.toml,
.github/workflows/publish.yml.

Must not touch: atf/environment.py, atf/steps/, atf/feedback.py.

Done when:
- reports/sprint_05/index.html is generated after each run
- atf run --all discovers and runs all sprints in alphabetical order
- atf run --all stops after the first sprint with any failure
- pyproject.toml is ready for PyPI publish with hatchling build backend
- .github/workflows/publish.yml publishes on git tag push using OIDC
- atf run --sprint sprint_05 passes all scenarios

---

## acceptance.feature — all 5 sprints, complete Gherkin

### sprint_01

```gherkin
Feature: [Sprint 01] ATF CLI scaffolding

  Scenario: Binary shows help
    Given the state file exists
    Then sprint "sprint_01" should have status "pending"

  Scenario: Public web target is reachable
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"
```

### sprint_02

```gherkin
Feature: [Sprint 02] Docker runner

  Scenario: WebUser can navigate inside Docker
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"

  Scenario: ApiClient can call a public API
    Given I am an ApiClient
    When I call GET "https://jsonplaceholder.typicode.com/users/1"
    Then the response status should be 200
    And the response should contain "Leanne Graham"
```

### sprint_03

```gherkin
Feature: [Sprint 03] Screenplay actors and steps

  Scenario: WebUser fills and submits a form
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com/login"
    And I fill in "username" with "tomsmith"
    And I fill in "password" with "SuperSecretPassword!"
    And I click the "Login" button
    Then I should see "You logged into a secure area!"

  Scenario: WebUser sees element on page
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com/checkboxes"
    Then the element "input[type='checkbox']" should be visible

  Scenario: ApiClient reads a field
    Given I am an ApiClient
    When I call GET "https://jsonplaceholder.typicode.com/posts/1"
    Then the response status should be 200
    And the response field "userId" should equal "1"
```

### sprint_04

```gherkin
Feature: [Sprint 04] Feedback and state tracking

  Scenario: State file tracks sprint
    Given the state file exists
    Then sprint "sprint_04" should have status "pending"

  Scenario: WebUser confirms app works
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"

  Scenario: ApiClient confirms API works
    Given I am an ApiClient
    When I call GET "https://jsonplaceholder.typicode.com/todos/1"
    Then the response status should be 200
    And the response should contain "delectus aut autem"
```

### sprint_05

```gherkin
Feature: [Sprint 05] Reports and full pipeline

  Scenario: WebUser sees a table
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com/tables"
    Then I should see "Data Tables"
    And the element "table" should be visible

  Scenario: HTML report exists after run
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"
    And a report file should exist at "reports/sprint_05/index.html"

  Scenario: ApiClient posts data
    Given I am an ApiClient
    When I call POST "https://jsonplaceholder.typicode.com/posts" with body:
      """
      {"title": "atf test", "body": "automated", "userId": 1}
      """
    Then the response status should be 201
    And the response should contain "atf test"
```

---

## Step vocabulary — every supported Gherkin step

```
Given I am a WebUser
Given I am an ApiClient
Given the state file exists

When I navigate to "{url}"
When I fill in "{field}" with "{value}"
When I click the "{text}" button
When I click "{selector}"
When I select "{value}" from "{field}"
When I wait for "{selector}"
When I wait {seconds} seconds
When I call GET "{url}"
When I call POST "{url}" with body:
When I call DELETE "{url}"
When I set header "{name}" to "{value}"

Then I should see "{text}"
Then I should not see "{text}"
Then the element "{selector}" should be visible
Then the element "{selector}" should not be visible
Then the field "{field}" should have value "{value}"
Then there should be {count} "{selector}" elements
Then the response status should be {code}
Then the response should contain "{text}"
Then the response field "{field}" should equal "{value}"
Then sprint "{sprint}" should have status "{status}"
Then a report file should exist at "{path}"
```

---

## Fixture handling — behavior by file type

setup.sh — runs on the host machine before Docker starts.
Used for starting test databases, running migrations, seeding via external CLI tools.
Must be executable (chmod +x).

seed.json — its contents are passed into Docker as an environment variable
named ATF_SEED_JSON. Step definitions or environment.py can read it if needed.

seed.sql — its file path is passed into Docker as an environment variable
named ATF_SEED_SQL pointing to the mounted path inside the container.
Step definitions or environment.py can execute it against a database if needed.

---

## feedback.md — format written on failure

```
# ATF Feedback: SPRINT_NAME — FAILED

## Timestamp
ISO datetime of the failure

## Failed Scenario
Name of the first failed scenario

## Step that failed
The exact step text that failed

## Error
The error message from the test runner

## Screenshot
Path to the screenshot file relative to project root

## All failures
Numbered list of all failed scenarios with their step and error
```

---

## CHANGELOG.md format

Follows Keep a Changelog format (https://keepachangelog.com).
Initial entry is version 0.1.0 with Added section listing the initial features.

---

## README.md required sections

- Project name and one-line description
- PyPI install badge and install command
- Quick start: init, run a sprint, check status
- Full CLI reference
- atf.config.json field reference
- Sprint folder convention
- Step vocabulary reference
- How to publish a new version

---

## Acceptance criteria — final checklist

- pip install atf-framework installs the atf binary globally
- pip install -e . works for local development
- atf --help shows all commands
- atf init creates atf.config.json and behave.ini with correct defaults
- atf run --sprint runs the feature file inside Docker
- atf run --sprint --feedback writes feedback.md on failure only
- atf run --sprint --retry re-runs up to the configured retries count
- atf run --all scans prompts folder alphabetically and stops after first failed sprint
- atf run --all exits with non-zero code if any sprint failed
- atf status shows color-coded table of all sprints
- atf status --sprint shows detailed view with failures and file paths
- atf-state.json stores full schema after every run
- STATE.md updated after every run
- HTML and JSON reports written to reports/sprint_NN/ after every run
- setup.sh runs on host before Docker if present
- seed.json passed as ATF_SEED_JSON env var if present
- seed.sql path passed as ATF_SEED_SQL env var if present
- Docker image pulled if not present according to pull_policy
- Zero Playwright or browser installation required on host
- All steps in the vocabulary are implemented
- Python code passes ruff linting and mypy type checking
- pyproject.toml uses hatchling and declares the atf entry point
- GitHub Actions publishes to PyPI on git tag using OIDC Trusted Publisher
