# Project Flow (Phase 1)

This document describes what is implemented in Phase 1.

---

## Application Startup

```text
User
  │
  ▼
Run: python main.py
  │
  ▼
initialize_database() → create table if needed
  │
  ▼
Display Main Menu (user_input_menu)
```

---

## Main Menu Flow

```text
Main Menu
  │
  ├── 1  → Explain an Error        (save input)
  ├── 2  → Explain Code            (save input)
  ├── 3  → Improve Code            (save input)
  ├── 4  → Generate Unit Tests     (save input)
  ├── 5  → SQL Assistant           (save input)
  ├── 6  → Regex Generator         (save input)
  ├── 7  → Git Assistant           (save input)
  ├── 8  → Save & View History     (submenu)
  ├── 9  → Export Session          (JSON file)
  └── 10 → Exit application
```

Options 1–7 save user input to SQLite with an `action_type` label. AI responses are planned for Phase 2.

---

## Save Action Flow (Options 1–7)

```text
User selects feature (e.g. 1)
  │
  ▼
User pastes multiline content (blank line to finish)
  │
  ▼
Validate input (not empty, not too large)
  │
  ▼
save_query(content, action_type) → SQLite
  │
  ▼
Confirmation message with record ID
```

---

## Save & View History (Option 8)

```text
User selects: 8
  │
  ▼
History Submenu
  │
  ├── 1 → View History
  ├── 2 → Delete History by ID
  ├── 3 → Delete All History
  └── 4 → Back to Main Menu
```

---

## View History

```text
User selects: 1 (in history submenu)
  │
  ▼
get_all_queries() → SQLite
  │
  ▼
Print records (newest first, with action type)
```

---

## Export Session (Option 9)

```text
User selects: 9
  │
  ▼
get_all_queries() → SQLite
  │
  ▼
Write exports/session_YYYYMMDD_HHMMSS.json
  │
  ▼
Confirmation message with file path
```

---

## Database Schema

```sql
CREATE TABLE developer_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL DEFAULT 'general',
    query TEXT NOT NULL,
    created_on TEXT NOT NULL
);
```

### Action Types

| action_type | Menu option |
|-------------|-------------|
| `explain_error` | 1. Explain an Error |
| `explain_code` | 2. Explain Code |
| `improve_code` | 3. Improve Code |
| `generate_tests` | 4. Generate Unit Tests |
| `sql_assistant` | 5. SQL Assistant |
| `regex_generator` | 6. Regex Generator |
| `git_assistant` | 7. Git Assistant |
| `general` | Legacy / default |

---

## Module Responsibilities

```text
main.py       → entry point, menu, user input, validation
database.py   → all SQL operations and JSON export
exports/      → exported session files (created at runtime)
```

---

## Phase 2 Preview

See [04_PHASE2_AI_PLAN.md](04_PHASE2_AI_PLAN.md) for the full AI integration plan.
