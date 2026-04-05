from atdd_orchestrator.domain.ports import StoryRepository, TaskQueue
from atdd_orchestrator.domain.story import Status

# git-sync llama este use case para encolar historias recién marcadas como inbox
TRANSITIONS: dict[Status, str] = {
    Status.INBOX: "run_test_engineer",
}


class DispatchStories:
    def __init__(self, story_repo: StoryRepository, queue: TaskQueue) -> None:
        self._repo = story_repo
        self._queue = queue

    def execute(self) -> None:
        for status, task_name in TRANSITIONS.items():
            for story_id in self._repo.find_by_status(status):
                self._queue.enqueue(task_name, story_id)
