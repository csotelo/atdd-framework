import pytest
from atdd_orchestrator.application.use_cases.run_developer import RunDeveloper
from atdd_orchestrator.domain.story import Status
from tests.stubs import StubStoryRepository, StubCodeRunner, StubTaskQueue, make_story

STORY_ID = "US01-login"


@pytest.fixture
def repo():
    return StubStoryRepository({STORY_ID: make_story("US01", Status.READY_TO_DEV)})


@pytest.fixture
def queue():
    return StubTaskQueue()


def test_calls_runner_with_correct_role(repo, queue):
    runner = StubCodeRunner()
    RunDeveloper(repo, runner, queue).execute(STORY_ID)
    role, _ = runner.calls[0]
    assert role == "developer"


def test_prompt_includes_story_id(repo, queue):
    runner = StubCodeRunner()
    RunDeveloper(repo, runner, queue).execute(STORY_ID)
    _, prompt = runner.calls[0]
    assert STORY_ID in prompt


def test_on_success_saves_ready_to_test(repo, queue):
    RunDeveloper(repo, StubCodeRunner(), queue).execute(STORY_ID)
    assert any(st == Status.READY_TO_TEST for _, st, _ in repo.saved)


def test_on_success_enqueues_run_tester(repo, queue):
    RunDeveloper(repo, StubCodeRunner(), queue).execute(STORY_ID)
    assert ("run_tester", STORY_ID) in queue.enqueued


def test_on_runner_failure_sets_blocked_and_reraises(repo, queue):
    with pytest.raises(RuntimeError):
        RunDeveloper(repo, StubCodeRunner(raises=RuntimeError("timeout")), queue).execute(STORY_ID)
    blocked = [(sid, st, note) for sid, st, note in repo.saved if st == Status.BLOCKED]
    assert len(blocked) == 1
    assert "timeout" in blocked[0][2]
