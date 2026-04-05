from atdd_orchestrator.domain.ports import TaskQueue
from atdd_orchestrator.infrastructure.celery.app import app

# Mapeo task_name → cola dedicada (debe coincidir con task_routes en app.py)
_QUEUE_MAP: dict[str, str] = {
    "run_test_engineer": "inbox",
    "run_developer":     "ready-to-dev",
    "run_tester":        "ready-to-test",
    "run_atf":           "ready-to-atf",
}


class CeleryTaskQueue(TaskQueue):
    def __init__(self, project_path: str) -> None:
        self._project_path = project_path

    def enqueue(self, task_name: str, story_id: str) -> None:
        queue = _QUEUE_MAP[task_name]
        app.send_task(task_name, args=[self._project_path, story_id], queue=queue)
