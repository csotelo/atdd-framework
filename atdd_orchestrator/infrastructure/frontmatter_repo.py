from pathlib import Path

import frontmatter

from atdd_orchestrator.domain.ports import StoryRepository
from atdd_orchestrator.domain.story import Status, Story


class FrontmatterStoryRepository(StoryRepository):
    def __init__(self, project_path: str) -> None:
        self._backlog = Path(project_path) / ".atdd" / "backlog"

    def _story_file(self, story_id: str) -> Path:
        return self._backlog / story_id / "story.md"

    def get(self, story_id: str) -> Story:
        post = frontmatter.load(self._story_file(story_id))
        return Story(
            id=post["id"],
            title=post["title"],
            status=Status(post["status"]),
            sprint=post["sprint"],
            blocked_reason=post.metadata.get("blocked_reason"),
        )

    def save_status(self, story_id: str, status: Status, note: str = "") -> None:
        path = self._story_file(story_id)
        post = frontmatter.load(path)
        post["status"] = status.value
        if note:
            post["blocked_reason"] = note
        elif "blocked_reason" in post.metadata:
            del post["blocked_reason"]
        path.write_text(frontmatter.dumps(post))

    def find_by_status(self, status: Status) -> list[str]:
        if not self._backlog.exists():
            return []
        result = []
        for story_dir in sorted(self._backlog.iterdir()):
            sf = story_dir / "story.md"
            if not sf.exists():
                continue
            post = frontmatter.load(sf)
            if post.get("status") == status.value:
                result.append(story_dir.name)
        return result
