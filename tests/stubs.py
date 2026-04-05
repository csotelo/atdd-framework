"""Implementaciones stub de los puertos para tests. Sin dependencias externas."""
from atdd_orchestrator.domain.ports import StoryRepository, CodeRunner, TaskQueue, Notifier
from atdd_orchestrator.domain.story import Status, Story


class StubStoryRepository(StoryRepository):
    def __init__(self, stories: dict[str, Story] | None = None) -> None:
        self._stories: dict[str, Story] = stories or {}
        self.saved: list[tuple[str, Status, str]] = []

    def get(self, story_id: str) -> Story:
        # Refleja el último status guardado si existe
        for sid, status, _ in reversed(self.saved):
            if sid == story_id:
                original = self._stories[story_id]
                return Story(
                    id=original.id,
                    title=original.title,
                    status=status,
                    sprint=original.sprint,
                )
        return self._stories[story_id]

    def save_status(self, story_id: str, status: Status, note: str = "") -> None:
        self.saved.append((story_id, status, note))

    def find_by_status(self, status: Status) -> list[str]:
        return [sid for sid, story in self._stories.items() if story.status == status]


class StubCodeRunner(CodeRunner):
    def __init__(self, raises: Exception | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self._raises = raises

    def run(self, role: str, prompt: str) -> None:
        self.calls.append((role, prompt))
        if self._raises:
            raise self._raises


class StubTaskQueue(TaskQueue):
    def __init__(self) -> None:
        self.enqueued: list[tuple[str, str]] = []

    def enqueue(self, task_name: str, story_id: str) -> None:
        self.enqueued.append((task_name, story_id))


class StubNotifier(Notifier):
    def __init__(self) -> None:
        self.started: list[Story] = []
        self.done: list[Story] = []

    def pipeline_started(self, story: Story) -> None:
        self.started.append(story)

    def story_done(self, story: Story) -> None:
        self.done.append(story)


def make_story(story_id: str, status: Status) -> Story:
    return Story(id=story_id, title="Test Story", status=status, sprint="sprint_01")
