import pytest
from atdd_orchestrator.domain.story import Status, Story


def test_status_values_match_frontmatter_strings():
    assert Status.INBOX.value          == "inbox"
    assert Status.READY_TO_DEV.value   == "in-progress:ready-to-dev"
    assert Status.READY_TO_TEST.value  == "in-progress:ready-to-test"
    assert Status.READY_TO_ATF.value   == "in-progress:ready-to-atf"
    assert Status.DONE.value           == "done"
    assert Status.BLOCKED.value        == "blocked"


def test_status_from_string():
    assert Status("inbox")                    == Status.INBOX
    assert Status("in-progress:ready-to-dev") == Status.READY_TO_DEV
    assert Status("done")                     == Status.DONE


def test_story_is_immutable():
    story = Story(id="US01", title="Login", status=Status.INBOX, sprint="sprint_01")
    with pytest.raises(Exception):
        story.status = Status.DONE  # type: ignore[misc]


def test_story_blocked_reason_defaults_to_none():
    story = Story(id="US01", title="Login", status=Status.INBOX, sprint="sprint_01")
    assert story.blocked_reason is None
