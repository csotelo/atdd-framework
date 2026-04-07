from atdd_orchestrator.domain.ports import StoryRepository, CodeRunner, TaskQueue
from atdd_orchestrator.domain.story import Status

_PROMPT = (
    "Act as /atdd_developer. "
    "Story {story_id} has status: in-progress:ready-to-dev. "
    "Read prompt.md and write the implementation to make the tests pass (GREEN)."
)


class RunDeveloper:
    def __init__(
        self,
        story_repo: StoryRepository,
        runner: CodeRunner,
        queue: TaskQueue,
    ) -> None:
        self._repo = story_repo
        self._runner = runner
        self._queue = queue

    def execute(self, story_id: str) -> None:
        try:
            self._runner.run("developer", _PROMPT.format(story_id=story_id))
            self._repo.save_status(story_id, Status.READY_TO_TEST)
            self._queue.enqueue("run_tester", story_id)
        except Exception as exc:
            self._repo.save_status(story_id, Status.BLOCKED, note=str(exc))
            raise
