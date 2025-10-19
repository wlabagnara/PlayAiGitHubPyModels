import os
from github_models import GitHubModelsClient, Config


def main():
    # optionally override config from env
    cfg = Config.from_env()
    client = GitHubModelsClient(cfg)

    prompt = os.getenv("EXAMPLE_PROMPT", "Write a short sonnet about coding in Python.")
    # Respect explicit default model if provided via env
    default_model = os.getenv("GITHUB_MODELS_DEFAULT_MODEL")
    if default_model:
        print("Using model:", default_model)
        out = client.generate_text(prompt, model=default_model)
    else:
        print("Using model:", cfg.enable_claude_sonnet_3_5 and "claude-sonnet-3.5" or "default-model")
        out = client.generate_text(prompt)
    print("---\nResult:\n")
    print(out)


if __name__ == "__main__":
    main()
