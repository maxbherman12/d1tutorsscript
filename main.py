from SheetManager import SheetManager

sheet_manager = SheetManager("./keys.json", "Tutoring", "Max", "./clients.txt")

commands = {
    "session": sheet_manager.log_session,
    "get invoice": sheet_manager.get_invoice,
    "log invoice": sheet_manager.log_invoice,
    "open payments": sheet_manager.get_open_payments,
    "stats": sheet_manager.get_payment_totals,
    "edit clients": sheet_manager.edit_clients,
    "quit": quit
}


def commands_to_str():
    ret = ""
    count = 1
    for key, val in commands.items():
        ret += f"\u2023 {key}\n"
        count += 1
    return ret


continue_prgm = True
while continue_prgm:
    response = input("Enter one of the following commands: \n" + commands_to_str()).strip().lower()
    keys = []
    for key, val in commands.items():
        keys.append(key)

    while response not in keys:
        print("Please input one of the available commands")
        response = input(commands_to_str()).strip().lower()

    commands[response]()

    continue_prgm = False

    prompt_continue = input("Would you like to continue? (y or n): ").strip().lower()
    while prompt_continue != "y" and prompt_continue != "n":
        print("You must enter either y or n")
        prompt_continue = input("Would you like to continue? (y or n): ").strip().lower()

    if prompt_continue == "y":
        continue_prgm = True
