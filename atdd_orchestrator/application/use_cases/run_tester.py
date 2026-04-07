from atdd_orchestrator.domain.ports import StoryRepository, CodeRunner, TaskQueue
from atdd_orchestrator.domain.story import Status

_PROMPT = (
    "Act as /atdd_tester. "
    "Story {story_id} has status: in-progress:ready-to-test. "
    "Run unit, integration, and smoke tests. "
    "If all pass: success (exit 0). "
    "If any fail: failure (exit 1)."
)


class RunTester:
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
            self._runner.run("tester", _PROMPT.format(story_id=story_id))
            self._repo.save_status(story_id, Status.READY_TO_ATF)
            self._queue.enqueue("run_atf", story_id)
        except Exception as exc:
            # Tests failed → return to developer
            self._repo.save_status(story_id, Status.READY_TO_DEV, note=str(exc))
            self._queue.enqueue("run_developer", story_id)
