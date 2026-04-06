"""
Dispatcher LangGraph — alternativa a Celery sin Redis.

Pollea el repo cada POLL_INTERVAL segundos buscando historias en
status INBOX y lanza el grafo de pipeline por cada una.

Uso:
    .venv/bin/python dispatcher_langgraph.py <path_al_proyecto>
"""
import logging
import sys
import time

from atdd_orchestrator.config import POLL_INTERVAL
from atdd_orchestrator.domain.story import Status
from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository
from atdd_orchestrator.infrastructure.langgraph.graph import build_pipeline

log = logging.getLogger(__name__)


def run(project_path: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Dispatcher LangGraph iniciado — proyecto: %s | polling cada %ds", project_path, POLL_INTERVAL)

    pipeline = build_pipeline()

    while True:
        try:
            repo = FrontmatterStoryRepository(project_path)
            inbox = repo.find_by_status(Status.INBOX)

            for story_id in inbox:
                log.info("Lanzando pipeline para historia: %s", story_id)
                initial_state = {
                    "story_id": story_id,
                    "project_path": project_path,
                    "status": Status.INBOX,
                    "blocked_reason": None,
                    "dev_retries": 0,
                }
                final_state = pipeline.invoke(initial_state)
                log.info(
                    "Pipeline completado — historia: %s | status final: %s",
                    story_id,
                    final_state.get("status"),
                )

        except Exception:
            log.exception("Error en ciclo de dispatch")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python dispatcher_langgraph.py <project_path>")
        sys.exit(1)
    run(sys.argv[1])
