import pytest
from atdd_orchestrator.application.use_cases.run_atf import RunAtf
from atdd_orchestrator.domain.story import Status
from tests.stubs import StubStoryRepository, StubCodeRunner, StubTaskQueue, StubNotifier, make_story

STORY_ID = "US03-checkout"


@pytest.fixture
def repo():
    return StubStoryRepository({STORY_ID: make_story("US03", Status.READY_TO_ATF)})


@pytest.fixture
def queue():
    return StubTaskQueue()


@pytest.fixture
def notifier():
    return StubNotifier()


def test_calls_runner_with_correct_role(repo, queue, notifier):
    runner = StubCodeRunner()
    RunAtf(repo, runner, queue, notifier).execute(STORY_ID)
    role, _ = runner.calls[0]
    assert role == "atf"


def test_prompt_includes_story_id(repo, queue, notifier):
    runner = StubCodeRunner()
    RunAtf(repo, runner, queue, notifier).execute(STORY_ID)
    _, prompt = runner.calls[0]
    assert STORY_ID in prompt


def test_on_success_saves_done(repo, queue, notifier):
    RunAtf(repo, StubCodeRunner(), queue, notifier).execute(STORY_ID)
    assert any(st == Status.DONE for _, st, _ in repo.saved)


def test_on_success_notifica_story_done(repo, queue, notifier):
    RunAtf(repo, StubCodeRunner(), queue, notifier).execute(STORY_ID)
    assert len(notifier.done) == 1


def test_on_failure_routes_back_to_developer(repo, queue, notifier):
    RunAtf(repo, StubCodeRunner(raises=RuntimeError("scenario failed")), queue, notifier).execute(STORY_ID)
    assert any(st == Status.READY_TO_DEV for _, st, _ in repo.saved)
    assert ("run_developer", STORY_ID) in queue.enqueued


def test_on_failure_does_not_reraise(repo, queue, notifier):
    """El ATF absorbe el error y re-enruta — no rompe el pipeline."""
    RunAtf(repo, StubCodeRunner(raises=RuntimeError("scenario failed")), queue, notifier).execute(STORY_ID)
