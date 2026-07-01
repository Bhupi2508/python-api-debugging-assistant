# Beginner Guide: How Data Flows Through This Project (Phase 2)

This document is written for a Python beginner. It explains **where the data goes** and **what each file does**.

## 1) Folder overview

- `main.py`

  - The command-line menu.
  - Reads what the user types.
  - Calls the correct feature.
  - Prints the results.

- `database.py`

  - All SQLite operations (create table, save input, list history, export).
  - Also stores AI output fields: `ai_response`, `ai_provider`, `model`.

- `config.py`

  - Loads environment variables from `.env`.
  - Produces a small `AIConfig` object (provider name, model, timeout).

- `services/`

  - AI logic lives here.
  - The CLI does not call Ollama directly.

- `services/ai_manager.py`

  - The “router”.
  - Reads config and creates the configured provider implementation.
  - Calls `provider.complete(prompt)`.

- `services/feature_services.py`

  - Feature-level code.
  - Loads the prompt template from `prompts/`.
  - Inserts the user input into the template.
  - Calls `services.ai_manager.complete()`.

- `services/providers/ollama_provider.py`

  - The actual HTTP call to Ollama.
  - This returns only text.

- `prompts/`

  - Plain text prompt templates.
  - Easy to edit later.

- `logger.py`
  - Very small log helpers.
  - Prints timestamps.

## 2) Execution flow diagram (Explain an Error)

### Step-by-step

1. **User chooses menu option 1** in `main.py`.
2. `main.py`
   - asks the user to paste the error
   - saves the pasted text using `database.save_query()`
3. `main.py`
   - calls `services.feature_services.explain_error_service()`
4. `services.feature_services`
   - loads `prompts/explain_error.txt`
   - fills `{input}` with what the user pasted
   - calls `services.ai_manager.complete(prompt)`
5. `services.ai_manager`
   - loads `.env` using `config.load_ai_config()`
   - creates the configured provider (`OllamaProvider` in this phase)
   - calls `provider.complete(prompt)`
6. `services/providers/ollama_provider.py`
   - sends HTTP request to `http://.../api/generate`
   - returns response text
7. `main.py`
   - saves response into SQLite using `database.save_ai_response()`
   - prints the AI response

## 3) Execution flow diagram (SQL Assistant)

The SQL Assistant is the same pipeline:

- Menu option 5 → `database.save_query()` → `sql_assistant_service()` → prompt template from `prompts/sql_assistant.txt`
- `ai_manager` routes to provider
- provider returns text
- `database.save_ai_response()` stores it
- response prints to the terminal

## 4) What is stored in SQLite?

`database.py` creates table `developer_queries` with these key columns:

- `id`
- `action_type` (example: `explain_error`, `sql_assistant`)
- `query` (the user input)
- `created_on`

Phase 2 adds AI fields:

- `ai_response`
- `ai_provider`
- `model`

## 5) How to run

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` from `.env.example`
3. Ensure Ollama is running locally (Phase 2 currently uses Ollama)
4. Run: `python main.py`

## 6) Adding a new AI provider later (simple idea)

To add a new provider in the future:

1. Create `services/providers/<new_provider>_provider.py`
2. Make it implement the `AIProvider` interface by providing `complete(prompt: str) -> str`.
3. Update `services/ai_manager.py` to route `config.provider` to your new class.

The CLI and feature services should not need changes.
