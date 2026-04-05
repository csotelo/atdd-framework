from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Status(str, Enum):
    # Estados operacionales del pipeline
    INBOX         = "inbox"
    READY_TO_DEV  = "in-progress:ready-to-dev"
    READY_TO_TEST = "in-progress:ready-to-test"
    READY_TO_ATF  = "in-progress:ready-to-atf"
    DONE          = "done"
    BLOCKED       = "blocked"

    # Estados legacy (migración / compatibilidad backlog)
    DRAFT         = "draft"
    UNVERIFIED    = "unverified"
    DAMAGED       = "damaged"
    UNKNOWN       = "unknown"
    ACCEPTED      = "accepted"


@dataclass(frozen=True)
class Story:
    id: str
    title: str
    status: Status
    sprint: str
    blocked_reason: Optional[str] = None
