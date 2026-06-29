from services.database_service import (
    add_and_check_error,
    delete_data,
    get_all_data,
    init_db,
)


def user_input_menu() -> int:
    print("\n==============================")
    print("        MAIN MENU")
    print("==============================")
    print("1. Get All Data")
    print("2. Add Data / Check Error")
    print("3. Delete Data by ID")
    print("4. Exit")
    print("==============================")
    return int(input("Enter your choice: "))


def prompt_multiline_error() -> str:
    print("Paste your errors (Press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    init_db()
    while True:
        choice = user_input_menu()
        match choice:
            case 1:
                rows = get_all_data()
                if not rows:
                    print("No records found.")
                else:
                    for row in rows:
                        print(row)
            case 2:
                payload = prompt_multiline_error()
                add_and_check_error(payload)
                print("Saved.")
            case 3:
                id_to_delete = int(input("Enter the ID to delete: "))
                deleted = delete_data(id_to_delete)
                print("Deleted." if deleted else "No record found with that ID.")
            case 4:
                print("Exiting Application...")
                return
            case _:
                print("Invalid Choice. Please try again.")


if __name__ == "__main__":
    main()
