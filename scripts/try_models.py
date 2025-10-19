#!/usr/bin/env python3
"""Try a short list of model names against the configured token and report results.

Usage:
  copy .env.example -> .env and add your token, or set GITHUB_MODELS_API_KEY in env
  python scripts\try_models.py
"""
import os
import sys

# Ensure the workspace root (project) is on sys.path so local package imports work
# when running this script directly from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from github_models.client import GitHubModelsClient, Config

CANDIDATES = [
    "claude-sonnet-3.5",
    "claude-sonnet-3",
    "claude-sonnet",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-3.5",
]


def main():
    cfg = Config.from_env()
    client = GitHubModelsClient(cfg)
    print("Using model list candidates:")
    for m in CANDIDATES:
        print(f" - {m}")
    print()

    for m in CANDIDATES:
        try:
            print(f"Trying model: {m}")
            # Use a tiny prompt and low max_tokens to minimize cost/time
            out = client.generate_text("Hello", model=m, max_tokens=8)
            print(f"  OK: received output (truncated): {str(out)[:200]!r}\n")
        except Exception as exc:
            print(f"  FAILED: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
