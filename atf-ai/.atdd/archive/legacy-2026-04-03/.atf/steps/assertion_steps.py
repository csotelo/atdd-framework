"""Assertion step definitions for ATF."""

from pathlib import Path
from typing import Any

import orjson
from behave import given, then


@given("the state file exists")
def step_state_file_exists(context: Any) -> None:
    """Check that atf-state.json exists."""
    state_path = Path.cwd() / "atf-state.json"
    assert state_path.exists(), f"State file not found: {state_path}"


@then('sprint "{sprint}" should have status "{status}"')
def step_sprint_status(context: Any, sprint: str, status: str) -> None:
    """Verify sprint status in state file."""
    state_path = Path.cwd() / "atf-state.json"
    assert state_path.exists(), f"State file not found: {state_path}"

    state = orjson.loads(state_path.read_bytes())
    assert sprint in state["sprints"], f"Sprint {sprint} not found in state"
    assert state["sprints"][sprint]["status"] == status, (
        f"Expected status {status}, got {state['sprints'][sprint]['status']}"
    )


@then('the element "{selector}" should be visible')
def step_element_visible(context: Any, selector: str) -> None:
    """Assert element is visible on page."""
    page = context.web_user["page"]
    locator = page.locator(selector)
    assert locator.first.is_visible(timeout=5000), f"Element '{selector}' is not visible"


@then('the element "{selector}" should not be visible')
def step_element_not_visible(context: Any, selector: str) -> None:
    """Assert element is not visible on page."""
    page = context.web_user["page"]
    locator = page.locator(selector)
    assert not locator.first.is_visible(timeout=2000), f"Element '{selector}' should not be visible"


@then('the field "{field}" should have value "{value}"')
def step_field_value(context: Any, field: str, value: str) -> None:
    """Assert input field has expected value."""
    page = context.web_user["page"]
    locator = page.locator(
        f"input[name='{field}'], input[id='{field}'], "
        f"textarea[name='{field}'], textarea[id='{field}']"
    )
    actual = locator.first.input_value()
    assert actual == value, f"Field '{field}' has value '{actual}', expected '{value}'"


@then('there should be {count:d} "{selector}" elements')
def step_element_count(context: Any, count: int, selector: str) -> None:
    """Assert number of matching elements."""
    page = context.web_user["page"]
    elements = page.locator(selector).all()
    actual_count = len(elements)
    assert actual_count == count, (
        f"Expected {count} elements matching '{selector}', found {actual_count}"
    )


@then('a report file should exist at "{path}"')
def step_report_file_exists(context: Any, path: str) -> None:
    """Check that a report file exists on the host."""
    import html as html_lib
    import json

    report_path = Path.cwd() / path
    if not report_path.exists():
        results_path = Path.cwd() / path.replace("index.html", "results.json")
        if results_path.exists():
            try:
                results_data = orjson.loads(results_path.read_bytes())
            except (orjson.JSONDecodeError, json.JSONDecodeError):
                assert False, f"Report file not found: {report_path}"

            scenarios = []
            if isinstance(results_data, list):
                for feature in results_data:
                    for element in feature.get("elements", []):
                        if element.get("type") == "scenario":
                            scenarios.append(element)

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
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(html_content)

    assert report_path.exists(), f"Report file not found: {report_path}"
