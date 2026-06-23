"""Command-line entry point for 神座纪元 v1.1."""

from character import create_character_interactive
from game_state import GameState
from intent_parser import parse_intent
from rule_engine import apply_rule
from save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
from story import render_ending, render_help, render_opening, render_result, render_status, render_title
from utils import CYAN, YELLOW, color_text, print_divider, safe_input


QUIT_COMMANDS = {"退出", "quit", "exit", "q"}
HELP_COMMANDS = {"帮助", "help", "h", "?"}
STATUS_COMMANDS = {"状态", "status", "s"}
SAVE_COMMANDS = {"存档", "save"}
LOAD_COMMANDS = {"读档", "load"}


def create_new_state():
    character = create_character_interactive()
    state = GameState(character)
    print(render_opening(character))
    return state


def create_initial_state():
    if save_exists():
        answer = safe_input("检测到本地存档。输入“读档”继续，直接回车新游戏：").strip().lower()
        if answer in LOAD_COMMANDS or answer in {"读档"}:
            state = load_game()
            print(f"已读取存档：{DEFAULT_SAVE_PATH}")
            return state

    return create_new_state()


def main():
    print(render_title())
    state = create_initial_state()

    while not state.is_game_over:
        print(render_status(state))
        user_text = safe_input(color_text("行动> ", CYAN, bold=True)).strip()

        if not user_text:
            print("你停在原地，雾也停在原地。请输入一个行动，或输入“帮助”。")
            continue

        command = user_text.lower()
        if command in QUIT_COMMANDS or user_text in QUIT_COMMANDS:
            print("你合上冒险日志，暂时离开雾中修道院。")
            break

        if command in HELP_COMMANDS or user_text in HELP_COMMANDS:
            print(render_help())
            continue

        if command in STATUS_COMMANDS or user_text in STATUS_COMMANDS:
            print(render_status(state))
            continue

        if command in SAVE_COMMANDS or user_text in SAVE_COMMANDS:
            save_path = save_game(state)
            print(f"已存档：{save_path}")
            continue

        if command in LOAD_COMMANDS or user_text in LOAD_COMMANDS:
            if not save_exists():
                print("当前没有本地存档。")
                continue
            state = load_game()
            print(f"已读取存档：{DEFAULT_SAVE_PATH}")
            continue

        action = parse_intent(user_text, state.current_location)
        result = apply_rule(state, action)
        print()
        print_divider("=")
        print(color_text("【行动结果】", YELLOW, bold=True))
        print(render_result(result))
        print_divider("=")

        if state.is_game_over:
            print(render_ending(state))


if __name__ == "__main__":
    main()
