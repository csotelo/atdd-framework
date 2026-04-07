"""
Git adapter — local repository operations.

Single responsibilities:
  - configure commit identity
  - pull --rebase
  - detect pending changes
  - auto-commit + push status changes
"""
import logging
import subprocess

from atdd_orchestrator.config import GIT_USER_NAME, GIT_USER_EMAIL

log = logging.getLogger(__name__)


def _run(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def configure(project_path: str) -> None:
    _run(["config", "user.name",  GIT_USER_NAME],  cwd=project_path)
    _run(["config", "user.email", GIT_USER_EMAIL], cwd=project_path)


def pull(project_path: str) -> None:
    result = _run(["pull", "--rebase", "--autostash"], cwd=project_path)
    if result.returncode != 0:
        log.warning("git pull failed in %s: %s", project_path, result.stderr.strip())


def has_changes(project_path: str) -> bool:
    result = _run(["status", "--porcelain"], cwd=project_path)
    return bool(result.stdout.strip())


def commit_and_push(project_path: str) -> None:
    _run(["add", "-A"], cwd=project_path)
    result = _run(
        ["commit", "-m", "chore(atdd): automatic status update"],
        cwd=project_path,
    )
    if result.returncode != 0:
        log.warning("git commit failed in %s: %s", project_path, result.stderr.strip())
        return
    push = _run(["push"], cwd=project_path)
    if push.returncode != 0:
        log.warning("git push failed in %s: %s", project_path, push.stderr.strip())
    else:
        log.info("git push OK — %s", project_path)
