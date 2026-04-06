# ATDD Orchestrator

> **Spec-Driven, Autonomous Acceptance-Test Development — queue-controlled, Scrum-oriented**

---

## Why this exists

Building a product solo is brutal.

You are the PO, the architect, the developer, the QA, and the one making sure the lights stay on — all at the same time, with a calendar that never has enough hours. At some point you stop asking "how do I build faster?" and start asking a harder question:

> *What can I actually automate without losing control of what gets built?*

I've been a programmer for years and a Product Owner long enough to know that most failures don't come from bad code — they come from ambiguous requirements, skipped tests, and "it works on my machine." So when AI coding agents started becoming real tools, I didn't see a magic button. I saw a new kind of team member that needed the same thing any team member needs: clear responsibilities, short tasks, and verifiable criteria for done.

The first thing I tried was the obvious approach: long prompts, one agent, do everything. It failed the way it always fails — the AI hallucinated, lost context, and confidently built the wrong thing. Long prompts tend to fail. The model drifts. The output is plausible but wrong.

Then I applied something I already knew from software architecture:

> **Divide and conquer.**

If a long prompt fails, what about a very short one with a very specific context? What if instead of one agent doing everything, you had multiple agents — each with a single role, a precise skill, and just enough context to do their job and nothing else?

That's where my background as a PO and architect converged with the agent world.

I already knew how to write well-structured user stories. I already thought in roles and responsibilities. I already used acceptance criteria as the definition of done. The missing piece was a system to coordinate it all — to take a story that's ready and move it through a pipeline of specialized agents, each doing one thing, each passing a quality gate before the next one starts.

So I built it:

- **Claude** as the architect colleague — the AI that's exceptional at understanding context, structuring problems, and generating precise, short prompts for each downstream agent. Claude doesn't execute. Claude thinks.
- **OpenCode** for the autonomous roles — test engineer, developer, tester. Short prompts, clear scope, no ambiguity. Fast, focused, cheap.
- **Celery + Redis** as the coordination layer — a queue that manages role transitions, ensures order, and decouples each stage from the next.
- **Gherkin acceptance scenarios** as the only real verdict — not the developer saying "it's done," not a linter passing, but the actual feature working end-to-end with Playwright.

The result is a system where I write the spec and the acceptance criteria with Claude, mark the story as ready, and walk away. The pipeline runs. Tests get written in RED. Code gets written until they're GREEN. Regressions get checked. Acceptance scenarios run. If everything passes, the story is `accepted`. If something breaks, it's `blocked` and waits for me.

I tested this on a real project — [atf-ai](atf-ai/), a CLI tool with a full test suite. Five user stories, end-to-end, from spec to acceptance. It worked.

This is that system, released.

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
[Celery + Redis  ·or·  LangGraph — fully autonomous from here]
    │
    ├── test_engineer   →  status: tests-written
    │   Writes unit + integration tests in RED (failing, no implementation yet)
    │
    ├── developer       →  status: built
    │   Makes the RED tests pass (GREEN). Does not touch test files.
    │
    ├── tester          →  status: tested
    │   Verifies regressions, runs ruff + mypy, checks nothing else broke
    │   ↑ retries developer (up to 3×) if quality gate fails
    │
    └── atf_worker      →  status: accepted
        Runs acceptance.feature with Playwright + Behave
        This is the only verdict that matters.
        ↑ retries developer (up to 3×) if acceptance fails
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
│   ├── dispatcher.py              # entry point Celery — polls every 30s
│   ├── domain/
│   │   ├── story.py               # Story entity + Status value object
│   │   └── ports.py               # interfaces: StoryRepository, CodeRunner, TaskQueue
│   ├── application/
│   │   └── use_cases/             # dispatch, run_test_engineer, run_developer, …
│   └── infrastructure/
│       ├── frontmatter_repo.py    # reads/writes story.md via YAML frontmatter
│       ├── opencode_runner.py     # CodeRunner → subprocess opencode
│       ├── celery/
│       │   ├── app.py             # Celery instance
│       │   ├── queue_adapter.py   # TaskQueue implementation
│       │   └── tasks.py           # thin wrappers → use cases
│       └── langgraph/
│           ├── state.py           # PipelineState TypedDict
│           ├── nodes.py           # nodes that call use cases (NoOpQueue)
│           └── graph.py           # StateGraph with conditional edges + retry logic
├── dispatcher_langgraph.py        # entry point LangGraph — no Redis required
├── skills/                        # Claude Code skills (architect, developer, …)
├── atf-ai/                        # real project running on this framework
├── tests/                         # 35 tests, 0 failures, no external dependencies
├── docker-compose.yml             # Redis only (Celery mode)
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

Two modes — pick one:

**LangGraph (no Redis required):**
```bash
pip install -e ".[langgraph]"
python dispatcher_langgraph.py /path/to/your/project
```

**Celery + Redis (distributed):**
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

**Why two orchestration modes (Celery and LangGraph)?**
LangGraph makes the state machine explicit as Python code — no Redis, no broker, easier to run locally and inspect. Celery is better for distributed setups where workers run on separate machines. Both share the same domain and use cases; the difference is only in the infrastructure adapter.

**Why OpenCode for autonomous roles?**
Claude credits are expensive and strategic. OpenCode handles the technical execution (writing tests, implementing code, running checks) at a lower cost. Claude is reserved for the `architect` role — the work that actually requires judgment.

**Why is the architect always human+Claude and never fully automated?**
Scope decisions and acceptance criteria are where projects go wrong. Automating that judgment away is how you end up building the wrong thing perfectly. The spec is the contract — it needs a human to own it.

**Why frontmatter in story.md as the event source?**
It keeps the state in the repository, not in a database. Any agent, any tool, any human can read and update it with a text editor. The orchestrator doesn't own the state — the project does.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
