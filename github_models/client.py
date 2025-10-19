import os
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    enable_claude_sonnet_3_5: bool = True
    api_style: str = "github"
    org: Optional[str] = None
    api_version: Optional[str] = None
    allow_no_api_key: bool = False
    debug_log_headers: bool = False

    @classmethod
    def from_env(cls):
        api_key = os.getenv("GITHUB_MODELS_API_KEY")
        # Trim whitespace so a token that is only spaces doesn't get treated as present.
        if api_key is not None:
            api_key = api_key.strip()
            if api_key == "":
                api_key = None
        base_url = os.getenv("GITHUB_MODELS_BASE_URL", "https://models.github.ai")
        # Default to enabled so Claude Sonnet 3.5 is used for all clients unless explicitly disabled
        enable_flag = os.getenv("ENABLE_CLAUDE_SONNET_3_5", "1")
        api_style = os.getenv("GITHUB_MODELS_API_STYLE", "github")
        org = os.getenv("GITHUB_MODELS_ORG")
        api_version = os.getenv("GITHUB_MODELS_API_VERSION")
        allow_no_key = os.getenv("GITHUB_MODELS_ALLOW_NO_API_KEY", "0")
        debug_headers = os.getenv("GITHUB_MODELS_DEBUG_HEADERS", "0")
        return cls(
            api_key=api_key,
            base_url=base_url,
            enable_claude_sonnet_3_5=(enable_flag in ("1", "true", "True")),
            api_style=api_style,
            org=org,
            api_version=api_version,
            allow_no_api_key=(allow_no_key in ("1", "true", "True")),
            debug_log_headers=(debug_headers in ("1", "true", "True")),
        )


