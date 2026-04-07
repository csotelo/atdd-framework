"""
LangGraph pipeline nodes.

Each node calls the corresponding use case passing a GraphRoutedQueue
(the graph handles routing, not the queue). After execution, reads
the current status from the repo to update the graph state.
"""
import logging

from atdd_orchestrator.domain.ports import TaskQueue
from atdd_orchestrator.domain.story import Status
from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository
from atdd_orchestrator.infrastructure.opencode_runner import OpenCodeRunner
from atdd_orchestrator.infrastructure.notifier import TelegramNotifier
from atdd_orchestrator.application.use_cases.run_test_engineer import RunTestEngineer
from atdd_orchestrator.application.use_cases.run_developer import RunDeveloper
from atdd_orchestrator.application.use_cases.run_tester import RunTester
from atdd_orchestrator.application.use_cases.run_atf import RunAtf
from .state import PipelineState

log = logging.getLogger(__name__)


class GraphRoutedQueue(TaskQueue):
    """No-effect queue — the LangGraph state machine handles routing between nodes.

    Use cases call queue.enqueue() at the end of each step; in the LangGraph
    model that call is intentionally ignored because the graph decides the next
    node by reading the story status from the repository.
    """

    def enqueue(self, task_name: str, story_id: str) -> None:
        pass


def _deps(project_path: str):
    repo = FrontmatterStoryRepository(project_path)
    runner = OpenCodeRunner(project_path)
    notifier = TelegramNotifier()
    queue = GraphRoutedQueue()
    return repo, runner, notifier, queue


def _read_status(project_path: str, story_id: str) -> tuple[Status, str]:
    repo = FrontmatterStoryRepository(project_path)
    story = repo.get(story_id)
    return story.status, story.blocked_reason or ""


# ---------------------------------------------------------------------------
# Nodos
# ---------------------------------------------------------------------------

def test_engineer_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[test_engineer] story=%s", story_id)

    repo, runner, notifier, queue = _deps(project_path)
    try:
        RunTestEngineer(repo, runner, queue, notifier).execute(story_id)
    except Exception:
        pass  # use case already saved BLOCKED to the repo

    status, reason = _read_status(project_path, story_id)
    return {**state, "status": status, "blocked_reason": reason}


def developer_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[developer] story=%s retry=%d", story_id, state["dev_retries"])

    repo, runner, notifier, queue = _deps(project_path)
    try:
        RunDeveloper(repo, runner, queue).execute(story_id)
    except Exception:
        pass  # use case already saved BLOCKED to the repo

    status, reason = _read_status(project_path, story_id)
    return {**state, "status": status, "blocked_reason": reason}


def tester_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[tester] story=%s", story_id)

    repo, runner, notifier, queue = _deps(project_path)
    # RunTester catches its own exception and saves READY_TO_DEV on failure
    RunTester(repo, runner, queue).execute(story_id)

    status, reason = _read_status(project_path, story_id)
    # If tester failed and returned to READY_TO_DEV, increment retry counter
    dev_retries = state["dev_retries"]
    if status == Status.READY_TO_DEV:
        dev_retries += 1
    return {**state, "status": status, "blocked_reason": reason, "dev_retries": dev_retries}


def atf_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[atf] story=%s", story_id)

    repo, runner, notifier, queue = _deps(project_path)
    # RunAtf catches its own exception and saves READY_TO_DEV on failure
    RunAtf(repo, runner, queue, notifier).execute(story_id)

    status, reason = _read_status(project_path, story_id)
    dev_retries = state["dev_retries"]
    if status == Status.READY_TO_DEV:
        dev_retries += 1
    return {**state, "status": status, "blocked_reason": reason, "dev_retries": dev_retries}
