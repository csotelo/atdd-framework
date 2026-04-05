"""Custom API interaction ability wrapping httpx.Client."""

import json

import httpx


class CallAnApi:
    """Ability to make HTTP requests."""

    def __init__(self) -> None:
        self._client = httpx.Client(verify=False, timeout=30.0)
        self._last_response: httpx.Response | None = None
        self._headers: dict[str, str] = {}

    def get(self, url: str) -> httpx.Response:
        """Make a GET request."""
        self._last_response = self._client.get(url, headers=self._headers)
        return self._last_response

    def post(self, url: str, body: str) -> httpx.Response:
        """Make a POST request with JSON body."""
        headers = {**self._headers, "Content-Type": "application/json"}
        try:
            data = json.loads(body)
            self._last_response = self._client.post(url, json=data, headers=headers)
        except (json.JSONDecodeError, TypeError):
            self._last_response = self._client.post(url, content=body, headers=headers)
        return self._last_response

    def delete(self, url: str) -> httpx.Response:
        """Make a DELETE request."""
        self._last_response = self._client.delete(url, headers=self._headers)
        return self._last_response

    def set_header(self, name: str, value: str) -> None:
        """Set a request header."""
        self._headers[name] = value

    @property
    def last_response(self) -> httpx.Response | None:
        """Get the last response."""
        return self._last_response

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    @classmethod
    def using_their(cls, client: httpx.Client) -> "CallAnApi":
        """Create ability with an existing httpx client."""
        ability = cls()
        ability._client = client
        return ability
