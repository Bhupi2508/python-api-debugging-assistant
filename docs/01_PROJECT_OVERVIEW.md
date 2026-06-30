# Project Overview

## What is this project?

**AI Developer Assistant (CLI)** is a Python command-line application that helps developers capture, store, and manage developer-related content locally using SQLite.

In **Phase 1**, the project provides:

- A full CLI menu with 7 developer action types
- SQLite storage for all user input
- History management (view, delete)
- Session export to JSON

AI responses are **planned for Phase 2** — see [04_PHASE2_AI_PLAN.md](04_PHASE2_AI_PLAN.md).

---

## Project Purpose

Developers often work with text that is useful to keep:

- Stack traces and error messages
- Code snippets to explain or improve
- SQL queries
- Regex pattern requirements
- Git command output and errors
- Code that needs unit tests

This tool stores that content with a labeled action type, so nothing is lost between sessions and you are ready to plug in AI in Phase 2.

---

## Current Implementation (Phase 1)

```text
main.py
  └── user_input_menu() → feature handlers
  └── database.py → SQLite (database/developer_history.db)
  └── exports/ → JSON session exports
```

**Working today:**

| # | Feature | Phase 1 behavior |
|---|---------|------------------|
| 1 | Explain an Error | Save error/stack trace |
| 2 | Explain Code | Save code snippet |
| 3 | Improve Code | Save code to improve |
| 4 | Generate Unit Tests | Save code for test generation |
| 5 | SQL Assistant | Save SQL query or question |
| 6 | Regex Generator | Save pattern description |
| 7 | Git Assistant | Save Git output or question |
| 8 | Save & View History | View, delete by ID, delete all |
| 9 | Export Session | Export all records to JSON |
| 10 | Exit | Close application |

---

## Future Vision

**Phase 2** connects each menu action to AI providers (OpenAI, Claude, Gemini, Ollama) and stores AI responses alongside user input.

Later phases may add streaming, conversation threads, and agentic workflows.
