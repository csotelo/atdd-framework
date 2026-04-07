from atdd_orchestrator.domain.ports import PipelineExecutor
from atdd_orchestrator.infrastructure.celery.app import app


class CeleryPipelineExecutor(PipelineExecutor):
    """Submits the story to the first Celery worker (test_engineer → inbox queue)."""

    def __init__(self, project_path: str) -> None:
        self._project_path = project_path

    def submit(self, story_id: str) -> None:
        app.send_task(
            "run_test_engineer",
            args=[self._project_path, story_id],
            queue="inbox",
        )
