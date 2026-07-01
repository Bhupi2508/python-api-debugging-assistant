"""Gemini provider.

Environment variables (in .env):
- AI_PROVIDER=gemini
- GEMINI_API_KEY=... (required)
- GEMINI_MODEL=gemini-1.5-flash (or any supported model)
"""

from __future__ import annotations

from dataclasses import dataclass

from services.providers.base_provider import AIProvider


@dataclass
class GeminiProvider(AIProvider):
    api_key: str | None
    model: str | None
    timeout_seconds: int

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env.")
        if not self.model:
            raise ValueError("GEMINI_MODEL is not set in .env.")

        # Lazy import so Gemini SDK isn't required when using other providers.
        from google import genai

        client = genai.Client(api_key=self.api_key)
        # google-genai uses `generate_content`.
        resp = client.models.generate_content(
            model=self.model,
            contents=[
                {"role": "user", "parts": [{"text": prompt}]},
            ],
            config={
                "temperature": 0.2,
            },
        )

        # Response shape for google-genai: resp.text (string)
        text = (getattr(resp, "text", None) or "").strip()
        return text
