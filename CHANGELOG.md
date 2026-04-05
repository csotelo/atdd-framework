# Changelog

All notable changes to this project will be documented in this file.
Most recent changes at the top.

Format: `[version] — YYYY-MM-DD`

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
