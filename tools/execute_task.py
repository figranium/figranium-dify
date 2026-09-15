from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import I18nObject, ToolInvokeMessage, ToolParameter, ToolParameterOption

from figranium_client import FigraniumClient, parse_variables_json


class ExecuteTaskTool(Tool):
    """Run a saved Figranium task with optional runtime variables."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        client = FigraniumClient.from_credentials(self.runtime.credentials)
        variables = parse_variables_json(tool_parameters.get("variables_json"))
        response = client.execute_task(tool_parameters.get("task_id"), variables)
        yield self.create_json_message(response)

    def get_runtime_parameters(self) -> list[ToolParameter]:
        """Populate the Task dynamic-select from the connected Figranium instance."""
        client = FigraniumClient.from_credentials(self.runtime.credentials)
        tasks = client.list_tasks().get("tasks", [])

        options: list[ToolParameterOption] = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            task_id = str(task.get("id") or "").strip()
            if not task_id:
                continue
            task_name = str(task.get("name") or task_id).strip() or task_id
            options.append(
                ToolParameterOption(
                    value=task_id,
                    label=I18nObject(en_US=task_name),
                )
            )

        return [
            ToolParameter(
                name="task_id",
                label=I18nObject(en_US="Task"),
                human_description=I18nObject(
                    en_US="Choose a saved task from the connected Figranium server."
                ),
                type=ToolParameter.ToolParameterType.DYNAMIC_SELECT,
                form=ToolParameter.ToolParameterForm.LLM,
                llm_description=(
                    "Select the saved Figranium automation task to execute from the available task list."
                ),
                required=True,
                options=options,
            )
        ]
