"""
LLM provider abstraction for P2S.

Both providers expose the same interface:
    provider.generate_json(prompt, system=...) -> dict

This lets the triage engine stay identical while the backend model is swapped
between a cloud model (Gemini) and a local, offline model (Ollama).
"""
import os
import re
import json
import time
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")


class LLMError(Exception):
    """Raised when a provider cannot return a usable response."""


class GeminiProvider:
    name = "gemini"

    def __init__(self, model: str = GEMINI_MODEL):
        from google import genai
        from google.genai import types
        self._types = types
        self.model = model
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options=types.HttpOptions(timeout=60_000),
        )

    @property
    def label(self) -> str:
        return f"Gemini ({self.model})"

    def generate_json(self, prompt: str, system: str = "", schema: dict | None = None) -> dict:
        contents = f"{system}\n\n{prompt}" if system else prompt
        last_err = None
        for attempt in range(4):
            try:
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=self._types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )
                return json.loads(resp.text)
            except json.JSONDecodeError as e:
                last_err = e
                break
            except Exception as e:  # network / quota / overload
                last_err = e
                msg = str(e)
                if attempt == 3:
                    break
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    m = re.search(r"retry in ([\d.]+)s", msg)
                    time.sleep(min(float(m.group(1)) + 1 if m else 20, 65))
                    continue
                if any(code in msg for code in ("503", "UNAVAILABLE", "504", "DEADLINE")):
                    time.sleep(2 * (attempt + 1))
                    continue
                break
        raise LLMError(f"Gemini request failed: {last_err}")


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_URL, api_key: str | None = None, timeout: int = 180):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key if api_key is not None else OLLAMA_API_KEY
        self.timeout = timeout

    @property
    def label(self) -> str:
        return f"Ollama ({self.model}, local)"

    def is_available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def installed_models(self) -> list[str]:
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=3) as r:
                data = json.loads(r.read().decode())
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def generate_json(self, prompt: str, system: str = "", schema: dict | None = None) -> dict:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            # A JSON schema constrains decoding; plain "json" is the fallback.
            "format": schema if schema else "json",
            "options": {"temperature": 0.2, "num_ctx": 4096},
            "keep_alive": "30m",
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode(),
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                body = json.loads(r.read().decode())
            return json.loads(body["message"]["content"])
        except urllib.error.URLError as e:
            raise LLMError(
                "Ollama is not reachable on "
                f"{self.base_url}. Start it (ollama serve) and pull the model "
                f"(ollama pull {self.model}). Details: {e}"
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise LLMError(f"Ollama returned an unusable response: {e}")


# ---- Runtime selection -----------------------------------------------------

_active = os.getenv("LLM_PROVIDER", "gemini").lower()
_cache: dict[str, object] = {}


def get_provider(name: str | None = None):
    """Return a provider instance by name ('gemini' | 'ollama'); default = active."""
    name = (name or _active).lower()
    if name not in ("gemini", "ollama"):
        raise ValueError(f"Unknown provider '{name}'")
    if name not in _cache:
        _cache[name] = GeminiProvider() if name == "gemini" else OllamaProvider()
    return _cache[name]


def get_active_name() -> str:
    return _active


def set_active(name: str) -> str:
    global _active
    name = name.lower()
    if name not in ("gemini", "ollama"):
        raise ValueError(f"Unknown provider '{name}'")
    _active = name
    return _active
