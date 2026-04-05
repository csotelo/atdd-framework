"""
OBSOLETO — reemplazado por infrastructure/git_sync.py

Este módulo era el dispatcher de polling local. El pipeline ahora
corre completamente en Docker Compose via git-sync + workers Celery.

Ver: docker-compose.yml y services/git-sync/Dockerfile
"""
import logging
import sys
import time

from atdd_orchestrator.application.use_cases.dispatch import DispatchStories
from atdd_orchestrator.config import POLL_INTERVAL
from atdd_orchestrator.infrastructure.celery.queue_adapter import CeleryTaskQueue
from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository

log = logging.getLogger(__name__)


def run(project_path: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Dispatcher iniciado — proyecto: %s | polling cada %ds", project_path, POLL_INTERVAL)

    while True:
        try:
            repo = FrontmatterStoryRepository(project_path)
            queue = CeleryTaskQueue(project_path)
            DispatchStories(repo, queue).execute()
        except Exception:
            log.exception("Error en ciclo de dispatch")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m atdd_orchestrator.dispatcher <project_path>")
        sys.exit(1)
    run(sys.argv[1])
