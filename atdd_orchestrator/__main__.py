"""
ATDD Orchestrator — entry point.

Lanza el loop de orquestación: detecta historias listas en cada proyecto
y las despacha al motor configurado (Celery por defecto, LangGraph para desarrollo local).

Uso:
    python -m atdd_orchestrator
"""
import logging
import time
from pathlib import Path

import yaml

from atdd_orchestrator.application.use_cases.dispatch import DispatchStories
from atdd_orchestrator.config import PIPELINE_ENGINE, POLL_INTERVAL, PROJECTS_FILE
from atdd_orchestrator.domain.ports import PipelineExecutor
from atdd_orchestrator.infrastructure import git_adapter
from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository

log = logging.getLogger(__name__)


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


def _load_projects() -> list[str]:
    path = Path(PROJECTS_FILE)
    if not path.exists():
        log.error("No se encontró %s", PROJECTS_FILE)
        return []
    with path.open() as f:
        data = yaml.safe_load(f)
    return data.get("projects", [])


def _process_project(project_path: str) -> None:
    log.info("Procesando proyecto: %s", project_path)
    git_adapter.configure(project_path)
    git_adapter.pull(project_path)

    repo     = FrontmatterStoryRepository(project_path)
    executor = _make_executor(project_path)
    DispatchStories(repo, executor).execute()

    if git_adapter.has_changes(project_path):
        git_adapter.commit_and_push(project_path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info(
        "ATDD Orchestrator iniciado — motor=%s | polling cada %ds | proyectos: %s",
        PIPELINE_ENGINE,
        POLL_INTERVAL,
        PROJECTS_FILE,
    )

    while True:
        for project_path in _load_projects():
            try:
                _process_project(project_path)
            except Exception:
                log.exception("Error procesando %s", project_path)
        time.sleep(POLL_INTERVAL)


main()
