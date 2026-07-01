"""Application entry point for the AI Developer Assistant CLI."""

from __future__ import annotations

import sqlite3

import database
from database import MAX_QUERY_LENGTH
from config import load_ai_config
from services.ai_manager import complete
from services.feature_services import explain_error_service, sql_assistant_service

import logger


def print_result(message: str) -> None:
    """Print an operation outcome in a consistent Result block."""
    print("\n*********** Result ***********")
    print(message)
    print("******************************\n")


def user_input_menu() -> int:
    print("\n====================================================")
    print("        🤖 AI Developer Assistant")
    print("====================================================")
    print("1. Explain an Error")
    print("2. Explain Code")
    print("3. Improve Code")
    print("4. Generate Unit Tests")
    print("5. SQL Assistant")
    print("6. Regex Generator")
    print("7. Git Assistant")
    print("8. Save & View History")
    print("9. Export Session")
    print("10. Exit")

    print("\n👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇")
    return int(input("Enter your choice : "))


def history_menu() -> None:
    """Show history management submenu."""
    while True:
        print("\n====================================================")
        print("           📜 Save & View History")
        print("====================================================")
        print("1. View History")
        print("2. Delete History by ID")
        print("3. Delete All History")
        print("4. Back to Main Menu")

        print("\n👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇")
        choice = input("Enter your choice : ").strip()

        match choice:
            case "1":
                view_history()
            case "2":
                delete_history_by_id()
            case "3":
                delete_all_history()
            case "4":
                return
            case _:
                print_result("Invalid choice. Please try again.")


def prompt_multiline_input(prompt: str) -> str:
    """Read multiline input until the user enters a blank line."""
    print(prompt)
    lines: list[str] = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def print_query_record(
    record_id: int,
    action_type: str,
    query: str,
    created_on: str,
    ai_response: str | None = None,
    ai_provider: str | None = None,
    model: str | None = None,
) -> None:
    """Print a single saved record in a readable format."""
    label = database.get_action_label(action_type)
    print(f"\n------------------- ID : {record_id} -------------------")
    print(f"Action:   {label}")
    print(f"Saved on: {created_on}")
    print(f"Content:\n{query}")

    if ai_response:
        print(f"\nAI Provider: {ai_provider or '-'}")
        print(f"Model:       {model or '-'}")
        print("AI Response:\n" + ai_response)


def save_action_input(
    action_type: str, action_label: str, input_prompt: str
) -> int | None:
    """Save user input for a menu action and return the record id (or None)."""
    print(f"\n--- {action_label} ---")
    print("Phase 1 saves your input locally. AI responses arrive in Phase 2.")

    content = prompt_multiline_input(input_prompt)

    if not content.strip():
        print_result("Nothing was saved. The input was empty.")
        return None

    if len(content) > MAX_QUERY_LENGTH:
        print_result(
            f"Input is too large ({len(content):,} characters). "
            f"Maximum allowed is {MAX_QUERY_LENGTH:,} characters."
        )
        return None

    try:
        record_id = database.save_query(content, action_type=action_type)
    except sqlite3.Error as exc:
        print_result(f"Could not save input: {exc}")
        return None

    print_result(f"Saved successfully under '{action_label}'. Record ID: {record_id}")
    return record_id


def _run_ai_for_record(
    record_id: int,
    action_type: str,
    user_input: str,
    prompt_func,
) -> None:
    """Call AI for a saved record and persist the response.

    Notes:
    - The CLI must not crash on AI failures.
    - The user's input must already be saved.
    """

    # Resolve provider/config early for friendly error messages.
    try:
        cfg = load_ai_config()
    except ValueError as exc:
        print_result(f"AI configuration error: {exc}")
        return

    logger.info(f"AI request started. provider = {cfg.provider}")

    try:
        ai_response = prompt_func(user_input)
        logger.info("AI response received")

        # Persist AI output.
        database.save_ai_response(
            record_id=record_id,
            ai_response=ai_response,
            ai_provider=cfg.provider,
            model=cfg.model,
        )

        print("\n--- AI Response ---")
        print(ai_response)

        # Keep AI response visible, but wrap the operation outcome consistently.
        print_result("AI response generated and saved successfully.")

    except (ValueError, sqlite3.Error) as exc:
        # ValueError covers invalid provider/settings and empty input validation.
        print_result(f"AI failed: {exc}")
    except Exception as exc:  # noqa: BLE001 - keep CLI resilient
        # Catch-all to avoid crashing the app.
        print_result(f"AI request failed due to an unexpected error: {exc}")


