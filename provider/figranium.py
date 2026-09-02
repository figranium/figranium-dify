from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from figranium_client import FigraniumClient, FigraniumError


class FigraniumProvider(ToolProvider):
    """Validate a Figranium connection before Dify saves its credentials."""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            FigraniumClient.from_credentials(credentials).list_tasks()
        except FigraniumError as error:
            raise ToolProviderCredentialValidationError(str(error)) from error
