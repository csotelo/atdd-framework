# ATDD Orchestrator

> **Spec-Driven, Autonomous Acceptance-Test Development — queue-controlled, Scrum-oriented**

---

## Why this exists

This project started as personal curiosity.

As a technical Product Owner, I spend a lot of time thinking about how to define scope clearly, how to make acceptance criteria unambiguous, and how to ensure that what gets built is exactly what was agreed — not an approximation.

When AI coding agents started becoming real tools (not just demos), I asked myself a simple question:

> *Can I give an AI agent the same responsibilities I'd give a role in a Scrum team — and hold it to the same standards?*

Not "can an AI write code?" — that bar is already cleared. The real question is whether you can build a system where:

- A **spec is the source of truth**, not a ticket in Jira
- Each **role has clear, independent criteria** for what "done" means
- The pipeline moves **autonomously**, triggered by events, not by someone checking Slack
- **Acceptance tests are the final judge** — not the developer, not the PO, not a linter

That curiosity led to this framework.

---

## The core idea

Traditional ATDD says: write acceptance tests first, then build until they pass.

This framework takes that idea further and asks: *what if the entire development pipeline — from test writing to acceptance — ran autonomously, with each stage owned by a dedicated agent, coordinated by a queue?*

The result is a pipeline where:

1. A human (the technical PO) collaborates with Claude to **define the spec and acceptance criteria**
2. From that point on, **specialized agents take over**, each with a single responsibility
3. Every transition between stages is **triggered by an event** (a status change in the story)
4. The pipeline **only advances when criteria are met** — an agent cannot skip a stage or self-certify
5. The whole thing runs under a **Scrum mental model**: sprints, backlog, user stories, definition of done

No human approval needed between test-writing and acceptance. The spec is the contract. The Gherkin scenario is the verdict.

---

## Pipeline

```
[Human + Claude]
    │
    ▼  architect creates stories, refines spec, marks sprint as ready
    │
    │  story.md → status: ready
    │
[Celery + Redis — fully autonomous from here]
    │
    ├── test_engineer   →  status: tests-written
    │   Writes unit + integration tests in RED (failing, no implementation yet)
    │
    ├── developer       →  status: built
    │   Makes the RED tests pass (GREEN). Does not touch test files.
    │
    ├── tester          →  status: tested
    │   Verifies regressions, runs ruff + mypy, checks nothing else broke
    │
    └── atf_worker      →  status: accepted
        Runs acceptance.feature with Playwright + Behave
        This is the only verdict that matters.
```

