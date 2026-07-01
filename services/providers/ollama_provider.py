"""Ollama provider.

This provider is designed for local models via Ollama.

Expected environment variables (in .env):
- AI_PROVIDER=ollama
- OLLAMA_BASE_URL=http://localhost:11434
- OLLAMA_MODEL=llama3 (or any available local model)
"""

from __future__ import annotations

from dataclasses import dataclass
import requests

from services.providers.base_provider import AIProvider


@dataclass
class OllamaProvider(AIProvider):
    base_url: str | None
    model: str | None
    timeout_seconds: int

    def complete(self, prompt: str) -> str:
        if not self.base_url:
            raise ValueError("OLLAMA_BASE_URL is not set in .env.")
        if not self.model:
            raise ValueError("OLLAMA_MODEL is not set in .env.")

        url = self.base_url.rstrip("/") + "/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            # keep it deterministic-ish for explanations; tune later per provider.
            "stream": False,
        }

        resp = requests.post(url, json=payload, timeout=self.timeout_seconds)
        resp.raise_for_status()

        data = resp.json()
        # Ollama returns {"response": "...", ...}
        text = (data.get("response") or "").strip()
        return text
