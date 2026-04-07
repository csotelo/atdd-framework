# Changelog

All notable changes to this project will be documented in this file.
Most recent changes at the top.

Format: `[version] — YYYY-MM-DD`

---

## [0.3.0] — 2026-04-07

### Added

- `PipelineExecutor` port in `domain/ports.py` — abstracts the pipeline execution engine from dispatch logic
- `infrastructure/celery/pipeline_executor.py` — `CeleryPipelineExecutor`: submits the story to the first worker via `send_task`
- `infrastructure/langgraph/pipeline_executor.py` — `LangGraphPipelineExecutor`: runs the full graph in-process
- `infrastructure/git_adapter.py` — pure git adapter: configure, pull, detect changes, commit, push
- `atdd_orchestrator/__main__.py` — proper entry point; runs with `python -m atdd_orchestrator`
- `PIPELINE_ENGINE` env var in `config.py` — selects the engine (`"celery"` default | `"langgraph"`)

### Changed

- `application/use_cases/dispatch.py` — `DispatchStories` receives `PipelineExecutor` instead of `TaskQueue`
- `infrastructure/langgraph/nodes.py` — `_NoOpQueue` renamed to `GraphRoutedQueue` with explicit docstring
- `services/git-sync/Dockerfile` — CMD updated to `python -m atdd_orchestrator`
- All docstrings, comments, log messages and agent prompts translated to English

### Removed

- `atdd_orchestrator/dispatcher.py` — removed (was marked OBSOLETE since 0.2.0)
- `dispatcher_langgraph.py` (root) — removed; absorbed by `LangGraphPipelineExecutor`
- `infrastructure/git_sync.py` — removed; split into `__main__.py` + `infrastructure/git_adapter.py`

### Architecture decisions

- `__main__.py` is the correct entry point in hexagonal architecture — application drivers do not belong in `infrastructure/`
- `infrastructure/git_adapter.py` is a pure adapter: only git operations, no orchestration logic
- `PipelineExecutor` is the right port for the pipeline entry point; `TaskQueue` is restricted to inter-worker communication within the Celery engine
- Celery is the production engine: real container isolation, parallel projects, crash resilience
- LangGraph is the local development engine: no Redis, no workers, sequential in-process execution
- Launch: `python -m atdd_orchestrator` (local) or `docker compose up` (production)

---

## [0.2.0] — 2026-04-06

### Added

- LangGraph adapter as an alternative to Celery + Redis (`infrastructure/langgraph/`)
  - `state.py` — `PipelineState` TypedDict with story, status, retries
  - `nodes.py` — 4 nodes that call existing use cases with `NoOpQueue`
  - `graph.py` — `StateGraph` with conditional edges: automatic retry up to 3 times if tester/atf fail
- `dispatcher_langgraph.py` — Redis-free entry point; invokes the graph per story in INBOX status
- `langgraph` as optional dependency in `pyproject.toml` (`pip install -e ".[langgraph]"`)

### Architecture decisions

- LangGraph makes routing explicit (conditional edges) instead of use cases enqueuing the next task
- Use cases receive `NoOpQueue` — no changes to domain or existing use cases
- Celery remains available; LangGraph is opt-in, not a mandatory replacement

---

## [0.1.0] — 2026-04-03

### Added

- Full orchestrator with hexagonal architecture (domain / application / infrastructure)
- `Story` entity + `Status` value object in `domain/story.py`
- Ports `StoryRepository`, `CodeRunner`, `TaskQueue` in `domain/ports.py`
- Use cases: `dispatch`, `run_test_engineer`, `run_developer`, `run_tester`, `run_atf`
- `FrontmatterRepo` — `StoryRepository` implementation reading `story.md` via YAML frontmatter
- `OpenCodeRunner` — `CodeRunner` implementation via subprocess `opencode run`
- Celery app + `CeleryQueueAdapter` + thin tasks per autonomous role
- `dispatcher.py` — entry point with 30s polling
- 35 unit and integration tests with no external dependencies (port stubs in `tests/stubs.py`)
- Claude Code skills: `atdd_architect`, `atdd_test_engineer`, `atdd_developer`, `atdd_tester`
- `install.sh` — syncs skills to `~/.claude/skills/` and installs dependencies in `.venv/`
- `docker-compose.yml` — Redis as broker
- `projects.yml.example` — multi-project configuration example
- Migration mode in `atdd_architect`: converts legacy `.atf/` projects to the new `.atdd/` format
- Real migration of `atf-ai` project — 5 stories migrated (4 `accepted`, 1 `damaged`)
- `PROYECTO.md` — project status document

### Architecture decisions

- Celery + Redis as broker for isolation between autonomous roles
- OpenCode for technical tasks (Claude credits reserved for strategic work)
- The `architect` role is always collaborative (Claude + human), never automated
- Explicit statuses in `story.md` frontmatter as the single source of truth
