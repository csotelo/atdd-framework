# Changelog

All notable changes to this project will be documented in this file.
Most recent changes at the top.

Format: `[version] — YYYY-MM-DD`

---

## [0.3.0] — 2026-04-07

### Added

- Puerto `PipelineExecutor` en `domain/ports.py` — abstracción del motor de ejecución del pipeline
- `infrastructure/celery/pipeline_executor.py` — `CeleryPipelineExecutor`: envía la historia al primer worker via `send_task`
- `infrastructure/langgraph/pipeline_executor.py` — `LangGraphPipelineExecutor`: ejecuta el grafo completo en proceso
- `PIPELINE_ENGINE` env var en `config.py` — selecciona el motor (`"celery"` default | `"langgraph"`)

### Changed

- `application/use_cases/dispatch.py` — `DispatchStories` recibe `PipelineExecutor` en lugar de `TaskQueue`; responsabilidad única y clara
- `infrastructure/langgraph/nodes.py` — `_NoOpQueue` renombrado a `GraphRoutedQueue` con docstring que explica el patrón explícitamente
- `services/git-sync/Dockerfile` — CMD actualizado a `python -m atdd_orchestrator`

### Removed

- `atdd_orchestrator/dispatcher.py` — eliminado (era OBSOLETO desde 0.2.0)
- `dispatcher_langgraph.py` (raíz) — eliminado; absorbido por `LangGraphPipelineExecutor`
- `infrastructure/git_sync.py` — eliminado; separado en `__main__.py` + `infrastructure/git_adapter.py`

### Architecture decisions

- `__main__.py` es el entry point correcto en hexagonal architecture — los drivers de la aplicación no pertenecen a `infrastructure/`
- `infrastructure/git_adapter.py` es un adaptador puro: solo operaciones git sin lógica de orquestación
- `PipelineExecutor` es el puerto correcto para el punto de entrada del pipeline; `TaskQueue` queda restringido a la comunicación interna entre workers Celery
- Celery es el motor de producción: aislamiento real por container, paralelismo entre proyectos, resiliencia ante caídas
- LangGraph es el motor de desarrollo local: sin Redis, sin workers, ejecución secuencial en proceso
- Lanzamiento: `python -m atdd_orchestrator` (local) o `docker compose up` (producción)

---

## [0.2.0] — 2026-04-06

### Added

- Adaptador LangGraph como alternativa a Celery + Redis (`infrastructure/langgraph/`)
  - `state.py` — `PipelineState` TypedDict con story, status, retries
  - `nodes.py` — 4 nodos que llaman los use cases existentes con `NoOpQueue`
  - `graph.py` — `StateGraph` con edges condicionales: retry automático hasta 3 veces si tester/atf fallan
- `dispatcher_langgraph.py` — entry point sin Redis; lanza el grafo por historia en status INBOX
- `langgraph` como dependencia opcional en `pyproject.toml` (`pip install -e ".[langgraph]"`)

### Architecture decisions

- LangGraph hace el routing explícito (edges condicionales) en lugar de que los use cases encolen la siguiente tarea
- Los use cases reciben `NoOpQueue` — sin cambios al dominio ni a los use cases existentes
- Celery sigue disponible; LangGraph es opt-in, no un reemplazo obligatorio

---

## [0.1.0] — 2026-04-03

### Added

- Orquestador completo con arquitectura hexagonal (domain / application / infrastructure)
- `Story` entity + `Status` value object en `domain/story.py`
- Puertos `StoryRepository`, `CodeRunner`, `TaskQueue` en `domain/ports.py`
- Use cases: `dispatch`, `run_test_engineer`, `run_developer`, `run_tester`, `run_atf`
- `FrontmatterRepo` — implementación de `StoryRepository` leyendo `story.md` con frontmatter YAML
- `OpenCodeRunner` — implementación de `CodeRunner` vía subprocess `opencode run`
- Celery app + `CeleryQueueAdapter` + tasks delgados para cada rol automático
- `dispatcher.py` — entry point con polling cada 30s
- 35 tests unitarios e de integración sin dependencias externas (stubs de puertos en `tests/stubs.py`)
- Skills de Claude Code: `atdd_architect`, `atdd_test_engineer`, `atdd_developer`, `atdd_tester`
- `install.sh` — sincroniza skills en `~/.claude/skills/` e instala dependencias en `.venv/`
- `docker-compose.yml` — Redis como broker
- `projects.yml.example` — configuración multi-proyecto de ejemplo
- Modo migración en `atdd_architect`: convierte proyectos legacy `.atf/` al nuevo formato `.atdd/`
- Migración real del proyecto `atf-ai` — 5 historias migradas (4 `accepted`, 1 `damaged`)
- `PROYECTO.md` — documento de estado del proyecto

### Architecture decisions

- Celery + Redis como broker para independencia entre roles automáticos
- OpenCode para tareas técnicas (créditos Claude reservados para trabajo estratégico)
- El rol `architect` es siempre colaborativo (Claude + humano), nunca automático
- Estados explícitos en frontmatter de `story.md` como fuente de verdad