class GitHubModelsClient:
    """Simple HTTP wrapper for GitHub Models-like API.

    This scaffold does not assume the exact API shape; adjust endpoints and payloads to match current GitHub Models API.
    """

    def __init__(self, config: Optional["Config"] = None):
        self.config = config or Config.from_env()
        if not self.config.api_key:
            if not getattr(self.config, "allow_no_api_key", False):
                raise ValueError(
                    "GITHUB_MODELS_API_KEY is required (set the env var, enable GITHUB_MODELS_ALLOW_NO_API_KEY for local debugging, or use a .env file via launch.json)"
                )
            # allowed to run without API key for local debugging
            # session will not include Authorization header
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
            })
            if self.config.api_version:
                self.session.headers.update({"X-GitHub-Api-Version": self.config.api_version})
            return
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        })
        if self.config.api_version:
            # include optional API version header used in GitHub docs
            self.session.headers.update({"X-GitHub-Api-Version": self.config.api_version})

    def _model_for_request(self, model: Optional[str]):
        # normalize model name: strip whitespace and any leading slashes so we send
        # 'claude-sonnet-3.5' instead of '/claude-sonnet-3.5'
        if model:
            m = model.strip()
            # remove any leading slashes that might have been accidentally included
            m = m.lstrip("/")
            return m
        if self.config.enable_claude_sonnet_3_5:
            return "claude-sonnet-3.5"
        return "default-model"

    def _post_json(self, url: str, payload: dict, timeout: int = 30):
        """Helper to POST JSON and raise a detailed HTTPError including response body for debugging."""
        # Optionally log masked headers for debugging
        if getattr(self.config, "debug_log_headers", False):
            try:
                headers = dict(self.session.headers)
                masked = {}
                for k, v in headers.items():
                    if k.lower() == "authorization":
                        # mask token but keep prefix
                        parts = v.split()
                        if len(parts) >= 2:
                            masked[k] = parts[0] + " [REDACTED]"
                        else:
                            masked[k] = "[REDACTED]"
                    else:
                        masked[k] = v
                print(f"[debug] POST {url} headers: {masked}")
                # If payload contains a model field, print it (helps diagnose model name issues).
                try:
                    model_value = payload.get("model") if isinstance(payload, dict) else None
                    if model_value is not None:
                        print(f"[debug] payload model: {model_value!r}")
                except Exception:
                    pass
            except Exception:
                print("[debug] could not read session headers")
        resp = self.session.post(url, json=payload, timeout=timeout)
        try:
            resp.raise_for_status()
        except Exception as exc:
            # include a short excerpt of the response body to help debug auth/shape issues
            text = None
            try:
                text = resp.text
            except Exception:
                text = "<no response body>"
            msg = f"HTTP {resp.status_code} when requesting {url}: {text[:1000]}"
            # raise a new HTTPError with the message and original response attached
            from requests import HTTPError

            raise HTTPError(msg, response=resp) from exc
        return resp.json()

    def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 512):
        model_to_use = self._model_for_request(model)
        # defensive normalize again at send time to avoid sending any leading slashes
        if isinstance(model_to_use, str):
            model_to_use = model_to_use.strip().lstrip('/')
        # Use GitHub Models inference endpoints (chat completions) by default.
        style = (self.config.api_style or "github").lower()

        # Build URL (org-attributed endpoints if org is present)
        base = self.config.base_url.rstrip("/")
        org_segment = None
        if self.config.org:
            org_segment = f"/orgs/{self.config.org}"

        # Chat-based inference (preferred GitHub Models shape)
        if style in ("github", "chat"):
            # If no api key but allowed for debugging, return a safe dummy response instead of calling out
            if not self.config.api_key and getattr(self.config, "allow_no_api_key", False):
                return f"[debug] simulated response for prompt: {prompt}"
            if org_segment:
                url = f"{base}{org_segment}/inference/chat/completions"
            else:
                url = f"{base}/inference/chat/completions"
            payload = {"model": model_to_use, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            data = self._post_json(url, payload)
            choices = data.get("choices") or []
            if choices and isinstance(choices, list):
                first = choices[0]
                if isinstance(first, dict):
                    msg = first.get("message") or first.get("delta")
                    if isinstance(msg, dict):
                        return msg.get("content") or str(msg)
                    # fallback if choice holds string
                    if first.get("text"):
                        return first.get("text")
            # last fallback
            return data.get("text") or data.get("generated_text") or str(data)

        # OpenAI-like completions compatibility
        if style == "openai":
            if org_segment:
                url = f"{base}{org_segment}/inference/completions"
            else:
                url = f"{base}/inference/completions"
            payload = {"model": model_to_use, "prompt": prompt, "max_tokens": max_tokens}
            data = self._post_json(url, payload)
            choices = data.get("choices") or []
            if choices and isinstance(choices, list):
                first = choices[0]
                if isinstance(first, dict) and first.get("text"):
                    return first.get("text")
                return str(first)
            return str(data)

        # fallback to simple endpoint
        url = f"{base}/inference/chat/completions"
        payload = {"model": model_to_use, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        data = self._post_json(url, payload)
        return data.get("text") or data.get("generated_text") or str(data)

    def list_models(self):
        """Try to list available models for the current token/account.

        This helper will try several endpoints that different APIs use to list
        models and return the first successful JSON response. It returns a
        tuple (endpoint_used, json_body).
        """
        base = self.config.base_url.rstrip("/")
        org_segment = f"/orgs/{self.config.org}" if self.config.org else ""
        # Try several likely endpoints and hostnames. Different deployments
        # and docs may show models under models.github.ai, api.github.com, or
        # under an /inference path. Try org-scoped and non-org variants.
        candidates = [
            f"{base}{org_segment}/models",
            f"{base}/models",
            f"{base}{org_segment}/inference/models",
            f"{base}/inference/models",
            # Try the public GitHub API host as some docs reference api.github.com
            "https://api.github.com/models",
            f"https://api.github.com{org_segment}/models",
            f"https://api.github.com{org_segment}/inference/models",
            "https://api.github.com/inference/models",
        ]
        last_err = None
        for url in candidates:
            try:
                resp = self.session.get(url, timeout=15)
            except Exception as exc:
                last_err = exc
                continue
            if resp is None:
                continue
            if 200 <= resp.status_code < 300:
                try:
                    return url, resp.json()
                except Exception:
                    return url, resp.text
            # remember the last non-200 response for error reporting
            last_err = resp
        # none succeeded
        msg = "Could not list models. Tried endpoints: " + ", ".join(candidates)
        if isinstance(last_err, requests.Response):
            try:
                body = last_err.text
            except Exception:
                body = "<no body>"
            raise RuntimeError(f"{msg}; last response {last_err.status_code}: {body[:1000]}")
        if last_err is not None:
            raise RuntimeError(f"{msg}; last error: {last_err}")
        raise RuntimeError(msg)
