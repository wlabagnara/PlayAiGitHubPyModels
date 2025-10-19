PlayAi GitHub Models — Chat Transcript
=====================================

Date: 2025-10-19
Repository: PlayAiGitHubPyModels

Overview
--------
This file is an export of the interactive development session where we scaffolded a small Python project to call GitHub Models, implemented a client wrapper, added an example, tests, and debugging helpers.

Important: this transcript omits any secret values (API tokens) and replaces them with placeholders like [REDACTED] where the token was masked in logs. Do not commit real `.env` files containing secrets.

Session summary
---------------
- Goal: Create AI applications in Python using GitHub Models; enable "Claude Sonnet 3.5" as a default option for clients.
- Major artifacts created:
  - `github_models/` package with `client.py` (Config, GitHubModelsClient)
  - `example/app.py` sample CLI
  - `tests/test_client.py` unit tests
  - `.vscode/launch.json` debug configuration
  - `.env.example`, `.gitignore`
  - `scripts/try_models.py` to probe which models the token can access
  - `README.md` updated with guidance including `GITHUB_MODELS_DEFAULT_MODEL`

Key features implemented
------------------------
- Config.from_env driven by environment variables:
  - GITHUB_MODELS_API_KEY, GITHUB_MODELS_BASE_URL, GITHUB_MODELS_API_STYLE, GITHUB_MODELS_ORG
  - ENABLE_CLAUDE_SONNET_3_5 (defaults to enabled)
  - GITHUB_MODELS_ALLOW_NO_API_KEY (debug bypass)
  - GITHUB_MODELS_DEBUG_HEADERS (prints masked headers and payload model)
  - GITHUB_MODELS_DEFAULT_MODEL (used by `example/app.py` when present)

- HTTP helper `_post_json` that raises enriched HTTPError including a short excerpt of the response body to aid debugging (e.g., 401/404 details are surfaced).

- Model name sanitization: model names are normalized (strip whitespace and leading slashes) before sending to the API to avoid errors like "Unknown model: /name".

- `list_models()` helper and `scripts/try_models.py` added to probe model availability for the given token.

Debugging & common issues encountered
------------------------------------
- Import errors when running example directly were fixed by running as a module or ensuring the workspace root is on `PYTHONPATH`. The `.vscode/launch.json` is configured to run the example as a module and to pass the workspace root in `PYTHONPATH`.

- Missing API key: by default the client raises a helpful ValueError. For local debugging you can set `GITHUB_MODELS_ALLOW_NO_API_KEY=1` to return a simulated response.

- 401 Unauthorized during early runs: the debug header printing revealed the Authorization header was being sent but the launch.json had a placeholder value (a single space). We added trimming/validation to treat all-whitespace tokens as missing and provide a clearer error.

- Unknown model (404): The client initially sent a model string that the server reported as unknown. We added normalization and a `try_models` script that probed candidate models; the probe showed `gpt-4o` and `gpt-4o-mini` were available for the user's token but the Claude models were not.

Files changed / created (high-level)
-----------------------------------
- `github_models/client.py` — main client code, config parsing, sanitization, HTTP helpers, list_models, generate_text
- `example/app.py` — sample CLI; now respects `GITHUB_MODELS_DEFAULT_MODEL`
- `tests/test_client.py` — unit tests (passing: 5 tests)
- `.vscode/launch.json` — debug config using `envFile` to avoid committing tokens
- `.env.example` and `.gitignore` — local `.env` usage guidance
- `scripts/try_models.py` — attempts candidate model names and reports which succeed
- `chat_transcript.md` & `chat_transcript.pdf` — this transcript and the generated PDF

Key commands used during the session
-----------------------------------
- Create and activate venv (Windows cmd):

  python -m venv .venv
  .\.venv\Scripts\activate

- Install deps:

  pip install -r requirements.txt

- Run tests:

  .venv\Scripts\python -m pytest -q

- Run the example:

  .venv\Scripts\python -m example.app

- Try models script:

  .venv\Scripts\python scripts\try_models.py

Privacy & security notes
------------------------
- Never commit `.env` containing `GITHUB_MODELS_API_KEY`.
- If a token is accidentally committed, revoke it immediately via GitHub settings and create a new token.
- Prefer short-lived or fine-grained tokens for production workloads.

Selected debug outputs (redacted)
--------------------------------
- Example masked headers printed during debugging:

  [debug] POST https://models.github.ai/inference/chat/completions headers: {'User-Agent': 'python-requests/2.32.5', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/vnd.github+json', 'Connection': 'keep-alive', 'Authorization': 'Bearer [REDACTED]', 'Content-Type': 'application/json'}

- Unknown model error example (from server):

  HTTP 404 when requesting https://models.github.ai/inference/chat/completions: {"error":{"code":"unknown_model","message":"Unknown model: /claude-sonnet-3.5","details":"Unknown model: /claude-sonnet-3.5"}}

- Model probe results (sample):

  Trying model: claude-sonnet-3.5 -> FAILED (unknown_model)
  Trying model: gpt-4o -> OK: received output 'Hello! How can I assist you today'
  Trying model: gpt-4o-mini -> OK

Appendix: How to regenerate this PDF locally
-------------------------------------------
I provided a small script `scripts/generate_transcript_pdf.py` in the repo that converts `chat_transcript.md` into `chat_transcript.pdf` using ReportLab.

To run it locally (from project root):

1. Install ReportLab in your venv:

   .venv\Scripts\python -m pip install reportlab

2. Run the generator:

   .venv\Scripts\python scripts\generate_transcript_pdf.py

This writes `chat_transcript.pdf` to the project root.

End of transcript
