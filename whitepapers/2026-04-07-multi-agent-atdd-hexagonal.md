---
title: "Building a Multi-Agent ATDD Pipeline with Hexagonal Architecture"
published: false
description: "How I built a fully autonomous ATDD pipeline where specialized AI agents write tests, implement code, verify quality, and run acceptance scenarios — coordinated by a swappable execution engine behind a clean port."
tags: ai, python, testing, architecture
cover_image:
---

# Building a Multi-Agent ATDD Pipeline with Hexagonal Architecture

> *Write the spec, mark the story as ready, walk away. The agents do the rest.*

---

## The problem with solo AI development

Building a product solo is brutal.

You are the PO, the architect, the developer, and the QA — all at the same time. When AI coding agents entered the picture, I didn't see a magic button. I saw a new kind of team member that needed the same thing any team member needs: **clear responsibilities, short tasks, and a verifiable definition of done**.

The first thing I tried was the obvious approach: long prompts, one agent, do everything. It failed the way it always fails. The model drifted, lost context, and confidently built the wrong thing.

Then I applied something I already knew from software architecture:

> **Divide and conquer.**

If a long prompt fails, what about a very short one with a very specific context? What if instead of one agent doing everything, you had **multiple agents — each with a single role, a precise skill, and just enough context to do their job**?

That question led me to build an ATDD orchestrator: a pipeline of specialized AI agents, coordinated by a state machine, that takes a user story from spec to acceptance without human intervention in the technical stages.

In this article I'll walk through the architecture, the design decisions, and — the main focus — how **hexagonal architecture** made it possible to support two completely different execution engines behind a single port, without touching the domain or the use cases.

---

## What is ATDD and why does it fit AI agents perfectly?

**Acceptance Test Driven Development** says: write acceptance criteria first, then build until they pass. The acceptance criteria — written as Gherkin scenarios — are the only real definition of done.

This maps naturally to a multi-agent pipeline:

1. **Architect** (human + Claude): define the spec, write the acceptance criteria, refine user stories
2. **Test engineer** (autonomous): write unit and integration tests in RED — before any implementation
3. **Developer** (autonomous): make the RED tests pass — and only that
4. **Tester** (autonomous): quality gate — regressions, ruff, mypy
5. **ATF worker** (autonomous): run the Gherkin acceptance scenarios with Playwright + Behave

Each role has a single responsibility. Each transition is triggered by a status change in a file. No agent can skip a stage or self-certify completion.

```
story.md → status: inbox
              │
              ▼
        test_engineer  → tests in RED
              │
              ▼
          developer    → tests GREEN
              │
              ▼
            tester     → quality gate
              │
              ▼
          atf_worker   → acceptance scenarios pass
              │
              ▼
        status: done  ✓
```

The spec is the contract. The Gherkin scenario is the verdict.

---

## The architecture: hexagonal all the way down

The orchestrator follows strict **hexagonal architecture** (ports and adapters):

```
domain          — pure Python, no external dependencies
application     — imports domain only (use cases)
infrastructure  — adapters only: Celery, LangGraph, git, frontmatter, opencode
__main__.py     — entry point, wires everything together
```

The domain defines four ports (interfaces):

```python
class StoryRepository(ABC):
    def get(self, story_id: str) -> Story: ...
    def save_status(self, story_id: str, status: Status, note: str = "") -> None: ...
    def find_by_status(self, status: Status) -> list[str]: ...

class CodeRunner(ABC):
    def run(self, role: str, prompt: str) -> None: ...

class TaskQueue(ABC):
    """Inter-worker queue — used internally by the Celery engine."""
    def enqueue(self, task_name: str, story_id: str) -> None: ...

class PipelineExecutor(ABC):
    """Starts the full pipeline for a story in INBOX.
    Each engine (Celery, LangGraph) provides its own implementation.
    """
    def submit(self, story_id: str) -> None: ...
```

