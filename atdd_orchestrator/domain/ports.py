from abc import ABC, abstractmethod
from atdd_orchestrator.domain.story import Story, Status


class StoryRepository(ABC):
    @abstractmethod
    def get(self, story_id: str) -> Story: ...

    @abstractmethod
    def save_status(self, story_id: str, status: Status, note: str = "") -> None: ...

    @abstractmethod
    def find_by_status(self, status: Status) -> list[str]: ...


class CodeRunner(ABC):
    @abstractmethod
    def run(self, role: str, prompt: str) -> None: ...


class TaskQueue(ABC):
    """Inter-worker task queue (used by the Celery engine)."""
    @abstractmethod
    def enqueue(self, task_name: str, story_id: str) -> None: ...


class PipelineExecutor(ABC):
    """Starts the full pipeline for a story in INBOX.

    Each engine (Celery, LangGraph) provides its own implementation.
    The entry point depends on this port, not on a concrete engine.
    """
    @abstractmethod
    def submit(self, story_id: str) -> None: ...


class Notifier(ABC):
    @abstractmethod
    def pipeline_started(self, story: Story) -> None: ...

    @abstractmethod
    def story_done(self, story: Story) -> None: ...
