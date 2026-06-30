# Phase 2: AI Integration Plan

This document is your **pre-build guide** for Phase 2. Read it before writing any AI code.

**Phase 1 (current)** gives you the CLI menu, SQLite storage, history, and export.  
**Phase 2** connects those menu actions to real AI providers and stores both input and AI response.

---

## What Phase 2 Adds

| Today (Phase 1) | Phase 2 |
|-----------------|---------|
| User pastes content | User pastes content |
| Content saved to SQLite | Content saved to SQLite |
| No AI response | AI analyzes content and returns a response |
| Export is input only | Export includes AI responses |

Phase 2 does **not** replace Phase 1. It extends the same menu items (1–7) with AI behind them.

---

## High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                         main.py (CLI)                           │
│  Menu → collect input → call feature handler → show result      │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       services/       database.py     config (.env)
       (AI logic)       (SQLite)        (API keys)
              │
              ▼
       ai_provider.py  ←── OpenAI / Claude / Gemini / Ollama
```

### Target Folder Structure (Phase 2)

```text
python-api-debugging-assistant/
├── main.py                      # CLI menu (already exists)
├── database.py                  # SQLite layer (extend for AI responses)
├── config.py                    # NEW: load .env settings
├── services/
│   ├── __init__.py
│   ├── ai_provider.py           # NEW: unified AI client wrapper
│   ├── explain_error.py         # NEW: prompt + call AI
│   ├── explain_code.py
│   ├── improve_code.py
│   ├── generate_tests.py
│   ├── sql_assistant.py
│   ├── regex_generator.py
│   └── git_assistant.py
├── prompts/                     # NEW: reusable prompt templates
│   ├── explain_error.txt
│   ├── explain_code.txt
│   └── ...
├── database/
│   └── developer_history.db
├── exports/                     # JSON exports (Phase 1)
├── .env                         # API keys (never commit)
├── .env.example
└── requirements.txt             # Add: openai, anthropic, python-dotenv, etc.
```

---

## End-to-End Flow (Phase 2)

```text
User selects "1. Explain an Error"
        │
        ▼
main.py → explain_error handler
        │
        ├── User pastes stack trace
        │
        ▼
services/explain_error.py
        │
        ├── Load prompt template from prompts/explain_error.txt
        ├── Build final prompt (template + user input)
        │
        ▼
services/ai_provider.py
        │
        ├── Read AI_PROVIDER from .env
        ├── Call OpenAI / Claude / Gemini / Ollama
        ├── Handle errors (timeout, rate limit, bad key)
        │
        ▼
database.py
        │
        ├── save_query(input, action_type)
        ├── save_response(record_id, ai_response)   ← NEW
        │
        ▼
main.py prints AI explanation to terminal
```

---

## Database Changes (Phase 2)

Extend the existing table or add a related table for AI output.

### Option A — Add columns (simple, recommended to start)

```sql
ALTER TABLE developer_queries ADD COLUMN ai_response TEXT;
ALTER TABLE developer_queries ADD COLUMN ai_provider TEXT;
ALTER TABLE developer_queries ADD COLUMN model TEXT;
```

| Column | Purpose |
|--------|---------|
| `ai_response` | Full text returned by the AI |
| `ai_provider` | e.g. `openai`, `anthropic`, `ollama` |
| `model` | e.g. `gpt-4o-mini`, `claude-3-haiku` |

### Option B — Separate table (better for long responses / retries)

```sql
CREATE TABLE ai_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER NOT NULL,
    response TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT,
    tokens_used INTEGER,
    created_on TEXT NOT NULL,
    FOREIGN KEY (query_id) REFERENCES developer_queries(id)
);
```

Start with **Option A** unless you need retry history or token tracking from day one.

---

## AI Provider Layer

One module should talk to all providers so feature code stays simple.

```text
services/ai_provider.py
        │
        ├── get_client()           # reads .env, returns configured client
        ├── complete(prompt)       # single entry point for all features
        └── Supported providers:
              ├── openai
              ├── anthropic
              ├── google (gemini)
              └── ollama (local, no API key)
```

### Example usage inside a feature service

```python
from services.ai_provider import complete

def explain_error(user_input: str) -> str:
    prompt = load_template("explain_error") + "\n\n" + user_input
    return complete(prompt)
```

---

## Environment Variables

Copy `.env.example` to `.env` and set one provider:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Optional overrides
OPENAI_MODEL=gpt-4o-mini
REQUEST_TIMEOUT=60
```

| Provider | Required variables |
|----------|-------------------|
| OpenAI | `AI_PROVIDER=openai`, `OPENAI_API_KEY` |
| Anthropic | `AI_PROVIDER=anthropic`, `ANTHROPIC_API_KEY` |
| Google Gemini | `AI_PROVIDER=google`, `GOOGLE_API_KEY` |
| Ollama (local) | `AI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434` |

---

## Dependencies to Install (Phase 2)

Add to `requirements.txt` (exact versions can be pinned later):

