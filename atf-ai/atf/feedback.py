"""Feedback generation for ATF."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson


def extract_failures(results_data: Any) -> list[dict[str, Any]]:
    """Extract failure details from behave JSON results."""
    failures = []

    if isinstance(results_data, list):
        features = results_data
    else:
        features = results_data.get("scenarios", [])

    for feature in features:
        for element in feature.get("elements", []):
            if element.get("type") != "scenario":
                continue
            if element.get("status") != "failed":
                continue

            scenario_name = element.get("name", "Unknown")
            for step in element.get("steps", []):
                result = step.get("result", {})
                if result.get("status") == "failed":
                    failures.append(
                        {
                            "scenario": scenario_name,
                            "step": f"{step.get('keyword', '')} {step.get('name', '')}",
                            "error": result.get("error_message", ""),
                        }
                    )

    return failures


def write_feedback(sprint_name: str) -> bool:
    """Write feedback.md for a failed sprint run.

    Returns True if feedback was written, False if no failures found.
    """
    config_path = Path.cwd() / "atf.config.json"
    if config_path.exists():
        config = orjson.loads(config_path.read_bytes())
        reports_dir = Path.cwd() / config.get("reportsDir", "reports")
    else:
        reports_dir = Path.cwd() / "reports"

    results_file = reports_dir / sprint_name / "results.json"
    if not results_file.exists():
        return False

    try:
        results_data = orjson.loads(results_file.read_bytes())
    except (orjson.JSONDecodeError, json.JSONDecodeError):
        return False

    failures = extract_failures(results_data)
    if not failures:
        return False

    feedback_path = Path.cwd() / "prompts" / sprint_name / "feedback.md"
    feedback_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        f"# Feedback for {sprint_name}",
        "",
        f"Timestamp: {timestamp}",
        "",
    ]

    for i, failure in enumerate(failures, 1):
        lines.append(f"## Failed Scenario {i}")
        lines.append("")
        lines.append(f"Scenario: {failure['scenario']}")
        lines.append(f"Step: {failure['step']}")
        lines.append(f"Error: {failure['error']}")
        lines.append("Screenshot: N/A")
        lines.append("")

    lines.append("## All Failures")
    lines.append("")
    for i, failure in enumerate(failures, 1):
        lines.append(f"{i}. {failure['scenario']} — {failure['step']}")

    lines.append("")
    feedback_path.write_text("\n".join(lines))

    return True
