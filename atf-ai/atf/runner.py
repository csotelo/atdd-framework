"""Test runner for ATF - executes tests in Docker container."""

import html as html_lib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
import docker
import docker.errors
import orjson

from atf.config import load_config
from atf.state import load_state, save_state


def get_reports_dir() -> Path:
    """Return path to reports directory."""
    config = load_config()
    reports_dir_name: str = config.get("reportsDir", "reports")
    reports_dir = Path.cwd() / reports_dir_name
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


def get_docker_client() -> docker.DockerClient:
    """Get a Docker client instance."""
    try:
        return docker.from_env()
    except docker.errors.DockerException as e:
        click.echo(f"Docker not available: {e}", err=True)
        raise


def pull_image(client: docker.DockerClient, pull_policy: str) -> None:
    """Pull Docker image based on pull policy."""
    config = load_config()
    docker_config = config.get("docker", {})
    image = docker_config.get("image", "mcr.microsoft.com/playwright/python:latest")

    if pull_policy == "always":
        click.echo(f"Pulling image {image}...")
        client.images.pull(image)
    elif pull_policy == "if-not-present":
        try:
            client.images.get(image)
            click.echo(f"Using cached image {image}")
        except docker.errors.NotFound:
            click.echo(f"Pulling image {image}...")
            client.images.pull(image)
    elif pull_policy == "never":
        try:
            client.images.get(image)
            click.echo(f"Using local image {image}")
        except docker.errors.NotFound:
            raise RuntimeError(f"Image {image} not found locally")


def extract_scenarios(results_data: Any) -> list[dict[str, Any]]:
    """Extract scenario objects from behave JSON output."""
    if isinstance(results_data, list):
        scenarios: list[dict[str, Any]] = []
        for feature in results_data:
            for element in feature.get("elements", []):
                if element.get("type") == "scenario":
                    scenarios.append(element)
        return scenarios
    return results_data.get("scenarios", [])  # type: ignore[no-any-return]


