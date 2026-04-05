"""
Migración de formato legacy .atf/ → nuevo formato .atdd/

Ejecutar desde la raíz del proyecto atf-ai:
    python migrate.py
"""
import json
import shutil
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).parent
ATF_DIR = PROJECT / ".atf"
ATDD_DIR = PROJECT / ".atdd"
TODAY = date.today().isoformat()

STATUS_MAP = {
    "passed": "accepted",
    "failed": "damaged",
    "pending": "unverified",
}

STORIES = [
    ("US01", "sprint_01", "scaffolding-cli",            "Project Scaffolding & CLI"),
    ("US02", "sprint_02", "docker-runner",               "Docker Runner"),
    ("US03", "sprint_03", "screenplay-actors-steps",     "Screenplay Actors & Full Step Library"),
    ("US04", "sprint_04", "feedback-state-tracking",     "Feedback & State Tracking"),
    ("US05", "sprint_05", "reports-pipeline-pypi",       "Reports, Full Pipeline & PyPI"),
]


def archive_legacy() -> None:
    archive = ATDD_DIR / "archive" / f"legacy-{TODAY}"
    archive.mkdir(parents=True)
    shutil.copytree(ATF_DIR, archive / ".atf")
    print(f"  ✓ Legacy archivado en {archive.relative_to(PROJECT)}")


def read_state() -> dict:
    return json.loads((ATF_DIR / "atf-state.json").read_text())["sprints"]


def create_backlog(sprints_state: dict) -> None:
    backlog = ATDD_DIR / "backlog"
    backlog.mkdir(parents=True)

    for us_id, sprint_id, slug, title in STORIES:
        sprint_state = sprints_state.get(sprint_id, {})
        legacy_status = sprint_state.get("status", "pending")
        new_status = STATUS_MAP[legacy_status]
        story_dir = backlog / f"{us_id}-{slug}"
        story_dir.mkdir()

        # story.md
        story_lines = [
            "---",
            f"id: {us_id}",
            f"title: \"{title}\"",
            f"status: {new_status}",
            f"sprint: {sprint_id}",
            f"migrated_from: .atf/prompts/{sprint_id}",
            f"legacy_status: {legacy_status}",
        ]
        if legacy_status == "failed" and sprint_state.get("failures"):
            first = sprint_state["failures"][0]
            story_lines.append(f"blocked_reason: \"{first['scenario']} — {first['step']}\"")
        story_lines += ["---", "", f"Historia migrada desde el sprint legacy `{sprint_id}`.", ""]
        (story_dir / "story.md").write_text("\n".join(story_lines))

        # prompt.md y acceptance.feature — copiar del legacy
        src = ATF_DIR / "prompts" / sprint_id
        shutil.copy(src / "prompt.md", story_dir / "prompt.md")
        shutil.copy(src / "acceptance.feature", story_dir / "acceptance.feature")

        print(f"  ✓ {us_id}-{slug} → status: {new_status}")


def create_sprints(sprints_state: dict) -> None:
    sprints_dir = ATDD_DIR / "sprints"

    for us_id, sprint_id, slug, title in STORIES:
        sprint_dir = sprints_dir / sprint_id
        sprint_dir.mkdir(parents=True)

        sprint_state = sprints_state.get(sprint_id, {})
        legacy_status = sprint_state.get("status", "pending")
        passed = legacy_status == "passed"
        scenarios = sprint_state.get("scenarios", {})

        (sprint_dir / "SPEC.md").write_text(
            f"# Sprint {sprint_id} — {title}\n\n"
            f"Entrega: {title}.\n"
            f"Migrado desde legacy el {TODAY}.\n"
        )
        (sprint_dir / "SCOPE.md").write_text(
            f"# Scope — {sprint_id}\n\n"
            f"## Incluye\n- Historia {us_id}: {title}\n\n"
            f"## No incluye\n- Cambios fuera del scope de {sprint_id}\n"
        )
        (sprint_dir / "STATE.md").write_text(
            f"# State — {sprint_id}\n\n"
            f"| Campo | Valor |\n|---|---|\n"
            f"| Status | {'passed ✓' if passed else 'failed ✗'} |\n"
            f"| Last run | {sprint_state.get('last_run', 'N/A')} |\n"
            f"| Scenarios | {scenarios.get('passed', 0)}/{scenarios.get('total', 0)} passed |\n"
        )
        (sprint_dir / "stories.md").write_text(
            f"# Stories — {sprint_id}\n\n- {us_id}-{slug}\n"
        )

    print(f"  ✓ {len(STORIES)} sprints creados")


