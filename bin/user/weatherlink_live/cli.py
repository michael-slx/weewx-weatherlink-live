from typing import List, Dict, Optional


class Colors:
    HEADER = '\033[36m'
    OK = '\033[92m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    STANDOUT = '\033[7m'
    END = '\033[0m'


def _display_choices_help(choices: Dict[str, str], help_choice: str) -> None:
    print("")
    print(f"Enter a list of choices separated by colon ({Colors.STANDOUT},{Colors.END}).")
    print(f"Enter a dot ({Colors.STANDOUT}.{Colors.END}) for an empty list.")
    print(f"Enter {Colors.STANDOUT}%s{Colors.END} for help." % help_choice)

    longest_choice = max(*[len(key) for key in choices.keys()])
    format_str = f" • {Colors.BOLD}{Colors.STANDOUT}%{longest_choice}s{Colors.END}: %s"

    print(f"\n{Colors.BOLD}Available choices:{Colors.END}")
    for choice, description in choices.items():
        print(format_str % (choice, description))

    print("")


def _are_all_items_valid_choices(input_list: List[str], choices: Dict[str, str], help_choice: str) -> bool:
    for item in input_list:
        if item not in choices:
            print(
                f"{Colors.FAIL}\"%s\" is not a valid choice!{Colors.END} Enter {Colors.STANDOUT}%s{Colors.END} for help." \
                % (item, help_choice)
            )
            return False

    return True


def prompt_list(prompt: str,
                choices: Dict[str, str],
                default: Optional[List[str]] = None,
                help_choice: str = 'h') -> List[str]:
    default_list_str = ", ".join(default) if default else "."
    prompt_str = (f"{Colors.BOLD}%s{Colors.END} [%s] (%s for help, dot for empty list): " % (prompt,
                                                                                             default_list_str,
                                                                                             help_choice)) \
        if default is not None \
        else (f"{Colors.BOLD}%s{Colors.END} (%s for help, dot for empty list): " % (prompt, help_choice))

    while True:
        input_str = input(prompt_str).strip().casefold()

        if input_str == help_choice:
            _display_choices_help(choices, help_choice)
            continue
        if not input_str:
            break
        if input_str == '.':
            return list()

        input_list = [item.strip() for item in input_str.split(',')]

        if not _are_all_items_valid_choices(input_list, choices, help_choice):
            continue

        return input_list

    return default if default is not None else list()
