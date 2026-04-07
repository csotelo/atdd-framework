"""
Nodos del grafo LangGraph.

Cada nodo llama al use case correspondiente pasándole un NoOpQueue
(el grafo maneja el routing, no la cola). Después de ejecutar, lee
el status actual del repo para actualizar el estado del grafo.
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
    """Cola sin efecto — el grafo LangGraph maneja el routing entre nodos.

    Los use cases llaman queue.enqueue() al finalizar cada paso; en el
    modelo LangGraph esa llamada es intencionalmente ignorada porque el
    grafo decide el siguiente nodo leyendo el status del repositorio.
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
    log.info("[test_engineer] historia=%s", story_id)

    repo, runner, notifier, queue = _deps(project_path)
    try:
        RunTestEngineer(repo, runner, queue, notifier).execute(story_id)
    except Exception:
        pass  # use case ya guardó BLOCKED en el repo

    status, reason = _read_status(project_path, story_id)
    return {**state, "status": status, "blocked_reason": reason}


def developer_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[developer] historia=%s retry=%d", story_id, state["dev_retries"])

    repo, runner, notifier, queue = _deps(project_path)
    try:
        RunDeveloper(repo, runner, queue).execute(story_id)
    except Exception:
        pass  # use case ya guardó BLOCKED en el repo

    status, reason = _read_status(project_path, story_id)
    return {**state, "status": status, "blocked_reason": reason}


def tester_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[tester] historia=%s", story_id)

    repo, runner, notifier, queue = _deps(project_path)
    # RunTester captura su propia excepción y guarda READY_TO_DEV si falla
    RunTester(repo, runner, queue).execute(story_id)

    status, reason = _read_status(project_path, story_id)
    # Si tester falló y volvió a READY_TO_DEV, incrementar retry counter
    dev_retries = state["dev_retries"]
    if status == Status.READY_TO_DEV:
        dev_retries += 1
    return {**state, "status": status, "blocked_reason": reason, "dev_retries": dev_retries}


def atf_node(state: PipelineState) -> PipelineState:
    story_id = state["story_id"]
    project_path = state["project_path"]
    log.info("[atf] historia=%s", story_id)

    repo, runner, notifier, queue = _deps(project_path)
    # RunAtf captura su propia excepción y guarda READY_TO_DEV si falla
    RunAtf(repo, runner, queue, notifier).execute(story_id)

    status, reason = _read_status(project_path, story_id)
    dev_retries = state["dev_retries"]
    if status == Status.READY_TO_DEV:
        dev_retries += 1
    return {**state, "status": status, "blocked_reason": reason, "dev_retries": dev_retries}
