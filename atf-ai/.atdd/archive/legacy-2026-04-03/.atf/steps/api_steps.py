"""API step definitions for ATF."""

from typing import Any

from behave import given, when, then

from atf.interactions.call_an_api import CallAnApi


@given("I am an ApiClient")
def step_given_api_client(context: Any) -> None:
    """Set up ApiClient actor."""
    context.api_client = CallAnApi()


@when('I call GET "{url}"')
def step_call_get(context: Any, url: str) -> None:
    """Make a GET request to the URL."""
    api = context.api_client
    api.get(url)


@when('I call POST "{url}" with body:')
def step_call_post(context: Any, url: str) -> None:
    """Make a POST request with JSON body."""
    api = context.api_client
    body = getattr(context, "text", "") or ""
    api.post(url, body)


@when('I call DELETE "{url}"')
def step_call_delete(context: Any, url: str) -> None:
    """Make a DELETE request."""
    api = context.api_client
    api.delete(url)


@when('I set header "{name}" to "{value}"')
def step_set_header(context: Any, name: str, value: str) -> None:
    """Set request header on ApiClient."""
    api = context.api_client
    api.set_header(name, value)


@then("the response status should be {code:d}")
def step_response_status(context: Any, code: int) -> None:
    """Check the response status code."""
    api = context.api_client
    response = api.last_response
    assert response is not None, "No response available"
    assert response.status_code == code, f"Expected status {code}, got {response.status_code}"


@then('the response should contain "{text}"')
def step_response_contains(context: Any, text: str) -> None:
    """Check that response contains text."""
    api = context.api_client
    response = api.last_response
    assert response is not None, "No response available"
    assert text in response.text, f"Response does not contain '{text}'"


@then('the response field "{field}" should equal "{value}"')
def step_response_field(context: Any, field: str, value: str) -> None:
    """Check that response JSON field equals expected value."""
    api = context.api_client
    response = api.last_response
    assert response is not None, "No response available"
    data = response.json()
    actual = data.get(field)
    assert str(actual) == value, f"Field '{field}' has value '{actual}', expected '{value}'"
