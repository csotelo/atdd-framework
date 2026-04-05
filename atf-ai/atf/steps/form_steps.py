"""Form step definitions for ATF."""

from typing import Any

from behave import when


@when('I fill in "{field}" with "{value}"')
def step_fill_in(context: Any, field: str, value: str) -> None:
    """Fill input by label or name."""
    page = context.web_user["page"]
    locator = page.locator(
        f"input[name='{field}'], input[id='{field}'], "
        f"label:has-text('{field}') >> .. >> input, "
        f"input[placeholder='{field}']"
    )
    locator.first.fill(value)


@when('I click the "{text}" button')
def step_click_button(context: Any, text: str) -> None:
    """Click button by visible text."""
    page = context.web_user["page"]
    page.get_by_role("button", name=text).click()


@when('I click "{selector}"')
def step_click_selector(context: Any, selector: str) -> None:
    """Click by CSS selector."""
    page = context.web_user["page"]
    page.locator(selector).click()


@when('I select "{value}" from "{field}"')
def step_select_option(context: Any, value: str, field: str) -> None:
    """Select option from dropdown."""
    page = context.web_user["page"]
    locator = page.locator(f"select[name='{field}'], select[id='{field}']")
    locator.first.select_option(label=value)
