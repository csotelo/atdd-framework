"""Navigation step definitions for ATF."""

import time
from typing import Any

from behave import given, when, then


@given("I am a WebUser")
def step_given_web_user(context: Any) -> None:
    """Set up WebUser actor."""
    pass


@when('I navigate to "{url}"')
def step_navigate_to(context: Any, url: str) -> None:
    """Navigate to a URL."""
    page = context.web_user["page"]
    page.goto(url, wait_until="domcontentloaded", timeout=30000)


@then('I should see "{text}"')
def step_should_see(context: Any, text: str) -> None:
    """Check that page contains text."""
    page = context.web_user["page"]
    assert page.text_content("body") and text in page.text_content("body"), (
        f"Text '{text}' not found on page"
    )


@then('I should not see "{text}"')
def step_should_not_see(context: Any, text: str) -> None:
    """Assert text is absent from page."""
    page = context.web_user["page"]
    body_text = page.text_content("body") or ""
    assert text not in body_text, f"Text '{text}' should not be on page"


@when('I wait for "{selector}"')
def step_wait_for_selector(context: Any, selector: str) -> None:
    """Wait until selector is visible."""
    page = context.web_user["page"]
    page.wait_for_selector(selector, state="visible", timeout=10000)


@when("I wait {seconds:d} seconds")
def step_wait_seconds(context: Any, seconds: int) -> None:
    """Sleep N seconds."""
    time.sleep(seconds)
