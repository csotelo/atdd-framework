from atdd_orchestrator.domain.ports import StoryRepository, PipelineExecutor
from atdd_orchestrator.domain.story import Status


class DispatchStories:
    """Detecta historias en INBOX y las envía al pipeline configurado."""

    def __init__(self, story_repo: StoryRepository, executor: PipelineExecutor) -> None:
        self._repo = story_repo
        self._executor = executor

    def execute(self) -> None:
        for story_id in self._repo.find_by_status(Status.INBOX):
            self._executor.submit(story_id)
