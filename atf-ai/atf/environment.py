"""Behave environment hooks for ATF."""

from typing import Any

from behave import use_step_matcher
from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]

from atf.interactions.call_an_api import CallAnApi

use_step_matcher("parse")


def before_all(context: Any) -> None:
    """Initialize browser and API actors before all tests."""
    context._playwright = sync_playwright().start()  # type: ignore[misc]
    context._browser = context._playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
    )  # type: ignore[misc]
    context._browser_context = context._browser.new_context()  # type: ignore[misc]

    context.web_user = {
        "context": context._browser_context,
        "page": None,
    }
    context.api_client = CallAnApi()


def before_feature(context: Any, feature: Any) -> None:
    """Run before each feature."""
    pass


def before_scenario(context: Any, scenario: Any) -> None:
    """Run before each scenario."""
    context.web_user["page"] = context._browser_context.new_page()


def after_scenario(context: Any, scenario: Any) -> None:
    """Run after each scenario."""
    if context.web_user and context.web_user.get("page"):
        context.web_user["page"].close()


def after_feature(context: Any, feature: Any) -> None:
    """Run after each feature."""
    pass


def after_all(context: Any) -> None:
    """Run after all tests."""
    if hasattr(context, "api_client") and context.api_client:
        context.api_client.close()

    if hasattr(context, "_browser"):
        context._browser.close()

    if hasattr(context, "_playwright"):
        context._playwright.stop()
