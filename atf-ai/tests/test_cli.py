"""Tests for ATF CLI."""

import subprocess
import sys
from pathlib import Path


def test_help_shows_all_commands() -> None:
    """Test that atf --help shows all commands."""
    result = subprocess.run(
        [sys.executable, "-m", "atf.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "init" in result.stdout
    assert "run" in result.stdout
    assert "status" in result.stdout


def test_init_creates_config(tmp_path: Path) -> None:
    """Test that atf init creates config files."""
    result = subprocess.run(
        [sys.executable, "-m", "atf.cli", "init"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert (tmp_path / "atf.config.json").exists()
    assert (tmp_path / "behave.ini").exists()


def test_run_sprint_calls_docker(tmp_path: Path) -> None:
    """Test that atf run --sprint runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "atf.cli", "run", "--sprint", "sprint_02"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
