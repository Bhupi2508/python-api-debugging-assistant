"""OpenAI provider.

Environment variables (in .env):
- AI_PROVIDER=openai
- OPENAI_API_KEY=... (required)
- OPENAI_MODEL=gpt-4o-mini (or any chat-capable model)
- (optional) OPENAI_BASE_URL=https://api.openai.com/v1
"""

from __future__ import annotations

from dataclasses import dataclass

from services.providers.base_provider import AIProvider


@dataclass
class OpenAIProvider(AIProvider):
    api_key: str | None
    model: str | None
    base_url: str | None
    timeout_seconds: int

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env.")
        if not self.model:
            raise ValueError("OPENAI_MODEL is not set in .env.")

        # Lazy import so OpenAI SDK isn't required when using other providers.
        from openai import OpenAI

        client_kwargs: dict[str, object] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = OpenAI(**client_kwargs)

        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful developer assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        text = (resp.choices[0].message.content or "").strip()
        return text
