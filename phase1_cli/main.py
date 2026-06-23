"""Command-line entry point for 神座纪元 v1.4."""

if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from phase1_cli.character import create_character_interactive
    from phase1_cli.game_service import handle_player_input
    from phase1_cli.game_state import GameState
    from phase1_cli.save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
    from phase1_cli.story import render_opening, render_status, render_title
    from phase1_cli.utils import CYAN, YELLOW, color_text, print_divider, safe_input
else:
    from .character import create_character_interactive
    from .game_service import handle_player_input
    from .game_state import GameState
    from .save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
    from .story import render_opening, render_status, render_title
    from .utils import CYAN, YELLOW, color_text, print_divider, safe_input


def create_new_state():
    character = create_character_interactive()
    state = GameState(character)
    print(render_opening(character))
    return state


def create_initial_state():
    if save_exists():
        answer = safe_input("检测到本地存档。输入“读档”继续，直接回车新游戏：").strip().lower()
        if answer in {"读档", "load"}:
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
        response = handle_player_input(state, user_text)

        if response.should_exit:
            print(response.text)
            break

        if response.should_save:
            save_path = save_game(state)
            print(f"已存档：{save_path}")
            continue

        if response.should_load:
            if not save_exists():
                print("当前没有本地存档。")
                continue
            state = load_game()
            print(f"已读取存档：{DEFAULT_SAVE_PATH}")
            continue

        if response.kind == "action":
            print()
            print_divider("=")
            print(color_text("【行动结果】", YELLOW, bold=True))
            print(response.text)
            print_divider("=")
            if response.ending_text:
                print(response.ending_text)
        else:
            print(response.text)


if __name__ == "__main__":
    main()
