"""Small, dependency-free client for Figranium's documented task API."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "http://localhost:11345"
DEFAULT_TIMEOUT_SECONDS = 120
MAX_TIMEOUT_SECONDS = 300
TIMEOUT_ERROR_MESSAGE = "Figranium request timed out. Increase the timeout for long-running tasks."


class FigraniumError(Exception):
    """A safe, user-facing Figranium integration error."""


def normalize_base_url(value: Any) -> str:
    base_url = str(value or DEFAULT_BASE_URL).strip().rstrip("/")
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise FigraniumError("Figranium base URL must be an absolute http(s) URL.")
    if parsed.query or parsed.fragment:
        raise FigraniumError("Figranium base URL must not contain a query string or fragment.")
    return base_url


def parse_timeout(value: Any) -> int:
    if value in (None, ""):
        return DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = int(str(value))
    except (TypeError, ValueError) as error:
        message = "Request timeout must be a whole number between 1 and 300 seconds."
        raise FigraniumError(message) from error
    if not 1 <= timeout <= MAX_TIMEOUT_SECONDS:
        raise FigraniumError("Request timeout must be between 1 and 300 seconds.")
    return timeout


def parse_variables_json(value: Any) -> dict[str, str]:
    if value in (None, ""):
        return {}
    if not isinstance(value, str):
        raise FigraniumError("Variable overrides must be supplied as a JSON object.")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise FigraniumError("Variable overrides must be valid JSON.") from error
    if not isinstance(parsed, dict) or any(
        not isinstance(key, str) or not isinstance(item, str) for key, item in parsed.items()
    ):
        message = "Variable overrides must be a JSON object with string keys and string values."
        raise FigraniumError(message)
    return parsed


@dataclass(frozen=True)
class FigraniumClient:
    base_url: str
    api_key: str
    timeout_seconds: int

    @classmethod
    def from_credentials(cls, credentials: Mapping[str, Any]) -> FigraniumClient:
        api_key = str(credentials.get("api_key") or "").strip()
        if not api_key:
            raise FigraniumError("Figranium API key is required.")
        return cls(
            base_url=normalize_base_url(credentials.get("base_url")),
            api_key=api_key,
            timeout_seconds=parse_timeout(credentials.get("timeout_seconds")),
        )

    def list_tasks(self) -> dict[str, Any]:
        response = self._request("GET", "/api/tasks/list")
        tasks = response.get("tasks") if isinstance(response, dict) else None
        if not isinstance(tasks, list):
            raise FigraniumError("Figranium returned an invalid task-list response.")
        return response

    def execute_task(self, task_id: Any, variables: Mapping[str, str]) -> dict[str, Any]:
        normalized_task_id = str(task_id or "").strip()
        if not normalized_task_id:
            raise FigraniumError("Task ID is required.")
        path = f"/api/tasks/{quote(normalized_task_id, safe='')}/api"
        return self._request("POST", path, {"variables": dict(variables)})

    def _request(
        self, method: str, path: str, payload: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310 -- fixed configured base URL
                body = response.read().decode("utf-8")
        except HTTPError as error:
            raise self._http_error(error.code) from error
        except TimeoutError as error:
            raise FigraniumError(TIMEOUT_ERROR_MESSAGE) from error
        except URLError as error:
            if isinstance(error.reason, TimeoutError):
                raise FigraniumError(TIMEOUT_ERROR_MESSAGE) from error
            raise FigraniumError("Could not connect to the configured Figranium server.") from error
        except OSError as error:
            raise FigraniumError("Could not connect to the configured Figranium server.") from error

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as error:
            raise FigraniumError("Figranium returned an invalid JSON response.") from error
        if not isinstance(parsed, dict):
            raise FigraniumError("Figranium returned an invalid JSON response.")
        return parsed

    @staticmethod
    def _http_error(status_code: int) -> FigraniumError:
        if status_code == 401:
            return FigraniumError(
                "Figranium rejected the API key. Check the configured credentials."
            )
        if status_code == 404:
            return FigraniumError("The requested Figranium task was not found.")
        if status_code == 400:
            return FigraniumError(
                "Figranium rejected the request. Check the task ID and variable overrides."
            )
        if 500 <= status_code <= 599:
            return FigraniumError("Figranium encountered a server error. Try again later.")
        return FigraniumError(f"Figranium request failed with HTTP status {status_code}.")