Each use case depends only on these ports. For example, `RunDeveloper`:

```python
class RunDeveloper:
    def __init__(self, story_repo, runner, queue): ...

    def execute(self, story_id: str) -> None:
        try:
            self._runner.run("developer", _PROMPT.format(story_id=story_id))
            self._repo.save_status(story_id, Status.READY_TO_TEST)
            self._queue.enqueue("run_tester", story_id)
        except Exception as exc:
            self._repo.save_status(story_id, Status.BLOCKED, note=str(exc))
            raise
```

Notice: the use case doesn't know *what* `CodeRunner` is (subprocess? API call? mock?), *what* `StoryRepository` stores to (files? database?), or *how* `TaskQueue` delivers the next task (Celery? Redis? LangGraph?).

This is the key. **The infrastructure is replaceable without touching the domain.**

---

## The entry point: `__main__.py`

In hexagonal architecture, the entry point is a **driver** — it wires the application together and starts the loop. It doesn't belong in `infrastructure/`, it belongs at the root of the package.

`python -m atdd_orchestrator` runs `__main__.py`:

```python
def _make_executor(project_path: str) -> PipelineExecutor:
    if PIPELINE_ENGINE == "langgraph":
        from atdd_orchestrator.infrastructure.langgraph.pipeline_executor import (
            LangGraphPipelineExecutor,
        )
        return LangGraphPipelineExecutor(project_path)

    from atdd_orchestrator.infrastructure.celery.pipeline_executor import (
        CeleryPipelineExecutor,
    )
    return CeleryPipelineExecutor(project_path)


def _process_project(project_path: str) -> None:
    git_adapter.configure(project_path)
    git_adapter.pull(project_path)

    repo     = FrontmatterStoryRepository(project_path)
    executor = _make_executor(project_path)
    DispatchStories(repo, executor).execute()

    if git_adapter.has_changes(project_path):
        git_adapter.commit_and_push(project_path)
```

`__main__.py` depends on the `PipelineExecutor` port — it never imports Celery or LangGraph directly. The engine is a deployment detail selected by `PIPELINE_ENGINE` env var.

The git operations (pull, commit, push) live in `infrastructure/git_adapter.py` — a pure adapter with no business logic. The orchestration loop lives in `__main__.py` — where it belongs.

---

## The production engine: Celery + Redis

The production implementation uses Celery with Redis as the broker. Each role has a dedicated queue and runs in its own isolated container.

```python
# infrastructure/celery/pipeline_executor.py
class CeleryPipelineExecutor(PipelineExecutor):
    def submit(self, story_id: str) -> None:
        app.send_task("run_test_engineer",
                      args=[self._project_path, story_id],
                      queue="inbox")

# infrastructure/celery/tasks.py
@app.task(name="run_developer", queue="ready-to-dev")
def task_developer(self, project_path: str, story_id: str) -> None:
    repo, runner, queue, notifier = _deps(project_path)
    RunDeveloper(repo, runner, queue).execute(story_id)
```

```
docker compose up
  ├── redis             ← message broker
  ├── git-sync          ← python -m atdd_orchestrator (polls, dispatches)
  ├── test-engineer     ← celery worker --queues=inbox
  ├── developer         ← celery worker --queues=ready-to-dev
  ├── tester            ← celery worker --queues=ready-to-test
  └── atf-worker        ← celery worker --queues=ready-to-atf
```

Each role runs in its own isolated container. A slow story blocks only one worker. If a container crashes, Redis preserves the message — the worker retries when it comes back. Multiple stories and projects advance in parallel.

This is the right engine for production: resilient, isolated, horizontally scalable.

---

## The local development engine: LangGraph

