# PlayAi GitHub Models Python Samples

This scaffold provides a minimal Python project for building AI applications using GitHub Models.

Overview
- `github_models/` - small package with a client wrapper
- `example/` - sample CLI showing how to use the client
- `tests/` - unit tests

Setup (Windows cmd.exe)

1. Create virtual environment:

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```cmd
pip install -r requirements.txt
```

Environment variables
- `GITHUB_MODELS_API_KEY` - your GitHub Models API key
- `GITHUB_MODELS_BASE_URL` - optional base URL for the API (defaults to GitHub's models endpoint)
- `ENABLE_CLAUDE_SONNET_3_5` - set to `1` to enable Claude Sonnet 3.5 for all clients
- `GITHUB_MODELS_API_STYLE` - one of `github` (default), `openai`, or `chat` to select the request/response shape
 - `GITHUB_MODELS_DEFAULT_MODEL` - optional. If set, `example/app.py` will use this model name when generating text. Useful to pin to a model your token can access (for example `gpt-4o`).
Additional GitHub Models settings
- `GITHUB_MODELS_ORG` - optional organization slug to attribute requests to org endpoints (maps to /orgs/{org}/inference/...)
- `GITHUB_MODELS_API_VERSION` - optional `X-GitHub-Api-Version` header value (e.g., `2022-11-28`)

Defaults and notes
- Default `GITHUB_MODELS_BASE_URL` is `https://models.github.ai` to match GitHub Models docs. If you have a different host, set this env var.

Usage

```cmd
# activate venv then run example
python example/app.py
```

Using a default model via `.env` or VS Code
- Create `.env` in the project root (copy `.env.example`) and add:

```
GITHUB_MODELS_API_KEY=your_token_here
GITHUB_MODELS_DEFAULT_MODEL=gpt-4o
```

- The VS Code launch configuration (`.vscode/launch.json`) loads `.env` when you debug the example, so you can keep secrets out of the repo. The example will prefer `GITHUB_MODELS_DEFAULT_MODEL` when present.

Run tests

```cmd
pytest -q
```