def create_spec_files() -> None:
    project_desc = (ATF_DIR / "project-description.md").read_text()

    (ATDD_DIR / "SPEC.md").write_text(
        "# SPEC — ATF (Acceptance Testing Framework)\n\n"
        + project_desc
    )

    (ATDD_DIR / "SCOPE.md").write_text(
        "# SCOPE — ATF\n\n"
        "## Qué hace ATF\n"
        "- Ejecutar tests de aceptación Gherkin dentro de Docker (Playwright)\n"
        "- Actualizar atf-state.json y STATE.md con resultados\n"
        "- Generar reportes HTML y JSON por sprint\n"
        "- Escribir feedback.md estructurado cuando un test falla\n"
        "- Publicarse en PyPI como `atf-framework`\n\n"
        "## Qué NO hace ATF\n"
        "- No genera código\n"
        "- No planifica sprints\n"
        "- No toma decisiones de arquitectura\n"
        "- No instala browsers en el host\n"
    )

    (ATDD_DIR / "STACK.md").write_text(
        "# STACK — ATF\n\n"
        "| Tecnología | Versión | Rol |\n|---|---|---|\n"
        "| Python | 3.11+ | Lenguaje principal |\n"
        "| Behave | latest | Runner de Gherkin |\n"
        "| Playwright | latest | Automatización de browser |\n"
        "| Docker | latest | Entorno de ejecución aislado |\n"
        "| behave-html-formatter | latest | Reportes HTML |\n"
        "| Hatchling | latest | Build backend PyPI |\n"
        "| Ruff | latest | Linting |\n"
        "| Mypy | latest | Type checking |\n"
    )

    (ATDD_DIR / "STATE.md").write_text(
        f"# STATE — ATF\n_Migrado: {TODAY}_\n\n"
        "## Estado global\n"
        "- US01-scaffolding-cli: **damaged** (sprint_01 falló — 1 scenario)\n"
        "- US02-docker-runner: **accepted** ✓\n"
        "- US03-screenplay-actors-steps: **accepted** ✓\n"
        "- US04-feedback-state-tracking: **accepted** ✓\n"
        "- US05-reports-pipeline-pypi: **accepted** ✓\n\n"
        "## Bloqueado\n"
        "US01 requiere que el step `sprint_01 should have status pending` refleje "
        "el estado real (actualmente `failed`, no `pending`).\n"
    )

    (ATDD_DIR / "atf.config.json").write_text(
        json.dumps({"promptsDir": ".atdd/backlog"}, indent=2) + "\n"
    )

    print("  ✓ SPEC.md, SCOPE.md, STACK.md, STATE.md, atf.config.json")


def create_migration_report(sprints_state: dict) -> None:
    lines = [
        f"# MIGRATION.md — legacy .atf/ → .atdd/",
        f"_Fecha: {TODAY}_\n",
        "## Origen",
        "Formato legacy `.atf/` con 5 sprints lineales.\n",
        "## Resultado",
        "| Historia | Sprint legacy | Status legacy | Status nuevo |",
        "|---|---|---|---|",
    ]
    for us_id, sprint_id, slug, title in STORIES:
        legacy = sprints_state.get(sprint_id, {}).get("status", "pending")
        nuevo = STATUS_MAP[legacy]
        lines.append(f"| {us_id}-{slug} | {sprint_id} | {legacy} | {nuevo} |")

    lines += [
        "",
        "## Archivado",
        f"El directorio `.atf/` fue copiado a `.atdd/archive/legacy-{TODAY}/`.",
        "El `.atf/` original no fue eliminado — puede borrarse manualmente.",
        "",
        "## Pendiente",
        "- US01-scaffolding-cli tiene status `damaged`.",
        "  El scenario fallido era: *sprint_01 should have status pending*.",
        "  Requiere revisar si el step debe actualizarse o si el test ya no aplica.",
    ]

    (ATDD_DIR / "MIGRATION.md").write_text("\n".join(lines) + "\n")
    print("  ✓ MIGRATION.md")


def main() -> None:
    print(f"\n=== Migración .atf/ → .atdd/ ===\n")

    if ATDD_DIR.exists():
        print(f"  ATDD_DIR ya existe. Eliminando para re-migrar...")
        shutil.rmtree(ATDD_DIR)

    ATDD_DIR.mkdir()
    sprints_state = read_state()

    print("\n[1/5] Archivando legacy...")
    archive_legacy()

    print("\n[2/5] Creando backlog...")
    create_backlog(sprints_state)

    print("\n[3/5] Creando sprints...")
    create_sprints(sprints_state)

    print("\n[4/5] Creando SPEC / SCOPE / STACK / STATE...")
    create_spec_files()

    print("\n[5/5] Generando MIGRATION.md...")
    create_migration_report(sprints_state)

    print("\n=== Migración completa ===\n")
    print(f"Estructura creada en: {ATDD_DIR.relative_to(PROJECT)}/")


if __name__ == "__main__":
    main()
