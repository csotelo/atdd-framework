"""
Servicio git-sync — punto de entrada del contenedor git-sync.

Responsabilidades:
  1. Cargar projects.yml
  2. Por cada proyecto: git pull
  3. Detectar historias con status inbox → encolar en Celery
  4. Detectar cambios sin commit → git add + commit + push

Uso:
    python -m atdd_orchestrator.infrastructure.git_sync
"""
import logging
import subprocess
import time
from pathlib import Path

import yaml

from atdd_orchestrator.application.use_cases.dispatch import DispatchStories
from atdd_orchestrator.config import (
    POLL_INTERVAL,
    PROJECTS_FILE,
    GIT_USER_NAME,
    GIT_USER_EMAIL,
)
from atdd_orchestrator.infrastructure.celery.queue_adapter import CeleryTaskQueue
from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository

log = logging.getLogger(__name__)


def _git(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _configure_git(project_path: str) -> None:
    _git(["config", "user.name",  GIT_USER_NAME],  cwd=project_path)
    _git(["config", "user.email", GIT_USER_EMAIL], cwd=project_path)


def _pull(project_path: str) -> None:
    result = _git(["pull", "--rebase", "--autostash"], cwd=project_path)
    if result.returncode != 0:
        log.warning("git pull falló en %s: %s", project_path, result.stderr.strip())


def _has_changes(project_path: str) -> bool:
    result = _git(["status", "--porcelain"], cwd=project_path)
    return bool(result.stdout.strip())


def _commit_and_push(project_path: str) -> None:
    _git(["add", "-A"], cwd=project_path)
    result = _git(
        ["commit", "-m", "chore(atdd): actualización automática de estado"],
        cwd=project_path,
    )
    if result.returncode != 0:
        log.warning("git commit falló en %s: %s", project_path, result.stderr.strip())
        return
    push = _git(["push"], cwd=project_path)
    if push.returncode != 0:
        log.warning("git push falló en %s: %s", project_path, push.stderr.strip())
    else:
        log.info("git push OK — %s", project_path)


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
    _configure_git(project_path)
    _pull(project_path)

    repo  = FrontmatterStoryRepository(project_path)
    queue = CeleryTaskQueue(project_path)
    DispatchStories(repo, queue).execute()

    if _has_changes(project_path):
        _commit_and_push(project_path)


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("git-sync iniciado — polling cada %ds | proyectos: %s", POLL_INTERVAL, PROJECTS_FILE)

    while True:
        projects = _load_projects()
        for project_path in projects:
            try:
                _process_project(project_path)
            except Exception:
                log.exception("Error procesando %s", project_path)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