```text
python-dotenv>=1.0.0
openai>=1.0.0
anthropic>=0.25.0
google-generativeai>=0.5.0
httpx>=0.27.0
```

Install:

```bash
pip install -r requirements.txt
```

For **Ollama** (local models):

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3`
3. Set `AI_PROVIDER=ollama` in `.env`

---

## Prompt Templates

Store prompts in `prompts/` as plain text files — easy to edit without touching Python.

Example `prompts/explain_error.txt`:

```text
You are a senior Python developer helping debug errors.
Explain the following error in plain language.
Include: likely cause, where to look, and a suggested fix.
Keep the answer concise and practical.

Error:
```

Each feature service loads its template, appends user input, and sends the combined string to `ai_provider.complete()`.

---

## Feature → Service Mapping

| Menu # | Feature | Service module | Prompt file |
|--------|---------|----------------|-------------|
| 1 | Explain an Error | `services/explain_error.py` | `prompts/explain_error.txt` |
| 2 | Explain Code | `services/explain_code.py` | `prompts/explain_code.txt` |
| 3 | Improve Code | `services/improve_code.py` | `prompts/improve_code.txt` |
| 4 | Generate Unit Tests | `services/generate_tests.py` | `prompts/generate_tests.txt` |
| 5 | SQL Assistant | `services/sql_assistant.py` | `prompts/sql_assistant.txt` |
| 6 | Regex Generator | `services/regex_generator.py` | `prompts/regex_generator.txt` |
| 7 | Git Assistant | `services/git_assistant.py` | `prompts/git_assistant.txt` |

`main.py` stays thin: validate input → call service → save to DB → print result.

---

## Error Handling Checklist

Phase 2 must handle failures gracefully:

| Scenario | User-facing behavior |
|----------|---------------------|
| Missing `.env` or API key | Clear message: "Set OPENAI_API_KEY in .env" |
| Network timeout | Retry once, then show error |
| Rate limit (429) | Wait and retry, or ask user to try later |
| Empty AI response | Save input only, warn user |
| Invalid provider name | List supported providers |

Never crash the CLI on AI errors — always save the user's input even if the AI call fails.

---

## Suggested Build Order

Build Phase 2 in small steps. Test each step before moving on.

```text
Step 1   config.py + .env loading
   │
Step 2   services/ai_provider.py (one provider first, e.g. OpenAI)
   │
Step 3   prompts/explain_error.txt + services/explain_error.py
   │
Step 4   Wire menu option 1 in main.py → full loop with DB save
   │
Step 5   Add ai_response column to database.py
   │
Step 6   Repeat for options 2–7 (copy pattern from step 3–4)
   │
Step 7   Add Ollama as second provider (optional local dev)
   │
Step 8   Update export to include ai_response
   │
Step 9   Update README and docs
```

---

## Sequence Diagram (One Request)

```text
User          main.py       service          ai_provider       database
  │              │              │                 │                │
  │── choice 1 ─►│              │                 │                │
  │── paste err ─►│              │                 │                │
  │              │── call ───────►│                 │                │
  │              │              │── complete() ──►│                │
  │              │              │                 │── API call ──► (cloud)
  │              │              │◄── response ────│                │
  │              │◄── text ──────│                 │                │
  │              │── save ─────────────────────────────────────────►│
  │◄── print ────│              │                 │                │
```

---

## Testing Before You Ship

Manual checks for each feature:

1. Run with valid API key → get AI response, saved in DB
2. Run with missing key → friendly error, input still saved
3. View history → shows action type, input, and AI response
4. Export session → JSON includes `ai_response` field
5. Switch provider in `.env` → same menu, different backend

Optional later: unit tests with mocked `ai_provider.complete()`.

---

## What Comes After Phase 2 (Preview)

| Phase | Focus |
|-------|--------|
| Phase 3 | Streaming responses (show tokens as they arrive) |
| Phase 4 | Conversation threads (follow-up questions on same record) |
| Phase 5 | Web UI or VS Code extension |
| Phase 6 | AI agents (multi-step: read file → fix → run tests) |

Phase 2 is the foundation. Get one provider and one feature working end-to-end first, then expand.

---

## Quick Start Checklist (When You Begin Phase 2)

- [ ] Read this document fully
- [ ] Create `config.py` and load `.env`
- [ ] Add dependencies to `requirements.txt` and install
- [ ] Create `services/ai_provider.py` with one provider
- [ ] Add `ai_response` column migration in `database.py`
- [ ] Implement `explain_error` end-to-end (menu 1)
- [ ] Test save + view history + export with AI response
- [ ] Copy pattern to menus 2–7
- [ ] Update README and `docs/02_PROJECT_FLOW.md`

---

## Summary

Phase 1 built the **shell**: menu, storage, history, export.  
Phase 2 adds the **brain**: AI provider layer, prompt templates, per-feature services, and stored responses.

Keep `main.py` as the entry point, `database.py` as the only SQL module, and put all AI logic in `services/`. That structure scales cleanly into streaming, agents, and a future web UI.
