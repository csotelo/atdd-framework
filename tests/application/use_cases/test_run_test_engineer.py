import pytest
from atdd_orchestrator.application.use_cases.run_test_engineer import RunTestEngineer
from atdd_orchestrator.domain.story import Status
from tests.stubs import StubStoryRepository, StubCodeRunner, StubTaskQueue, StubNotifier, make_story

STORY_ID = "US01-login"


@pytest.fixture
def repo():
    return StubStoryRepository({STORY_ID: make_story("US01", Status.INBOX)})


@pytest.fixture
def queue():
    return StubTaskQueue()


@pytest.fixture
def notifier():
    return StubNotifier()


def test_notifica_pipeline_started(repo, queue, notifier):
    RunTestEngineer(repo, StubCodeRunner(), queue, notifier).execute(STORY_ID)
    assert len(notifier.started) == 1
    assert notifier.started[0].id == "US01"


def test_calls_runner_with_correct_role(repo, queue, notifier):
    runner = StubCodeRunner()
    RunTestEngineer(repo, runner, queue, notifier).execute(STORY_ID)
    role, _ = runner.calls[0]
    assert role == "test_engineer"


def test_prompt_includes_story_id(repo, queue, notifier):
    runner = StubCodeRunner()
    RunTestEngineer(repo, runner, queue, notifier).execute(STORY_ID)
    _, prompt = runner.calls[0]
    assert STORY_ID in prompt


def test_on_success_saves_ready_to_dev(repo, queue, notifier):
    RunTestEngineer(repo, StubCodeRunner(), queue, notifier).execute(STORY_ID)
    assert any(st == Status.READY_TO_DEV for _, st, _ in repo.saved)


def test_on_success_enqueues_run_developer(repo, queue, notifier):
    RunTestEngineer(repo, StubCodeRunner(), queue, notifier).execute(STORY_ID)
    assert ("run_developer", STORY_ID) in queue.enqueued


def test_on_runner_failure_sets_blocked_and_reraises(repo, queue, notifier):
    error = RuntimeError("opencode crashed")
    with pytest.raises(RuntimeError):
        RunTestEngineer(repo, StubCodeRunner(raises=error), queue, notifier).execute(STORY_ID)
    blocked = [(sid, st, note) for sid, st, note in repo.saved if st == Status.BLOCKED]
    assert len(blocked) == 1
    assert "opencode crashed" in blocked[0][2]
