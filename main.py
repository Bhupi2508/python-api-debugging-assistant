"""Application entry point for the AI Developer Assistant CLI."""

import sqlite3

import database
from database import MAX_QUERY_LENGTH


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
    print("====================================================")

    return int(input("Enter your choice: "))


def history_menu() -> None:
    """Show history management submenu."""
    while True:
        print("\n--- Save & View History ---")
        print("1. View History")
        print("2. Delete History by ID")
        print("3. Delete All History")
        print("4. Back to Main Menu")

        choice = input("Enter your choice: ").strip()

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
                print("Invalid choice. Please try again.")


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
) -> None:
    """Print a single saved query in a readable format."""
    label = database.get_action_label(action_type)
    print("-" * 52)
    print(f"ID:       {record_id}")
    print(f"Action:   {label}")
    print(f"Saved on: {created_on}")
    print(f"Content:\n{query}")


def save_action_input(action_type: str, action_label: str, input_prompt: str) -> None:
    """Save user input for a menu action."""
    print(f"\n--- {action_label} ---")
    print("Phase 1 saves your input locally. AI responses arrive in Phase 2.")

    content = prompt_multiline_input(input_prompt)

    if not content.strip():
        print("Nothing was saved. The input was empty.")
        return

    if len(content) > MAX_QUERY_LENGTH:
        print(
            f"Input is too large ({len(content):,} characters). "
            f"Maximum allowed is {MAX_QUERY_LENGTH:,} characters."
        )
        return

    try:
        record_id = database.save_query(content, action_type=action_type)
    except sqlite3.Error as exc:
        print(f"Could not save input: {exc}")
        return

    print(f"Saved successfully under '{action_label}'. Record ID: {record_id}")


def explain_error() -> None:
    save_action_input(
        "explain_error",
        "Explain an Error",
        "Paste your error or stack trace (press Enter twice to finish):",
    )


def explain_code() -> None:
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
    save_action_input(
        "sql_assistant",
        "SQL Assistant",
        "Paste your SQL query or question (press Enter twice to finish):",
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
    """Display all saved queries."""
    try:
        rows = database.get_all_queries()
    except sqlite3.Error as exc:
        print(f"Could not load history: {exc}")
        return

    if not rows:
        print("No history found.")
        return

    print(f"\nShowing {len(rows)} record(s):\n")
    for record_id, action_type, query, created_on in rows:
        print_query_record(record_id, action_type, query, created_on)


def delete_history_by_id() -> None:
    """Delete a single history record by its ID."""
    raw_id = input("Enter the ID to delete: ").strip()
    if not raw_id.isdigit():
        print("Invalid ID. Please enter a number.")
        return

    record_id = int(raw_id)

    try:
        if not database.query_exists(record_id):
            print("No record found with that ID.")
            return

        deleted = database.delete_query(record_id)
    except sqlite3.Error as exc:
        print(f"Could not delete record: {exc}")
        return

    if deleted:
        print(f"Record {record_id} deleted.")
    else:
        print("No record found with that ID.")


def delete_all_history() -> None:
    """Delete all history records after user confirmation."""
    confirm = input(
        "Delete ALL history? This cannot be undone. (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Delete all cancelled.")
        return

    try:
        removed = database.delete_all_queries()
    except sqlite3.Error as exc:
        print(f"Could not delete history: {exc}")
        return

    print(f"Deleted {removed} record(s).")


def export_session() -> None:
    """Export all saved records to a JSON file."""
    try:
        rows = database.get_all_queries()
    except sqlite3.Error as exc:
        print(f"Could not load history for export: {exc}")
        return

    if not rows:
        print("No history to export.")
        return

    try:
        export_path = database.export_session()
    except (sqlite3.Error, OSError) as exc:
        print(f"Could not export session: {exc}")
        return

    print(f"Exported {len(rows)} record(s) to:\n{export_path}")


def main() -> None:
    """Run the CLI application."""
    try:
        database.initialize_database()
    except sqlite3.Error as exc:
        print(f"Could not initialize database: {exc}")
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
                print("Invalid choice. Please enter a number.")
                continue

            if choice == 10:
                print("\nExiting application...")
                return

            handler = action_handlers.get(choice)
            if handler is None:
                print("Invalid choice. Please try again.")
                continue

            handler()
    finally:
        database.close_database()


if __name__ == "__main__":
    main()