[LangGraph](https://github.com/langchain-ai/langgraph) is a library for building stateful, graph-based workflows. You define nodes (work units) and edges (transitions), compile the graph, and invoke it with an initial state.

For local development — one project, no Redis, no Docker — LangGraph is the simpler alternative.

### State

```python
class PipelineState(TypedDict):
    story_id: str
    project_path: str
    status: Status
    blocked_reason: Optional[str]
    dev_retries: int  # prevents infinite loops on repeated failures
```

### Nodes

Each node calls the existing use case with a `GraphRoutedQueue` instead of a real queue adapter. **The graph handles routing — the use cases don't need to know what comes next.**

```python
class GraphRoutedQueue(TaskQueue):
    """The use cases call queue.enqueue() as a side effect.
    In LangGraph, that call is intentionally ignored —
    the graph decides the next node by reading the story status.
    """
    def enqueue(self, task_name: str, story_id: str) -> None:
        pass
```

After executing the use case, the node reads the current status from the repository (the use case already persisted it) and returns the updated state:

```python
def developer_node(state: PipelineState) -> PipelineState:
    repo, runner, notifier, queue = _deps(state["project_path"])
    try:
        RunDeveloper(repo, runner, queue).execute(state["story_id"])
    except Exception:
        pass  # use case already saved BLOCKED to the repo

    status, reason = _read_status(state["project_path"], state["story_id"])
    return {**state, "status": status, "blocked_reason": reason}
```

### Graph with conditional edges

The state machine that is implicit in Celery (queue names, routing keys, scattered enqueue calls) becomes explicit Python code:

```python
def _route_after_tester(state: PipelineState) -> str:
    if state["status"] == Status.READY_TO_ATF:
        return "atf"
    if state["status"] == Status.READY_TO_DEV:
        if state["dev_retries"] < MAX_DEV_RETRIES:
            return "developer"   # quality gate failed → retry
    return END                   # blocked or retries exhausted

def build_pipeline():
    g = StateGraph(PipelineState)
    g.add_node("test_engineer", test_engineer_node)
    g.add_node("developer",     developer_node)
    g.add_node("tester",        tester_node)
    g.add_node("atf",           atf_node)
    g.set_entry_point("test_engineer")
    g.add_conditional_edges("tester", _route_after_tester,
        {"atf": "atf", "developer": "developer", END: END})
    # ... other edges
    return g.compile()
```

The retry logic, the blocking conditions, the terminal states — all visible, all in one place.

### LangGraph executor

```python
# infrastructure/langgraph/pipeline_executor.py
class LangGraphPipelineExecutor(PipelineExecutor):
    def __init__(self, project_path: str) -> None:
        self._project_path = project_path
        self._pipeline = build_pipeline()

    def submit(self, story_id: str) -> None:
        self._pipeline.invoke({
            "story_id": story_id,
            "project_path": self._project_path,
            "status": Status.INBOX,
            "blocked_reason": None,
            "dev_retries": 0,
        })
```

No broker, no worker containers:

```bash
PIPELINE_ENGINE=langgraph python -m atdd_orchestrator
```

---

## The design decisions worth discussing

### Why is the state stored in files, not a database?

Each user story's state lives in a `story.md` file with YAML frontmatter:

```yaml
---
id: US04
title: User can reset their password
status: in-progress:ready-to-test
sprint: sprint_02
---
```

Keeping state in the repository means:
- Any agent, any tool, any human can read and update it with a text editor
- The state survives restarts with no migration
- Git history shows every state transition
- The orchestrator doesn't own the state — **the project does**

### Why is the Architect role never automated?

The architect (human + Claude) defines scope, acceptance criteria, and what the story means. That judgment stays human-controlled.

Automating that step is how you end up building the wrong thing perfectly. The spec is the contract — someone has to own it.

### Why Celery for production and LangGraph for local development?

Celery runs each role in its own isolated container. If the tester container is slow, developer keeps working. If a container crashes, Redis holds the message — the worker picks it up when it restarts. Multiple stories across multiple projects advance simultaneously.

LangGraph runs the full pipeline in a single process. One slow story blocks the orchestrator for everything else. A mid-pipeline crash leaves the story in an intermediate state with no resume mechanism.

LangGraph is the right choice when you want to debug a single story locally without standing up the full Docker stack. Celery is the right choice when you're running multiple projects autonomously and you need the system to recover without you.

Both share the **same domain and the same use cases**. The engine is only an infrastructure choice.

### The GraphRoutedQueue pattern

The use cases call `self._queue.enqueue("run_tester", story_id)` as a side effect of their execution. In the LangGraph world, that call is meaningless — the graph reads the story status and decides the next node.

Rather than modifying the use cases (which would break the Celery flow), LangGraph nodes pass a `GraphRoutedQueue` that absorbs enqueue calls silently. The use case's core behavior — running the agent, saving the status, raising on failure — is unchanged. Only the routing side effect is suppressed.

This is dependency injection doing exactly what it's supposed to do.

---

## What I tested on a real project

The first project running through this pipeline is [atf-ai](https://github.com/csotelo/atdd-framework/tree/main/atf-ai) — a CLI tool with Playwright-based acceptance tests. Five user stories, end-to-end:

| Story | Status |
|---|---|
| US01 — Scaffolding CLI | `damaged` (1 failing scenario, known issue) |
| US02 — Docker Runner | `accepted` ✓ |
| US03 — Screenplay Actors & Steps | `accepted` ✓ |
| US04 — Feedback & State Tracking | `accepted` ✓ |
| US05 — Reports Pipeline & PyPI | `accepted` ✓ |

Four out of five stories went from `inbox` to `done` autonomously. The fifth is blocked on a known state mismatch that requires architectural review — exactly the kind of thing that should block, not silently pass.

---

## What's next

- **LangGraph checkpointing** — persist graph state to disk so a local pipeline can resume after a crash without re-running completed stages
- **Observability** — emit structured events at each node transition for unified tracing across both engines
- **Self-healing architect** — when a story is `blocked`, trigger a Claude session to diagnose and propose a fix
- **Dynamic worker scaling** — scale Celery workers per queue based on backlog depth

---

## Repository

The full source is open:

**[github.com/csotelo/atdd-framework](https://github.com/csotelo/atdd-framework)**

```
atdd_orchestrator/
├── __main__.py      # entry point — python -m atdd_orchestrator
├── domain/          # Story, Status, ports — pure Python
├── application/     # use cases — depend only on domain
└── infrastructure/
    ├── git_adapter.py            # pure git adapter
    ├── celery/
    │   ├── pipeline_executor.py  # PipelineExecutor → send_task (production)
    │   ├── queue_adapter.py      # TaskQueue → inter-worker enqueue
    │   └── tasks.py              # thin Celery tasks → use cases
    └── langgraph/
        ├── pipeline_executor.py  # PipelineExecutor → graph.invoke (local dev)
        ├── nodes.py              # nodes → use cases (GraphRoutedQueue)
        └── graph.py              # StateGraph with conditional edges + retry logic
```

35 tests, 0 failures. No Redis, no OpenCode, no network required to run the test suite — all ports are stubbed.

---

## Final thought

The thing that surprised me most about this project wasn't the AI part. It was how much the design decisions at the domain level determined what was possible later.

`PipelineExecutor` is a four-line abstract class. But because it exists, you can swap the execution engine with an env var, test the entire orchestration logic without Redis or Docker, and reason about Celery and LangGraph as implementation details rather than architectural constraints.

The entry point lives in `__main__.py` — not buried in `infrastructure/`. The git adapter lives in `infrastructure/git_adapter.py` — a pure adapter with no business logic. Every file is in the layer where it belongs.

If you're building multi-agent pipelines: get the ports right first. Put things in the right layer. The implementations will follow.

---

*Questions, issues, or contributions: [github.com/csotelo/atdd-framework](https://github.com/csotelo/atdd-framework)*
