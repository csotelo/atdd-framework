"""State management for ATF."""

from pathlib import Path
from typing import Any

import orjson


def get_state_path() -> Path:
    """Return path to atf-state.json."""
    return Path.cwd() / "atf-state.json"


def load_state() -> dict[str, Any]:
    """Load state from atf-state.json."""
    state_path = get_state_path()
    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")
    data = orjson.loads(state_path.read_bytes())
    return data  # type: ignore[no-any-return]


def save_state(state: dict[str, Any]) -> None:
    """Save state to atf-state.json."""
    state_path = get_state_path()
    data = orjson.dumps(state, option=orjson.OPT_INDENT_2)
    state_path.write_bytes(data)
