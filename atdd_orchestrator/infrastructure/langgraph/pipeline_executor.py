from atdd_orchestrator.domain.ports import PipelineExecutor
from atdd_orchestrator.domain.story import Status
from atdd_orchestrator.infrastructure.langgraph.graph import build_pipeline

import logging

log = logging.getLogger(__name__)


class LangGraphPipelineExecutor(PipelineExecutor):
    """Ejecuta el pipeline completo en proceso usando el grafo LangGraph.

    No requiere Redis ni workers externos. El grafo maneja el routing
    entre nodos (test_engineer → developer → tester → atf).
    """

    def __init__(self, project_path: str) -> None:
        self._project_path = project_path
        self._pipeline = build_pipeline()

    def submit(self, story_id: str) -> None:
        log.info("LangGraph: iniciando pipeline para historia=%s", story_id)
        final_state = self._pipeline.invoke({
            "story_id": story_id,
            "project_path": self._project_path,
            "status": Status.INBOX,
            "blocked_reason": None,
            "dev_retries": 0,
        })
        log.info(
            "LangGraph: pipeline completado historia=%s status=%s",
            story_id,
            final_state.get("status"),
        )
