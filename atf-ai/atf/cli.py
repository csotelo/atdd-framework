"""CLI entry point for ATF."""

import shutil
import sys
from pathlib import Path

import click

from atf import __version__
from atf.config import get_config_path, write_default_config


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """ATF - Acceptance Testing Framework CLI."""
    pass


@main.command()
def init() -> None:
    """Initialize ATF configuration in the current directory."""
    config_path = get_config_path()
    if config_path.exists():
        click.echo(f"Error: {config_path} already exists", err=True)
        sys.exit(1)

    write_default_config()

    behave_ini_path = config_path.parent / "behave.ini"
    if not behave_ini_path.exists():
        behave_content = """[behave]
steps_dir = prompts/steps
environment_file = atf/environment.py
paths = prompts
format = pretty
"""
        behave_ini_path.write_text(behave_content)
        click.echo(f"Created {behave_ini_path.name}")
    else:
        click.echo(f"{behave_ini_path.name} already exists, skipping")

    atf_state_src = Path(__file__).parent.parent / "atf-state.json"
    state_file_path = config_path.parent / "atf-state.json"
    if not state_file_path.exists() and atf_state_src.exists():
        shutil.copy(atf_state_src, state_file_path)
        click.echo(f"Created {state_file_path.name}")

    state_template_src = Path(__file__).parent.parent / "STATE.md"
    state_template_path = config_path.parent / "STATE.md"
    if not state_template_path.exists() and state_template_src.exists():
        shutil.copy(state_template_src, state_template_path)
        click.echo(f"Created {state_template_path.name}")

    click.echo(f"Created {config_path.name}")


def discover_sprints() -> list[str]:
    """Discover sprints alphabetically from prompts/ directory."""
    prompts_dir = Path.cwd() / "prompts"
    if not prompts_dir.exists():
        return []
    sprints = []
    for entry in prompts_dir.iterdir():
        if entry.is_dir() and entry.name.startswith("sprint_"):
            feature_file = entry / "acceptance.feature"
            if feature_file.exists():
                sprints.append(entry.name)
    return sorted(sprints)


@main.command()
@click.option("--sprint", help="Sprint to run")
@click.option("--feedback", is_flag=True, help="Write feedback.md on failure")
@click.option("--retry", is_flag=True, help="Re-run even if passed")
@click.option("--all", "run_all", is_flag=True, help="Run all sprints")
def run(sprint: str | None, feedback: bool, retry: bool, run_all: bool) -> None:
    """Run acceptance tests."""
    from atf.feedback import write_feedback
    from atf.fixtures import run_fixtures_if_present
    from atf.runner import run_sprint
    from atf.state import load_state

    if run_all:
        sprints = discover_sprints()
        if not sprints:
            click.echo("No sprints found in prompts/", err=True)
            sys.exit(1)

        run_fixtures_if_present()

        results: list[dict[str, str]] = []
        overall_exit = 0

        for sprint_name in sprints:
            if not retry:
                try:
                    state = load_state()
                    sprint_data = state.get("sprints", {}).get(sprint_name, {})
                    if sprint_data.get("status") == "passed":
                        click.echo(f"Skipping {sprint_name} (already passed)")
                        results.append(
                            {
                                "sprint": sprint_name,
                                "status": "skipped",
                                "scenarios": str(sprint_data.get("scenarios", {}).get("passed", 0)),
                            }
                        )
                        continue
                except FileNotFoundError:
                    pass

            click.echo(f"\n--- Running {sprint_name} ---")
            exit_code = run_sprint(sprint_name, feedback=feedback, retry=retry)

            if feedback and exit_code != 0:
                wrote = write_feedback(sprint_name)
                if wrote:
                    click.echo(f"Feedback written to prompts/{sprint_name}/feedback.md")

            sprint_status = "passed" if exit_code == 0 else "failed"
            results.append(
                {
                    "sprint": sprint_name,
                    "status": sprint_status,
                    "scenarios": str(exit_code),
                }
            )

            if exit_code != 0:
                overall_exit = exit_code
                click.echo(f"\n{sprint_name} failed. Stopping.")
                break

        click.echo("\n" + "=" * 50)
        click.echo(f"{'Sprint':<15} {'Status':<10} {'Exit':<8}")
        click.echo("-" * 50)
        for r in results:
            click.echo(f"{r['sprint']:<15} {r['status']:<10} {r['scenarios']:<8}")
        click.echo("=" * 50)

        sys.exit(overall_exit)

    if not sprint:
        click.echo("Error: --sprint is required", err=True)
        sys.exit(1)

    if not retry:
        try:
            state = load_state()
            sprint_data = state.get("sprints", {}).get(sprint, {})
            if sprint_data.get("status") == "passed":
                click.echo(
                    f"Sprint '{sprint}' already passed. Use --retry to re-run.",
                    err=True,
                )
                sys.exit(0)
        except FileNotFoundError:
            pass

    run_fixtures_if_present()

    exit_code = run_sprint(sprint, feedback=feedback, retry=retry)

    if feedback and exit_code != 0:
        wrote = write_feedback(sprint)
        if wrote:
            click.echo(f"Feedback written to prompts/{sprint}/feedback.md")

    sys.exit(exit_code)


@main.command()
@click.option("--sprint", help="Show status for specific sprint")
def status(sprint: str | None) -> None:
    """Show sprint status from atf-state.json."""
    from atf.state import load_state

    try:
        state = load_state()
    except FileNotFoundError:
        click.echo("Error: atf-state.json not found. Run 'atf init' first.", err=True)
        sys.exit(1)

    if sprint:
        if sprint not in state.get("sprints", {}):
            click.echo(f"Error: sprint '{sprint}' not found", err=True)
            sys.exit(1)
        sprint_data = state["sprints"][sprint]
        click.echo(f"Sprint: {sprint}")
        click.echo(f"Status: {sprint_data.get('status', 'unknown')}")
        click.echo(f"Last run: {sprint_data.get('last_run', 'never')}")
        click.echo(f"Duration: {sprint_data.get('duration_seconds', 'N/A')}s")
        scenarios = sprint_data.get("scenarios", {})
        click.echo(
            f"Scenarios: {scenarios.get('passed', 0)} passed, "
            f"{scenarios.get('failed', 0)} failed, "
            f"{scenarios.get('total', 0)} total"
        )
        failures = sprint_data.get("failures", [])
        if failures:
            click.echo("\nFailures:")
            for failure in failures:
                click.echo(f"  - {failure.get('scenario')}: {failure.get('step')}")
    else:
        click.echo(f"{'Sprint':<12} {'Status':<10} {'Passed':<8} {'Failed':<8} {'Total':<8}")
        click.echo("-" * 54)
        for name, data in state.get("sprints", {}).items():
            scenarios = data.get("scenarios", {})
            click.echo(
                f"{name:<12} {data.get('status', 'unknown'):<10} "
                f"{scenarios.get('passed', 0):<8} {scenarios.get('failed', 0):<8} "
                f"{scenarios.get('total', 0):<8}"
            )


if __name__ == "__main__":
    main()