def extract_failures(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract failure details from scenarios."""
    failures = []
    for scenario in scenarios:
        if scenario.get("status") != "failed":
            continue
        for step in scenario.get("steps", []):
            result = step.get("result", {})
            if result.get("status") == "failed":
                failures.append(
                    {
                        "scenario": scenario.get("name", "Unknown"),
                        "step": f"{step.get('keyword', '')} {step.get('name', '')}",
                        "error": result.get("error_message", ""),
                    }
                )
    return failures


def run_sprint(sprint_name: str, feedback: bool = False, retry: bool = False) -> int:
    """Run acceptance tests for a sprint in Docker container."""
    config = load_config()
    docker_config = config.get("docker", {})
    image = docker_config.get("image", "mcr.microsoft.com/playwright/python:latest")
    pull_policy = docker_config.get("pull_policy", "if-not-present")

    client = get_docker_client()
    pull_image(client, pull_policy)

    project_dir = Path.cwd()
    reports_dir = get_reports_dir()
    sprint_report_dir = reports_dir / sprint_name
    sprint_report_dir.mkdir(exist_ok=True)

    feature_path = f"prompts/{sprint_name}/acceptance.feature"

    click.echo(f"Running {feature_path} in Docker container...")

    install_cmd = (
        "pip install behave requests orjson click httpx playwright --quiet && "
        "playwright install chromium && "
        "python -m behave"
    )

    start_time = time.time()
    exit_code = 1

    try:
        container = client.containers.run(
            image,
            f"sh -c '{install_cmd} {feature_path} --format=json --outfile=/app/reports/{sprint_name}/results.json'",
            volumes={
                str(project_dir): {"bind": "/app", "mode": "rw"},
            },
            working_dir="/app",
            detach=False,
            auto_remove=True,
        )
        if isinstance(container, bytes):
            click.echo(container.decode("utf-8", errors="replace"))
        exit_code = 0

    except docker.errors.ContainerError as e:
        if e.stderr:
            stderr_text = (
                e.stderr.decode("utf-8", errors="replace")
                if isinstance(e.stderr, bytes)
                else str(e.stderr)
            )
            click.echo(stderr_text)
        exit_code = e.exit_status
    except Exception as e:
        click.echo(f"Error running container: {e}", err=True)
        exit_code = 1

    duration = time.time() - start_time

    results_file = sprint_report_dir / "results.json"
    if results_file.exists():
        try:
            results_data = orjson.loads(results_file.read_bytes())
        except (orjson.JSONDecodeError, json.JSONDecodeError) as e:
            click.echo(f"Error parsing results: {e}", err=True)
            results_data = []

        scenarios = extract_scenarios(results_data)

        passed = sum(1 for s in scenarios if s.get("status") == "passed")
        failed = sum(1 for s in scenarios if s.get("status") == "failed")
        total = len(scenarios)

        status = "passed" if failed == 0 else "failed"

        generate_html_report(results_data, sprint_report_dir / "index.html")
    else:
        passed = 0
        failed = 0
        total = 0
        scenarios = []
        status = "failed" if exit_code != 0 else "passed"

    update_state(sprint_name, status, duration, passed, failed, total, scenarios)

    click.echo(f"Sprint {sprint_name} completed: {status}")
    click.echo(f"Duration: {duration:.1f}s")
    click.echo(f"Scenarios: {passed} passed, {failed} failed, {total} total")

    return exit_code


def update_state(
    sprint_name: str,
    status: str,
    duration: float,
    passed: int,
    failed: int,
    total: int,
    scenarios: list[dict[str, Any]] | None = None,
) -> None:
    """Update atf-state.json with sprint results."""
    try:
        state = load_state()
        if "sprints" not in state:
            state["sprints"] = {}
    except (FileNotFoundError, KeyError, orjson.JSONDecodeError):
        state = {"project": "", "current_sprint": sprint_name, "sprints": {}}

    if sprint_name not in state["sprints"]:
        state["sprints"][sprint_name] = {
            "status": "pending",
            "last_run": None,
            "duration_seconds": None,
            "scenarios": {"total": 0, "passed": 0, "failed": 0},
            "failures": [],
        }

    failures = extract_failures(scenarios) if scenarios else []

    state["sprints"][sprint_name]["status"] = status
    state["sprints"][sprint_name]["last_run"] = datetime.now(timezone.utc).isoformat()
    state["sprints"][sprint_name]["duration_seconds"] = duration
    state["sprints"][sprint_name]["scenarios"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
    }
    state["sprints"][sprint_name]["failures"] = failures

    save_state(state)
    update_state_md(sprint_name, status)


def update_state_md(sprint_name: str, status: str) -> None:
    """Update STATE.md with sprint status."""
    state_md_path = Path.cwd() / "STATE.md"
    if not state_md_path.exists():
        return

    lines = state_md_path.read_text().split("\n")
    for i, line in enumerate(lines):
        if f"| {sprint_name} |" in line:
            parts = line.split("|")
            for j, part in enumerate(parts):
                stripped = part.strip()
                if stripped in ("pending", "passed", "failed"):
                    parts[j] = f" {status} "
                    break
            lines[i] = "|".join(parts)
            break

    state_md_path.write_text("\n".join(lines))


def generate_html_report(results: Any, output_path: Path) -> None:
    """Generate HTML report from JSON results."""
    html_template = """<!DOCTYPE html>
<html>
<head>
    <title>ATF Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .scenario {{ margin: 10px 0; padding: 10px; border: 1px solid #ccc; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .status {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    {scenarios}
</body>
</html>"""

    scenarios = extract_scenarios(results)

    scenarios_html = ""
    for scenario in scenarios:
        status_class = "passed" if scenario.get("status") == "passed" else "failed"
        status_text = scenario.get("status", "unknown").upper()
        scenario_name = html_lib.escape(scenario.get("name", "Unknown"))
        steps_html = "".join(
            f"<li>{html_lib.escape(step.get('keyword', ''))} {html_lib.escape(step.get('name', ''))} - {html_lib.escape(step.get('status', ''))}</li>"
            for step in scenario.get("steps", [])
        )
        scenarios_html += f"""
        <div class="scenario {status_class}">
            <span class="status">{status_text}</span>: {scenario_name}
            <ul>{steps_html}</ul>
        </div>
        """

    html_content = html_template.format(scenarios=scenarios_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content)
