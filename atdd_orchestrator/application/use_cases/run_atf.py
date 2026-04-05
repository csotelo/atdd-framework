from atdd_orchestrator.domain.ports import StoryRepository, CodeRunner, TaskQueue, Notifier
from atdd_orchestrator.domain.story import Status

_PROMPT = (
    "Actúa como /atdd_tester en modo aceptación. "
    "La historia {story_id} tiene status: in-progress:ready-to-atf. "
    "Corre el acceptance.feature con Behave/Playwright. "
    "Si todos los scenarios pasan: éxito (exit 0). "
    "Si alguno falla: falla (exit 1)."
)


class RunAtf:
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
        try:
            self._runner.run("atf", _PROMPT.format(story_id=story_id))
            self._repo.save_status(story_id, Status.DONE)
            story = self._repo.get(story_id)
            self._notifier.story_done(story)
        except Exception as exc:
            # Acceptance tests fallaron → devolver al developer
            self._repo.save_status(story_id, Status.READY_TO_DEV, note=str(exc))
            self._queue.enqueue("run_developer", story_id)