def explain_error() -> None:
    record_id = save_action_input(
        "explain_error",
        "Explain an Error",
        "Paste your error or stack trace (press Enter twice to finish):",
    )
    if record_id is None:
        return

    user_input = database.get_all_queries()[0][2]  # simplest: re-read latest query

    _run_ai_for_record(
        record_id=record_id,
        action_type="explain_error",
        user_input=user_input,
        prompt_func=explain_error_service,
    )


def explain_code() -> None:
    # Phase 2: must keep existing Phase 1 behavior.
    save_action_input(
        "explain_code",
        "Explain Code",
        "Paste the code you want explained (press Enter twice to finish):",
    )


def improve_code() -> None:
    save_action_input(
        "improve_code",
        "Improve Code",
        "Paste the code you want to improve (press Enter twice to finish):",
    )


def generate_unit_tests() -> None:
    save_action_input(
        "generate_tests",
        "Generate Unit Tests",
        "Paste the code to generate tests for (press Enter twice to finish):",
    )


def sql_assistant() -> None:
    record_id = save_action_input(
        "sql_assistant",
        "SQL Assistant",
        "Paste your SQL query or question (press Enter twice to finish):",
    )
    if record_id is None:
        return

    user_input = database.get_all_queries()[0][2]

    _run_ai_for_record(
        record_id=record_id,
        action_type="sql_assistant",
        user_input=user_input,
        prompt_func=sql_assistant_service,
    )


def regex_generator() -> None:
    save_action_input(
        "regex_generator",
        "Regex Generator",
        "Describe the pattern you need (press Enter twice to finish):",
    )


def git_assistant() -> None:
    save_action_input(
        "git_assistant",
        "Git Assistant",
        "Paste Git output, error, or question (press Enter twice to finish):",
    )


def view_history() -> None:
    """Display all saved records."""
    try:
        rows = database.get_all_queries()
    except sqlite3.Error as exc:
        print_result(f"Could not load history: {exc}")
        return

    if not rows:
        print_result("No history found.")
        return

    print(f"\n************* Showing {len(rows)} record(s) *************")
    for (
        record_id,
        action_type,
        query,
        created_on,
        ai_response,
        ai_provider,
        model,
    ) in rows:
        print_query_record(
            record_id,
            action_type,
            query,
            created_on,
            ai_response,
            ai_provider,
            model,
        )


def delete_history_by_id() -> None:
    """Delete a single history record by its ID."""
    raw_id = input("Enter the ID to delete: ").strip()
    if not raw_id.isdigit():
        print_result("Invalid ID. Please enter a number.")
        return

    record_id = int(raw_id)

    try:
        if not database.query_exists(record_id):
            print_result("No record found with that ID.")
            return

        deleted = database.delete_query(record_id)
    except sqlite3.Error as exc:
        print_result(f"Could not delete record: {exc}")
        return

    if deleted:
        print_result(f"Record {record_id} deleted.")
    else:
        print_result("No record found with that ID.")


def delete_all_history() -> None:
    """Delete all history records after user confirmation."""
    confirm = (
        input("Delete ALL history? This cannot be undone. (yes/no): ").strip().lower()
    )

    if confirm != "yes":
        print_result("Delete all cancelled.")
        return

    try:
        removed = database.delete_all_queries()
    except sqlite3.Error as exc:
        print_result(f"Could not delete history: {exc}")
        return

    print_result(f"Deleted {removed} record(s).")


def export_session() -> None:
    """Export all saved records to a JSON file."""
    try:
        rows = database.get_all_queries()
    except sqlite3.Error as exc:
        print_result(f"Could not load history for export: {exc}")
        return

    if not rows:
        print_result("No history to export.")
        return

    try:
        export_path = database.export_session()
    except (sqlite3.Error, OSError) as exc:
        print_result(f"Could not export session: {exc}")
        return

    print(f"Exported {len(rows)} record(s) to:\n{export_path}")


def main() -> None:
    """Run the CLI application."""
    try:
        database.initialize_database()
    except sqlite3.Error as exc:
        print_result(f"Could not initialize database: {exc}")
        return

    action_handlers = {
        1: explain_error,
        2: explain_code,
        3: improve_code,
        4: generate_unit_tests,
        5: sql_assistant,
        6: regex_generator,
        7: git_assistant,
        8: history_menu,
        9: export_session,
        10: lambda: None,
    }

    try:
        while True:
            try:
                choice = user_input_menu()
            except ValueError:
                print_result("Invalid choice. Please enter a number.")
                continue

            if choice == 10:
                print("\nExiting application...")
                return

            handler = action_handlers.get(choice)
            if handler is None:
                print_result("Invalid choice. Please try again.")
                continue

            handler()
    finally:
        database.close_database()


if __name__ == "__main__":
    main()
