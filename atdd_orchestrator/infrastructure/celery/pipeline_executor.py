from atdd_orchestrator.domain.ports import PipelineExecutor
from atdd_orchestrator.infrastructure.celery.app import app


class CeleryPipelineExecutor(PipelineExecutor):
    """Envía la historia al primer worker Celery (test_engineer → cola inbox)."""

    def __init__(self, project_path: str) -> None:
        self._project_path = project_path

    def submit(self, story_id: str) -> None:
        app.send_task(
            "run_test_engineer",
            args=[self._project_path, story_id],
            queue="inbox",
        )
