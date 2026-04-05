# ATDD Framework — Estado del proyecto
_Guardado: 2026-04-03_

## Qué es esto

Framework de desarrollo ATDD (Acceptance Test Driven Development) implementado como
skills de Claude Code. Permite llevar una historia de usuario desde spec hasta aceptación
sin intervención humana en las etapas técnicas.

---

## Skills creados (en ~/.claude/skills/)

| Skill | Estado | Rol |
|---|---|---|
| `atdd_architect` | Completo | Crea sprints, historias, contratos. MANUAL (Claude + humano) |
| `atdd_test_engineer` | Completo | Escribe tests en RED antes de que exista código |
| `atdd_developer` | Completo | Hace los tests RED pasar (GREEN). Automático via OpenCode |
| `atdd_tester` | Completo | Valida regresiones y calidad. Automático via OpenCode |

---

## Pipeline completo

```
[Humano + Claude]
    │
    ▼ architect crea historias y marca sprint como ready
    │
    ▼ story.md → status: ready
    │
[Celery + Redis — AUTOMÁTICO]
    │
    ├── test_engineer (OpenCode) → status: tests-written
    │   Escribe unit + integration tests en RED
    │
    ├── developer (OpenCode)    → status: built
    │   Hace que los tests pasen (GREEN)
    │
    ├── tester (OpenCode)       → status: tested
    │   Verifica regresiones, calidad (ruff, mypy)
    │
    └── atf_worker (atf-ai)     → status: accepted
        Corre acceptance.feature con Playwright/Behave
```

---

## Estados de una historia

| Status | Quién lo asigna |
|---|---|
| `draft` | architect (historia identificada, sin refinar) |
| `ready` | architect (refinada: story.md + prompt.md + acceptance.feature) |
| `tests-written` | test_engineer (tests en RED escritos) |
| `in-progress` | developer (trabajando) |
| `built` | developer (código escrito, tests pasan) |
| `tested` | tester (regresiones OK, calidad OK) |
| `accepted` | ATF tool (Gherkin scenarios pasaron) |
| `blocked` | cualquier rol (con nota de qué falló) |
| `unverified` | architect en migración (funciona pero sin tests) |
| `damaged` | architect en recovery (tests fallan) |
| `unknown` | architect en recovery (sin tests, sin forma de verificar) |

---

## Estructura de archivos del framework

```
.atdd/                              ← dentro de cada proyecto
├── SPEC.md                         ← spec macro inmutable
├── SCOPE.md                        ← qué hace y qué NO hace
├── STACK.md                        ← tecnologías con versiones
├── STATE.md                        ← estado global
├── atf.config.json                 ← { "promptsDir": ".atdd/backlog" }
├── baseline.txt                    ← generado por test_engineer antes de cada US
├── backlog/
│   └── US01-nombre/
│       ├── story.md                ← frontmatter: id, title, status, sprint
│       ├── prompt.md               ← instrucciones para developer
│       ├── acceptance.feature      ← Gherkin para ATF tool
│       └── tests-red.txt           ← output de pytest al escribir tests en RED
└── sprints/
    └── sprint_01/
        ├── SPEC.md                 ← qué entrega este sprint técnicamente
        ├── SCOPE.md                ← qué incluye y qué NO incluye
        ├── STATE.md                ← estado del sprint
        └── stories.md              ← lista de USs asignadas
```

---

## Orquestador — COMPLETO

**Ubicación:** `/home/csotelo/Development/ventures/atdd/`

**Stack:**
- Celery + Redis (broker para independencia entre roles)
- OpenCode (`opencode run "prompt"`) para roles automáticos
- Python puro — arquitectura hexagonal

**Estructura:**
```
atdd/
├── atdd_orchestrator/
│   ├── config.py
│   ├── dispatcher.py              ← entry point, polling cada 30s
│   ├── domain/
│   │   ├── story.py               ← entidad Story + value object Status
│   │   └── ports.py               ← interfaces: StoryRepository, CodeRunner, TaskQueue
│   ├── application/
│   │   └── use_cases/
│   │       ├── dispatch.py        ← orquesta transitions
│   │       ├── run_test_engineer.py
│   │       ├── run_developer.py
│   │       ├── run_tester.py
│   │       └── run_atf.py
│   └── infrastructure/
│       ├── frontmatter_repo.py    ← StoryRepository (frontmatter)
│       ├── opencode_runner.py     ← CodeRunner (subprocess opencode)
│       └── celery/
│           ├── app.py             ← instancia Celery
│           ├── queue_adapter.py   ← TaskQueue (Celery)
│           └── tasks.py           ← wrappers delgados → use cases
├── tests/
│   ├── stubs.py                   ← stubs reutilizables de puertos
│   ├── domain/
│   ├── application/use_cases/
│   └── infrastructure/
├── docker-compose.yml             ← solo Redis
├── pyproject.toml
└── install.sh                     ← sincroniza skills + instala dependencias
```

**Reglas de dependencia (hexagonal):**
- `domain` → sin dependencias externas
- `application` → solo importa `domain`
- `infrastructure` → importa `domain` + `application` + librerías externas
- Use cases testeables sin Redis ni OpenCode (stubs de puertos)

**Tests:** 35 tests, 0 fallos, sin dependencias externas

**Cómo instalar:**
```bash
bash install.sh
```

**Cómo correr:**
```bash
docker compose up -d
.venv/bin/celery -A atdd_orchestrator.infrastructure.celery.app worker --loglevel=info
.venv/bin/python -m atdd_orchestrator.dispatcher <path_al_proyecto>
```

---

## Modo migración (nuevo en atdd_architect)

Para proyectos con formato legacy (.atf/ con sprints que son USs):

1. Leer `atf-state.json` → mapear qué pasó
2. Archivar en `.atdd/archive/legacy-YYYY-MM-DD/`
3. Crear `backlog/US0N-nombre/` para cada sprint legacy
4. Status según atf-state: passed→accepted, failed→damaged, no corrido→unverified
5. Generar `MIGRATION.md`
6. Inicializar nueva estructura `.atdd/`

**Primer caso real:** proyecto ATF en `/home/csotelo/Development/ventures/atf-ai/`

---

## Proyecto ATF (atf-ai)

**Ubicación:** `/home/csotelo/Development/ventures/atdd/atf-ai/`
**Formato:** `.atdd/` — migrado el 2026-04-03

| Historia | Sprint | Status |
|---|---|---|
| US01-scaffolding-cli | sprint_01 | `damaged` (1 scenario fallido) |
| US02-docker-runner | sprint_02 | `accepted` ✓ |
| US03-screenplay-actors-steps | sprint_03 | `accepted` ✓ |
| US04-feedback-state-tracking | sprint_04 | `accepted` ✓ |
| US05-reports-pipeline-pypi | sprint_05 | `accepted` ✓ |

**Pendiente:** resolver US01 — el step `sprint_01 should have status pending` falla porque el estado real es `failed`.

---

## Notas personales

- El arquitecto siempre es colaborativo (Claude + humano), nunca automático
- Claude se usa para tareas estratégicas (créditos bien invertidos)
- OpenCode para tareas técnicas automatizadas (test_engineer, developer, tester)
- El usuario es peruano — no usar "vos" ni expresiones argentinas
