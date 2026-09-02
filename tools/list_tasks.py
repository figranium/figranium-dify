from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from figranium_client import FigraniumClient


class ListTasksTool(Tool):
    """List saved Figranium task summaries."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        del tool_parameters
        client = FigraniumClient.from_credentials(self.runtime.credentials)
        yield self.create_json_message(client.list_tasks())
