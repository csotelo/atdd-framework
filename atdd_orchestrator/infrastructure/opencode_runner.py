import subprocess

from atdd_orchestrator.domain.ports import CodeRunner
from atdd_orchestrator.config import OPENCODE_BIN, TIMEOUTS


class OpenCodeRunner(CodeRunner):
    def __init__(self, project_path: str) -> None:
        self._project_path = project_path

    def run(self, role: str, prompt: str) -> None:
        timeout = TIMEOUTS.get(role, 1800)
        subprocess.run(
            [OPENCODE_BIN, "run", prompt],
            cwd=self._project_path,
            timeout=timeout,
            check=True,
        )
