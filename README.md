# AI Developer Assistant (CLI)

A beginner-friendly **command-line tool** for capturing developer-related content locally using **SQLite**.

Phase 1 provides the full menu shell — all actions save input with labeled action types. **AI responses arrive in Phase 2.**

---

## Project Overview

Developers often collect useful context: stack traces, code snippets, SQL queries, regex needs, Git issues, and more. This tool lets you **save that content by action type**, **view history**, **delete records**, and **export sessions**.

Content is stored exactly as you paste it. Phase 2 will send that content to AI providers and store the responses.

---

## Current Functionality (Phase 1)

| Option | Description |
|--------|-------------|
| 1. Explain an Error | Save an error or stack trace |
| 2. Explain Code | Save a code snippet to explain |
| 3. Improve Code | Save code you want improved |
| 4. Generate Unit Tests | Save code for test generation |
| 5. SQL Assistant | Save a SQL query or question |
| 6. Regex Generator | Save a pattern description |
| 7. Git Assistant | Save Git output or a question |
| 8. Save & View History | View, delete by ID, or delete all |
| 9. Export Session | Export all records to JSON |
| 10. Exit | Close the application |

---

## Folder Structure

```text
python-api-debugging-assistant/
├── main.py                 # Application entry point and CLI menu
├── database.py             # SQLite layer (all SQL lives here)
├── requirements.txt
├── README.md
├── LICENSE
├── .env.example            # Template for Phase 2 AI configuration
├── database/
│   └── developer_history.db   # Created at runtime (not tracked by git)
├── exports/                   # Session exports (created at runtime)
└── docs/
    ├── 01_PROJECT_OVERVIEW.md
    ├── 02_PROJECT_FLOW.md
    ├── 03_FUTURE_ROADMAP.md
    └── 04_PHASE2_AI_PLAN.md   # Detailed Phase 2 build guide
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd python-api-debugging-assistant
```

### 2. Create a virtual environment

macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Phase 1 uses only the Python standard library — no external packages are required.

---

## Running the Project

```bash
python main.py
```

---

## SQLite Database

- **Database file:** `database/developer_history.db` (created automatically on first run)
- **Table:** `developer_queries`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `action_type` | TEXT | Feature label (e.g. `explain_error`) |
| `query` | TEXT | Developer content, stored exactly as entered |
| `created_on` | TEXT | Timestamp (`YYYY-MM-DD HH:MM:SS`) |

---

## Validation

The application includes practical validation:

- Empty input is not saved
- Very large input is rejected (100,000 character limit)
- Invalid menu choices do not crash the app
- Delete by ID checks that the record exists
- Database errors are handled with clear messages

---

## Current Limitations

- No AI responses yet (Phase 2 — see [docs/04_PHASE2_AI_PLAN.md](docs/04_PHASE2_AI_PLAN.md))
- No search or filtering in history
- Single local SQLite database only
- No authentication or multi-user support

---

## Future Roadmap

| Phase | Feature |
|-------|---------|
| 1 | Foundation (current) — menu, SQLite, history, export |
| 2 | AI Integration — providers, prompts, stored responses |
| 3 | Streaming responses |
| 4 | Conversation threads |
| 5 | Web UI |
| 6 | AI Agents |

Details: [docs/03_FUTURE_ROADMAP.md](docs/03_FUTURE_ROADMAP.md)  
Phase 2 build guide: [docs/04_PHASE2_AI_PLAN.md](docs/04_PHASE2_AI_PLAN.md)

---

## Environment Variables (Phase 2)

Phase 1 does not require a `.env` file. When you start Phase 2, copy `.env.example` to `.env` and add your API keys.

See [.env.example](.env.example) for the planned format.

---

## Contributing

Contributions are welcome. Please keep changes focused, beginner-friendly, and aligned with the phased roadmap.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a pull request with a clear description

---

## License

This project is provided under the license described in [LICENSE](LICENSE).
