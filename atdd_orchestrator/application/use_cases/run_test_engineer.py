from atdd_orchestrator.domain.ports import StoryRepository, CodeRunner, TaskQueue, Notifier
from atdd_orchestrator.domain.story import Status

_PROMPT = (
    "Act as /atdd_test_engineer. "
    "Story {story_id} has status: inbox. "
    "Write the tests in RED following the ATDD process."
)


class RunTestEngineer:
    def __init__(
        self,
        story_repo: StoryRepository,
        runner: CodeRunner,
        queue: TaskQueue,
        notifier: Notifier,
    ) -> None:
        self._repo = story_repo
        self._runner = runner
        self._queue = queue
        self._notifier = notifier

    def execute(self, story_id: str) -> None:
        story = self._repo.get(story_id)
        self._notifier.pipeline_started(story)
        try:
            self._runner.run("test_engineer", _PROMPT.format(story_id=story_id))
            self._repo.save_status(story_id, Status.READY_TO_DEV)
            self._queue.enqueue("run_developer", story_id)
        except Exception as exc:
            self._repo.save_status(story_id, Status.BLOCKED, note=str(exc))
            raise
