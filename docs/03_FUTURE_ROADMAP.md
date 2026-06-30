# Future Roadmap

This document lists planned phases. **Phase 1 is implemented today.**

For a detailed Phase 2 build guide (architecture, flow, dependencies), see **[04_PHASE2_AI_PLAN.md](04_PHASE2_AI_PLAN.md)**.

---

## Phase 1: Foundation (Current)

- Full CLI menu (10 options)
- SQLite storage with action types
- History management (view, delete)
- Session export to JSON

```text
User → CLI Menu → database.py → SQLite
                  exports/     → JSON files
```

---

## Phase 2: AI Integration

**Goal:** Connect menu actions 1–7 to AI providers and store responses.

- `services/ai_provider.py` — unified client for OpenAI, Claude, Gemini, Ollama
- Prompt templates in `prompts/`
- One service module per feature
- Extend database with `ai_response` column

**Start here:** [04_PHASE2_AI_PLAN.md](04_PHASE2_AI_PLAN.md)

---

## Phase 3: Streaming & UX

**Goal:** Stream AI responses token-by-token in the terminal.

---

## Phase 4: Conversation Threads

**Goal:** Follow-up questions on the same saved record.

---

## Phase 5: Web UI

**Goal:** Browser-based interface sharing the same backend.

---

## Phase 6: AI Agents

**Goal:** Multi-step agentic workflows (read files, suggest fixes, run commands).

---

## Architecture Vision

```text
Phase 1 (now):     main.py → database.py
Phase 2:           main.py → services/ → ai_provider → database.py
Phase 3+:          + streaming, threads, optional web layer
```

Phase 1 stays intentionally complete on its own so you can learn storage and CLI patterns before adding AI complexity.
