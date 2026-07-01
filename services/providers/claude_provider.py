"""Claude provider.

This is currently a minimal scaffold.

Environment variables (in .env):
- AI_PROVIDER=claude
- CLAUDE_API_KEY=...
- CLAUDE_MODEL=...

When you're ready, wire it to the Anthropic SDK.
"""

from __future__ import annotations

from dataclasses import dataclass

from services.providers.base_provider import AIProvider


@dataclass
class ClaudeProvider(AIProvider):
    api_key: str | None
    model: str | None
    timeout_seconds: int

    def complete(self, prompt: str) -> str:
        raise NotImplementedError(
            "Claude provider is scaffolded but not implemented yet. Set AI_PROVIDER to openai/gemini/ollama instead."
        )
