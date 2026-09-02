# Figranium for Dify

Official Dify Tool Plugin for executing reusable [Figranium](https://github.com/figranium/figranium) browser automation tasks from Dify workflows and agents.

## Capabilities

- **Execute Task** — runs a saved task by ID and returns Figranium's JSON result unchanged. Optional runtime variables are supplied as a JSON object.
- **List Tasks** — lists saved task IDs, names, and descriptions, so an agent or workflow can identify the task to run.

Task creation, deletion, scheduling, browser sessions, inspectors, and execution-history access are intentionally not included. Build and manage automations in Figranium, then use this plugin to run them from Dify.

## Setup

1. Run a reachable Figranium server. The default local address is `http://localhost:11345`.
2. Create an API key in Figranium Settings.
3. Install this plugin in Dify and configure its provider:
   - **Figranium base URL**: the URL Dify can reach (not necessarily `localhost` when Dify runs in a container).
   - **Figranium API key**: the key from Figranium Settings.
   - **Request timeout**: 1–300 seconds; defaults to 120.
4. Add **Figranium → Execute Task** to a workflow or enable it for an agent.

## Execute Task input

- `task_id` — required saved Figranium task ID. Call **List Tasks** when the ID is not known.
- `variables_json` — optional JSON object with string values, for example:

```json
{"url":"https://example.com","limit":"10"}
```

The plugin sends the documented Figranium request:

```http
POST /api/tasks/{taskId}/api
x-api-key: {api-key}
Content-Type: application/json

{"variables":{"url":"https://example.com","limit":"10"}}
```

## Security and privacy

This plugin sends its API key and tool inputs only to the configured Figranium server. It has no telemetry, analytics, persistent storage, or calls to any other service. Because Figranium tasks can automate browsers, only enable tasks you trust and make the server accessible only to intended Dify deployments.

See [PRIVACY.md](PRIVACY.md) for the complete data-use statement.

## Development

Use Python 3.12 and the Dify Plugin CLI. Install dependencies with `uv sync`, run `uv run pytest` and `uv run ruff check .`, then package with `dify plugin package .`.

Marketplace publication requires the `figranium` Marketplace organization and an approved submission; this repository does not publish automatically.

