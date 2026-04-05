import pytest
from atdd_orchestrator.application.use_cases.dispatch import DispatchStories
from atdd_orchestrator.domain.story import Status
from tests.stubs import StubStoryRepository, StubTaskQueue, make_story


@pytest.fixture
def queue() -> StubTaskQueue:
    return StubTaskQueue()


def test_inbox_story_dispatches_test_engineer(queue):
    repo = StubStoryRepository({"US01-login": make_story("US01", Status.INBOX)})
    DispatchStories(repo, queue).execute()
    assert ("run_test_engineer", "US01-login") in queue.enqueued


def test_no_actionable_stories_enqueues_nothing(queue):
    repo = StubStoryRepository({
        "US01-login":  make_story("US01", Status.DRAFT),
        "US02-signup": make_story("US02", Status.DONE),
        "US03-logout": make_story("US03", Status.BLOCKED),
    })
    DispatchStories(repo, queue).execute()
    assert queue.enqueued == []


def test_multiple_inbox_stories_all_enqueued(queue):
    repo = StubStoryRepository({
        "US01-login":  make_story("US01", Status.INBOX),
        "US02-signup": make_story("US02", Status.INBOX),
    })
    DispatchStories(repo, queue).execute()
    assert len(queue.enqueued) == 2
    assert all(t == "run_test_engineer" for t, _ in queue.enqueued)


def test_ready_to_dev_not_dispatched_by_git_sync(queue):
    """Las historias en estados intermedios son manejadas por los workers, no por git-sync."""
    repo = StubStoryRepository({
        "US01-login": make_story("US01", Status.READY_TO_DEV),
    })
    DispatchStories(repo, queue).execute()
    assert queue.enqueued == []
