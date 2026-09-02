# Figranium for Dify

[Figranium](https://figranium.dev/) is a visual, self-hosted browser-automation platform. This official Dify Tool Plugin lets Dify workflows and agents run the reusable Figranium tasks you have already built and return their results as structured JSON.

> **Status:** ready for local and GitHub-based installation. This plugin has not yet been submitted to the Dify Marketplace.

- **Figranium:** [Website](https://figranium.dev/) · [Documentation](https://figranium.dev/docs) · [Source](https://github.com/figranium/figranium)
- **This plugin:** [Source](https://github.com/figranium/figranium-dify) · [Issues and support](https://github.com/figranium/figranium-dify/issues)

## What it does

| Tool | Use it when you need to |
| --- | --- |
| **Execute Task** | Run a saved Figranium task by ID, optionally overriding its runtime variables. This is the primary tool. |
| **List Tasks** | Retrieve task IDs, names, and descriptions before selecting a task to execute. |

The plugin deliberately does not create, modify, delete, schedule, inspect, or open browser sessions. Build and manage automation in Figranium; use Dify to invoke trusted, reusable tasks.

## Requirements

- A Figranium server reachable from the Dify runtime. The Figranium default is `http://localhost:11345`.
- A Figranium API key created in **Figranium Settings**.
- Dify 1.6.0 or later.

If Dify runs in Docker or on another host, `localhost` refers to that Dify runtime—not your laptop. Configure a network-reachable Figranium URL instead.

## Install and configure

### Install from a local package

1. Build or download a `figranium-<version>.difypkg` package.
2. In Dify, open **Plugins** → **Install Plugin** → **Install via Local File**.
3. Select the package, then open its Figranium provider settings.

### Configure the provider

| Setting | Description |
| --- | --- |
| **Figranium base URL** | The reachable URL of the Figranium server, such as `http://figranium.internal:11345`. |
| **Figranium API key** | The key from Figranium Settings. It is stored as a Dify secret and sent only as the `x-api-key` request header. |
| **Request timeout** | 1–300 seconds; defaults to 120. Increase it for legitimate long-running automations. |

Saving the credentials performs a read-only `List Tasks` request to verify the connection.

## Use in Dify

### Workflow

1. Add **Figranium → Execute Task** to a Workflow.
2. Set `task_id` to the ID of a saved Figranium task.
3. Optionally bind `variables_json` to a JSON string from an earlier node.
4. Use the returned JSON directly in downstream nodes.

### Agent

Enable **Figranium → Execute Task** and, when task discovery is useful, **Figranium → List Tasks**. The agent can call `List Tasks` to find an exact ID and then call `Execute Task`.

## Execute Task input and output

`task_id` is required. `variables_json` is optional and must be a JSON object whose keys and values are strings:

```json
{
  "url": "https://example.com",
  "limit": "10"
}
```

The plugin sends Figranium's documented request without reshaping the result:

```http
POST /api/tasks/{taskId}/api
x-api-key: {api-key}
Content-Type: application/json

{"variables":{"url":"https://example.com","limit":"10"}}
```

The complete JSON response from Figranium is returned to Dify. This retains task-specific output fields for workflows and agents.

## Errors and troubleshooting

| Message | What to check |
| --- | --- |
| API key rejected | Create or copy the API key from Figranium Settings again. |
| Task not found | Call **List Tasks** and use the returned exact task ID. |
| Could not connect | Confirm the base URL is reachable from the Dify runtime and that Figranium is running. |
| Request timed out | Increase the provider timeout or reduce the task's execution time. |
| Variable overrides invalid | Supply a JSON object with string keys and values; omit the field when no overrides are needed. |

## Security and privacy

Figranium tasks can automate browsers and may interact with credentials, websites, or data defined in those tasks. Enable only tasks you trust, scope Figranium API keys appropriately, and restrict network access to the Figranium server.

The plugin sends its API key, task ID, and optional variable overrides only to the Figranium URL configured in Dify. It has no telemetry, analytics, persistent storage, or calls to any other service. Read the full [privacy policy](PRIVACY.md).

## Development

This project requires Python 3.12 and [uv](https://docs.astral.sh/uv/). The Dify Plugin CLI is required to create installable packages.

```bash
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
dify plugin package . --output_path ../figranium-0.0.1.difypkg
```

The test suite covers request construction, URL and timeout validation, variable parsing, API errors, malformed responses, secret-safe error handling, and provider credential validation.

## Release and Marketplace

Do not publish a package until it has been tested against a reachable Figranium server. For a Marketplace release, package a new version, fork [langgenius/dify-plugins](https://github.com/langgenius/dify-plugins), and submit one package at `figranium/figranium/` through its English-language PR template. Disclose the browser-automation capability as high risk during review.

See Dify's [Marketplace submission guide](https://docs.dify.ai/en/develop-plugin/publishing/marketplace-listing/release-to-dify-marketplace) for current review requirements.

## License

This repository is distributed under the included [license](LICENSE).
