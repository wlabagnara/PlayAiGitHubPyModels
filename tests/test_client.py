import os
import pytest
from github_models.client import Config, GitHubModelsClient


def test_config_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_MODELS_API_KEY", "testkey")
    monkeypatch.setenv("ENABLE_CLAUDE_SONNET_3_5", "1")
    cfg = Config.from_env()
    assert cfg.api_key == "testkey"
    assert cfg.enable_claude_sonnet_3_5 is True


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GITHUB_MODELS_API_KEY", raising=False)
    with pytest.raises(ValueError):
        GitHubModelsClient()


class DummyResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {"generated_text": "hello"}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("http error")

    def json(self):
        return self._json


def test_generate_text_happy_path(monkeypatch):
    monkeypatch.setenv("GITHUB_MODELS_API_KEY", "testkey")
    cfg = Config.from_env()
    client = GitHubModelsClient(cfg)

    def fake_post(url, json, timeout):
        # mimic GitHub chat completions response shape
        return DummyResponse(json_data={"choices": [{"message": {"content": json["messages"][0]["content"] + " world"}}]})

    client.session.post = fake_post
    res = client.generate_text("hi")
    assert "hi world" in res


def test_openai_style(monkeypatch):
    monkeypatch.setenv("GITHUB_MODELS_API_KEY", "testkey")
    monkeypatch.setenv("GITHUB_MODELS_API_STYLE", "openai")
    cfg = Config.from_env()
    client = GitHubModelsClient(cfg)

    def fake_post(url, json, timeout):
        return DummyResponse(json_data={"choices": [{"text": json.get("prompt") + " openai"}]})

    client.session.post = fake_post
    res = client.generate_text("hello")
    assert "hello openai" in res


def test_chat_style(monkeypatch):
    monkeypatch.setenv("GITHUB_MODELS_API_KEY", "testkey")
    monkeypatch.setenv("GITHUB_MODELS_API_STYLE", "chat")
    cfg = Config.from_env()
    client = GitHubModelsClient(cfg)

    def fake_post(url, json, timeout):
        return DummyResponse(json_data={"choices": [{"message": {"content": json["messages"][0]["content"] + " chat"}}]})

    client.session.post = fake_post
    res = client.generate_text("hey")
    assert "hey chat" in res
