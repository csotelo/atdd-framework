"""Fixtures management for ATF."""

import os
import subprocess
from pathlib import Path
from typing import Any


def build_fixture_env() -> dict[str, Any]:
    """Build environment variables for fixture execution."""
    config_path = Path.cwd() / "atf.config.json"
    if not config_path.exists():
        return {}

    import orjson

    config = orjson.loads(config_path.read_bytes())

    env = {
        "ATF_BASE_URL": config.get("baseURL", "http://localhost:3000"),
        "ATF_TIMEOUT": str(config.get("timeout", 30000)),
        "ATF_HEADLESS": "1" if config.get("headless", True) else "0",
    }

    return env


def run_fixtures_if_present() -> int:
    """Run fixtures if fixtures.py exists in project root."""
    fixtures_path = Path.cwd() / "fixtures.py"

    if not fixtures_path.exists():
        return 0

    import click

    click.echo("Running fixtures...")

    env = build_fixture_env()
    merged_env = {**os.environ, **env}

    try:
        result = subprocess.run(
            ["python", str(fixtures_path)],
            capture_output=True,
            text=True,
            env=merged_env,
        )

        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)

        return result.returncode
    except Exception as e:
        click.echo(f"Error running fixtures: {e}", err=True)
        return 1
