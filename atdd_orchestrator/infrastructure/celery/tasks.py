"""
Celery tasks — capa delgada que construye dependencias e invoca use cases.
Cada task escucha exclusivamente su cola dedicada.
"""
from atdd_orchestrator.infrastructure.celery.app import app
from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository
from atdd_orchestrator.infrastructure.opencode_runner import OpenCodeRunner
from atdd_orchestrator.infrastructure.notifier import TelegramNotifier
from atdd_orchestrator.infrastructure.celery.queue_adapter import CeleryTaskQueue
from atdd_orchestrator.application.use_cases.run_test_engineer import RunTestEngineer
from atdd_orchestrator.application.use_cases.run_developer import RunDeveloper
from atdd_orchestrator.application.use_cases.run_tester import RunTester
from atdd_orchestrator.application.use_cases.run_atf import RunAtf


def _deps(project_path: str):
    repo     = FrontmatterStoryRepository(project_path)
    runner   = OpenCodeRunner(project_path)
    queue    = CeleryTaskQueue(project_path)
    notifier = TelegramNotifier()
    return repo, runner, queue, notifier


@app.task(name="run_test_engineer", bind=True, max_retries=0, queue="inbox")
def task_test_engineer(self, project_path: str, story_id: str) -> None:
    repo, runner, queue, notifier = _deps(project_path)
    RunTestEngineer(repo, runner, queue, notifier).execute(story_id)


@app.task(name="run_developer", bind=True, max_retries=0, queue="ready-to-dev")
def task_developer(self, project_path: str, story_id: str) -> None:
    repo, runner, queue, notifier = _deps(project_path)
    RunDeveloper(repo, runner, queue).execute(story_id)


@app.task(name="run_tester", bind=True, max_retries=0, queue="ready-to-test")
def task_tester(self, project_path: str, story_id: str) -> None:
    repo, runner, queue, notifier = _deps(project_path)
    RunTester(repo, runner, queue).execute(story_id)


@app.task(name="run_atf", bind=True, max_retries=0, queue="ready-to-atf")
def task_atf(self, project_path: str, story_id: str) -> None:
    repo, runner, queue, notifier = _deps(project_path)
    RunAtf(repo, runner, queue, notifier).execute(story_id)
