from typing import Dict, Optional


class AbortCliMenu(Exception):
    pass


def _print_menu_help(options: Dict[str, str]):
    for action, description in options.items():
        print("%3s: %s" % (action, description))


def menu(prompt: str, options: Dict[str, str], help_cmd: str = 'h') -> str:
    help_cmd_folded = help_cmd.casefold()
    options[help_cmd_folded] = "Display this help"
    options = {k.casefold(): v for k, v in options.items()}

    full_prompt = "%s (%s to display help): " % (prompt, help_cmd)
    try:
        while True:
            action = input(full_prompt)
            action_clean = action.strip().casefold()
            if len(action_clean) < 1:
                continue
            if action_clean not in options.keys():
                print("%s is not a valid option! Use one of: %s" % (action_clean, ', '.join(options.keys())))
                continue
            if action_clean == help_cmd_folded:
                _print_menu_help(options)
                continue
            return action_clean

    except EOFError as e:
        raise AbortCliMenu() from e
    except KeyboardInterrupt as e:
        raise AbortCliMenu() from e


def prompt_int_range(prompt: str, min_value: int, max_value: int, default_value: Optional[int] = None) -> int:
    full_prompt = ("%s (%d - %d) [%d]: " % (prompt, min_value, max_value, default_value)) \
        if default_value is not None \
        else ("%s (%d - %d): " % (prompt, min_value, max_value))

    try:
        while True:
            input_str = input(full_prompt)
            input_str_cleaned = input_str.strip()
            if default_value is not None and len(input_str_cleaned) < 1:
                return default_value

            try:
                input_int = int(input_str_cleaned)
                if input_int not in range(min_value, max_value + 1):
                    print("Input has to be an integer in range %d - %d" % (min_value, max_value))
                    continue
                return input_int

            except ValueError:
                print("Input is not an integer")

    except EOFError as e:
        raise AbortCliMenu() from e
    except KeyboardInterrupt as e:
        raise AbortCliMenu() from e
