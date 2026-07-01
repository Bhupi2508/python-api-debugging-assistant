"""AI feature services.

These services implement the Phase 2 features that transform user input
into an AI response.

They are responsible for:
- loading prompt templates
- validating input
- calling the AI manager

They do NOT deal with SQLite directly; the CLI coordinates saving.
"""

from __future__ import annotations

from pathlib import Path

from services.ai_manager import complete

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def _load_prompt_template(prompt_filename: str) -> str:
    """Load a prompt template from the prompts/ folder."""

    path = PROMPTS_DIR / prompt_filename
    return path.read_text(encoding="utf-8")


def explain_error_service(user_input: str) -> str:
    """Explain an error for beginners."""

    input_text = (user_input or "").strip()
    if not input_text:
        raise ValueError("Error input cannot be empty.")

    template = _load_prompt_template("explain_error.txt")
    prompt = template.format(input=input_text)

    return complete(prompt)


def sql_assistant_service(user_input: str) -> str:
    """Answer a SQL question/help request."""

    input_text = (user_input or "").strip()
    if not input_text:
        raise ValueError("SQL input cannot be empty.")

    template = _load_prompt_template("sql_assistant.txt")
    prompt = template.format(input=input_text)

    return complete(prompt)
