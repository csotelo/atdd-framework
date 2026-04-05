import pytest
from atdd_orchestrator.application.use_cases.run_tester import RunTester
from atdd_orchestrator.domain.story import Status
from tests.stubs import StubStoryRepository, StubCodeRunner, StubTaskQueue, make_story

STORY_ID = "US02-signup"


@pytest.fixture
def repo():
    return StubStoryRepository({STORY_ID: make_story("US02", Status.READY_TO_TEST)})


@pytest.fixture
def queue():
    return StubTaskQueue()


def test_calls_runner_with_correct_role(repo, queue):
    runner = StubCodeRunner()
    RunTester(repo, runner, queue).execute(STORY_ID)
    role, _ = runner.calls[0]
    assert role == "tester"


def test_prompt_includes_story_id(repo, queue):
    runner = StubCodeRunner()
    RunTester(repo, runner, queue).execute(STORY_ID)
    _, prompt = runner.calls[0]
    assert STORY_ID in prompt


def test_on_success_saves_ready_to_atf(repo, queue):
    RunTester(repo, StubCodeRunner(), queue).execute(STORY_ID)
    assert any(st == Status.READY_TO_ATF for _, st, _ in repo.saved)


def test_on_success_enqueues_run_atf(repo, queue):
    RunTester(repo, StubCodeRunner(), queue).execute(STORY_ID)
    assert ("run_atf", STORY_ID) in queue.enqueued


def test_on_failure_routes_back_to_developer(repo, queue):
    RunTester(repo, StubCodeRunner(raises=RuntimeError("tests fallaron")), queue).execute(STORY_ID)
    assert any(st == Status.READY_TO_DEV for _, st, _ in repo.saved)
    assert ("run_developer", STORY_ID) in queue.enqueued


def test_on_failure_does_not_reraise(repo, queue):
    """El tester absorbe el error y re-enruta — no rompe el pipeline."""
    RunTester(repo, StubCodeRunner(raises=RuntimeError("tests fallaron")), queue).execute(STORY_ID)
