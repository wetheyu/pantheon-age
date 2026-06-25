"""Small helper functions shared by the CLI modules."""

import os
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
TRUTHY_VALUES = {"1", "true", "yes", "on"}


def color_text(text, color="", bold=False):
    prefix = ""
    if bold:
        prefix += BOLD
    if color:
        prefix += color
    if not prefix:
        return text
    return f"{prefix}{text}{RESET}"


def clamp(value, minimum, maximum):
    """Keep a number inside a safe range."""
    return max(minimum, min(value, maximum))


def print_divider(char="-", width=60):
    print(char * width)


def safe_input(prompt):
    """Read user input.

    Returning "退出" on EOF makes automated tests and piped demos finish cleanly.
    """
    try:
        if should_use_prompt_toolkit():
            return prompt_toolkit_input(prompt)
        return input(prompt)
    except EOFError:
        return "退出"


def should_use_prompt_toolkit():
    if os.getenv("PANTHEON_SIMPLE_INPUT", "").strip().lower() in TRUTHY_VALUES:
        return False
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return False
    try:
        import prompt_toolkit  # noqa: F401
    except ImportError:
        return False
    return True


def prompt_toolkit_input(prompt_text):
    from prompt_toolkit import prompt
    from prompt_toolkit.formatted_text import ANSI

    return prompt(ANSI(prompt_text))


def numbered_choice(options, prompt):
    """Ask the user to choose from a list by number or exact text."""
    while True:
        answer = safe_input(prompt).strip()
        if answer.isdigit():
            index = int(answer) - 1
            if 0 <= index < len(options):
                return options[index]

        for option in options:
            if answer == option:
                return option

        print("输入没有匹配到选项，请输入编号或完整名称。")
