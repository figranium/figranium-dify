from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from figranium_client import FigraniumClient, parse_variables_json


class ExecuteTaskTool(Tool):
    """Run a saved Figranium task with optional runtime variables."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        client = FigraniumClient.from_credentials(self.runtime.credentials)
        variables = parse_variables_json(tool_parameters.get("variables_json"))
        response = client.execute_task(tool_parameters.get("task_id"), variables)
        yield self.create_json_message(response)
