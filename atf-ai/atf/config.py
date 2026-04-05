"""Configuration management for ATF."""

from pathlib import Path
from typing import Any

import orjson


def get_config_path() -> Path:
    """Return path to atf.config.json."""
    return Path.cwd() / "atf.config.json"


def get_default_config() -> dict[str, Any]:
    """Return default configuration dictionary."""
    return {
        "baseURL": "http://localhost:3000",
        "promptsDir": "prompts",
        "reportsDir": "reports",
        "stateFile": "atf-state.json",
        "headless": True,
        "timeout": 30000,
        "retries": 1,
        "screenshots": "only-on-failure",
        "docker": {
            "image": "mcr.microsoft.com/playwright/python:latest",
            "pull_policy": "if-not-present",
        },
    }


def write_default_config() -> None:
    """Write default configuration to atf.config.json."""
    config_path = get_config_path()
    config_data = orjson.dumps(get_default_config(), option=orjson.OPT_INDENT_2)
    config_path.write_bytes(config_data)


def load_config() -> dict[str, Any]:
    """Load configuration from atf.config.json."""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    data = orjson.loads(config_path.read_bytes())
    return data  # type: ignore[no-any-return]