Each agent runs via [OpenCode](https://opencode.ai) (`opencode run "prompt"`), independently, with no shared state beyond the story file. The orchestrator polls every 30 seconds and dispatches the next task when a story's status advances.

---

## Roles and responsibilities

This maps directly to Scrum — but executed by agents, not people.

| Role | Who | Responsibility | Criterion to advance |
|---|---|---|---|
| `architect` | Human + Claude | Spec, scope, stack, sprint planning, story refinement | Story has `story.md` + `prompt.md` + `acceptance.feature` |
| `test_engineer` | OpenCode (autonomous) | Write failing tests before any implementation | Tests exist and are RED |
| `developer` | OpenCode (autonomous) | Write implementation until tests pass | Tests are GREEN, no regressions |
| `tester` | OpenCode (autonomous) | Quality gate: ruff, mypy, regression check | All checks pass |
| `atf_worker` | OpenCode (autonomous) | Run Gherkin acceptance scenarios | All scenarios pass |

The `architect` role is **always collaborative**. Strategic decisions — what to build, why, what the acceptance criteria are — stay with the human. Claude is a thinking partner here, not an executor.

Everything downstream is **fully automated**.

---

## Story lifecycle

```
draft → ready → tests-written → in-progress → built → tested → accepted
                                                              ↑
                                              This is the only real "done"
```

Special statuses for recovery and migration:

| Status | Meaning |
|---|---|
| `blocked` | Any agent flagged a blocker — needs human review |
| `unverified` | Legacy code with no tests — functions but unverified |
| `damaged` | Tests exist but fail — known regression |
| `unknown` | No tests, no way to verify — needs architect attention |

---

## Project structure

```
atdd/
├── atdd_orchestrator/
│   ├── config.py
│   ├── dispatcher.py              # entry point — polls every 30s
│   ├── domain/
│   │   ├── story.py               # Story entity + Status value object
│   │   └── ports.py               # interfaces: StoryRepository, CodeRunner, TaskQueue
│   ├── application/
│   │   └── use_cases/             # dispatch, run_test_engineer, run_developer, …
│   └── infrastructure/
│       ├── frontmatter_repo.py    # reads/writes story.md via YAML frontmatter
│       ├── opencode_runner.py     # CodeRunner → subprocess opencode
│       └── celery/
│           ├── app.py             # Celery instance
│           ├── queue_adapter.py   # TaskQueue implementation
│           └── tasks.py           # thin wrappers → use cases
├── skills/                        # Claude Code skills (architect, developer, …)
├── atf-ai/                        # real project running on this framework
├── tests/                         # 35 tests, 0 failures, no external dependencies
├── docker-compose.yml             # Redis only
├── pyproject.toml
├── install.sh                     # syncs skills + installs dependencies
└── projects.yml.example           # multi-project configuration example
```

### Architecture: hexagonal (ports & adapters)

The orchestrator follows strict hexagonal architecture:

```
domain          — no external dependencies, pure Python
application     — imports domain only
infrastructure  — imports domain + application + external libs (Celery, Redis, frontmatter)
```

Use cases are fully testable without Redis or OpenCode — ports are injected as stubs in `tests/stubs.py`.

---

## Story file format

Each user story lives in `.atdd/backlog/US0N-name/`:

```
US01-feature-name/
├── story.md            # frontmatter: id, title, status, sprint
├── prompt.md           # instructions for the developer agent
├── acceptance.feature  # Gherkin scenarios — the acceptance contract
└── tests-red.txt       # pytest output at RED stage (for traceability)
```

`story.md` frontmatter example:

```yaml
---
id: US01
title: User can log in with email and password
status: ready
sprint: sprint_01
---
```

The `status` field is the event that drives the queue.

---

## Getting started

### Requirements

- Python 3.11+
- Docker (for Redis)
- [OpenCode](https://opencode.ai) installed and authenticated

### Install

```bash
bash install.sh
```

Syncs Claude Code skills to `~/.claude/skills/` and installs Python dependencies in `.venv/`.

### Run

```bash
# 1. Start Redis
docker compose up -d

# 2. Start the Celery worker
.venv/bin/celery -A atdd_orchestrator.infrastructure.celery.app worker --loglevel=info

# 3. Start the dispatcher pointing to your project
.venv/bin/python -m atdd_orchestrator.dispatcher /path/to/your/project
```

### Initialize a project

Use the `atdd_architect` skill inside Claude Code:

```
/atdd_architect
```

This will guide you through creating `SPEC.md`, `SCOPE.md`, `STACK.md`, and your first sprint with user stories.

---

## Running tests

```bash
.venv/bin/pytest tests/ -v
```

35 tests, 0 failures. No Redis, no OpenCode, no network — all ports stubbed.

---

## Migration from legacy projects

If you have an existing project using the old `.atf/` format, the `atdd_architect` skill includes a migration mode that:

1. Reads `atf-state.json` and maps what ran and what didn't
2. Archives the legacy structure under `.atdd/archive/legacy-YYYY-MM-DD/`
3. Creates proper `backlog/US0N-name/` entries for each legacy sprint
4. Assigns statuses: `passed → accepted`, `failed → damaged`, `not run → unverified`
5. Generates a `MIGRATION.md` with the full audit trail

---

## Design decisions

**Why Celery + Redis and not a simple loop?**
Each agent runs independently. A queue decouples the orchestrator from execution — if a developer task takes 10 minutes, the dispatcher isn't blocked. It also gives us retries, visibility, and a natural place to add priorities later.

**Why OpenCode for autonomous roles?**
Claude credits are expensive and strategic. OpenCode handles the technical execution (writing tests, implementing code, running checks) at a lower cost. Claude is reserved for the `architect` role — the work that actually requires judgment.

**Why is the architect always human+Claude and never fully automated?**
Scope decisions and acceptance criteria are where projects go wrong. Automating that judgment away is how you end up building the wrong thing perfectly. The spec is the contract — it needs a human to own it.

**Why frontmatter in story.md as the event source?**
It keeps the state in the repository, not in a database. Any agent, any tool, any human can read and update it with a text editor. The orchestrator doesn't own the state — the project does.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
