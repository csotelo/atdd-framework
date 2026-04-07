from typing import TypedDict, Optional
from atdd_orchestrator.domain.story import Status


class PipelineState(TypedDict):
    story_id: str
    project_path: str
    status: Status
    blocked_reason: Optional[str]
    dev_retries: int  # number of times developer retried after tester/atf failure
