import pytest
from pathlib import Path
import frontmatter

from atdd_orchestrator.infrastructure.frontmatter_repo import FrontmatterStoryRepository
from atdd_orchestrator.domain.story import Status


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Temporary project with one story in the backlog."""
    backlog = tmp_path / ".atdd" / "backlog" / "US01-login"
    backlog.mkdir(parents=True)
    story = backlog / "story.md"
    story.write_text(
        "---\nid: US01\ntitle: Login\nstatus: inbox\nsprint: sprint_01\n---\nDescription.\n"
    )
    return tmp_path


def test_get_returns_story_with_correct_fields(project):
    repo = FrontmatterStoryRepository(str(project))
    story = repo.get("US01-login")
    assert story.id == "US01"
    assert story.title == "Login"
    assert story.status == Status.INBOX
    assert story.sprint == "sprint_01"
    assert story.blocked_reason is None


def test_save_status_updates_frontmatter_on_disk(project):
    repo = FrontmatterStoryRepository(str(project))
    repo.save_status("US01-login", Status.READY_TO_DEV)
    post = frontmatter.load(project / ".atdd" / "backlog" / "US01-login" / "story.md")
    assert post["status"] == "in-progress:ready-to-dev"


def test_save_status_with_note_writes_blocked_reason(project):
    repo = FrontmatterStoryRepository(str(project))
    repo.save_status("US01-login", Status.BLOCKED, note="opencode timeout")
    post = frontmatter.load(project / ".atdd" / "backlog" / "US01-login" / "story.md")
    assert post["status"] == "blocked"
    assert post["blocked_reason"] == "timeout en opencode"


def test_save_status_clears_blocked_reason_when_note_empty(project):
    repo = FrontmatterStoryRepository(str(project))
    repo.save_status("US01-login", Status.BLOCKED, note="something failed")
    repo.save_status("US01-login", Status.READY_TO_DEV)
    post = frontmatter.load(project / ".atdd" / "backlog" / "US01-login" / "story.md")
    assert "blocked_reason" not in post.metadata


def test_find_by_status_returns_matching_story_ids(project):
    repo = FrontmatterStoryRepository(str(project))
    result = repo.find_by_status(Status.INBOX)
    assert result == ["US01-login"]


def test_find_by_status_returns_empty_when_no_match(project):
    repo = FrontmatterStoryRepository(str(project))
    result = repo.find_by_status(Status.DONE)
    assert result == []


def test_find_by_status_returns_empty_when_backlog_missing(tmp_path):
    repo = FrontmatterStoryRepository(str(tmp_path))
    assert repo.find_by_status(Status.INBOX) == []


def test_find_by_status_returns_multiple_stories(project):
    backlog = project / ".atdd" / "backlog"
    story2 = backlog / "US02-signup"
    story2.mkdir()
    (story2 / "story.md").write_text(
        "---\nid: US02\ntitle: Signup\nstatus: inbox\nsprint: sprint_01\n---\n"
    )
    repo = FrontmatterStoryRepository(str(project))
    result = repo.find_by_status(Status.INBOX)
    assert sorted(result) == ["US01-login", "US02-signup"]
