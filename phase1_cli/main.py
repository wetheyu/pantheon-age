"""Command-line entry point for 神座纪元 v4.7."""

import os

if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from phase1_cli.character import build_character
    from phase1_cli.data import CLASSES, GODS
    from phase1_cli.game_service import handle_player_input
    from phase1_cli.game_state import GameState
    from phase1_cli.save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
    from phase1_cli.story import render_opening, render_status, render_title
    from phase1_cli.utils import CYAN, YELLOW, color_text, numbered_choice, print_divider, safe_input
else:
    from .character import build_character
    from .data import CLASSES, GODS
    from .game_service import handle_player_input
    from .game_state import GameState
    from .save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
    from .story import render_opening, render_status, render_title
    from .utils import CYAN, YELLOW, color_text, numbered_choice, print_divider, safe_input


TRUTHY_VALUES = {"1", "true", "yes", "on"}


def choose_class():
    print("\n请选择职业：")
    class_ids = list(CLASSES.keys())
    for index, class_id in enumerate(class_ids, start=1):
        class_config = CLASSES[class_id]
        print(f"{index}. {class_config['name']} / {class_config['english_name']} - {class_config['description']}")

    while True:
        answer = safe_input("输入职业编号或 class_id：").strip().lower()
        if answer.isdigit():
            index = int(answer) - 1
            if 0 <= index < len(class_ids):
                return class_ids[index]

        for class_id, class_config in CLASSES.items():
            names = {class_id, class_config["name"], class_config["english_name"].lower()}
            if answer in names:
                return class_id

        print("没有找到这个职业，请重新输入。")


def choose_god():
    print("\n请选择信仰神明：")
    for index, god in enumerate(GODS, start=1):
        print(f"{index}. {god}")
    return numbered_choice(GODS, "输入神明编号或完整名称：")


def create_character_interactive():
    print_divider("=")
    print("创建角色")
    print_divider("=")
    name = safe_input("请输入角色名：").strip() or "无名冒险者"
    class_id = choose_class()
    god = choose_god()
    character = build_character(name, class_id, god)

    print("\n角色创建完成：")
    print(f"- 名字：{character.name}")
    print(f"- 职业：{character.class_name}")
    print(f"- 信仰：{character.god}")
    print(f"- 属性：{character.stats}")
    print(f"- HP/SAN：{character.hp}/{character.san}")
    print(f"- 初始道具：{', '.join(character.inventory)}")
    return character


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


def should_show_runtime_debug():
    return (
        os.getenv("PANTHEON_SHOW_RUNTIME", "").strip().lower() in TRUTHY_VALUES
        or os.getenv("PANTHEON_USE_LLM", "").strip().lower() in TRUTHY_VALUES
    )


def should_use_llm():
    return os.getenv("PANTHEON_USE_LLM", "").strip().lower() in TRUTHY_VALUES


def should_use_plain_prompt():
    return os.getenv("PANTHEON_PLAIN_PROMPT", "").strip().lower() in TRUTHY_VALUES


def action_prompt():
    if should_use_plain_prompt():
        return "行动> "
    return color_text("行动> ", CYAN, bold=True)


def print_runtime_debug(response):
    if not should_show_runtime_debug() or not response.llm_runtime:
        return

    runtime = response.llm_runtime
    providers = runtime["providers"]
    action_candidate = runtime["action_candidate"]
    candidate = action_candidate["candidate"]
    adjudication = runtime["adjudication"]["request"]
    narration = runtime["narration"]

    print(color_text("【Phase 4 Runtime】", CYAN, bold=True))
    print(
        f"- providers: action={providers['action_provider']}, "
        f"narration={providers['narration_provider']}, model={providers['model']}"
    )
    print(f"- runtime: llm_enabled={providers['llm_enabled']}, reason={providers['reason']}")
    print(
        f"- candidate: intent={candidate['intent']}, target={candidate['target']}, "
        f"fallback={action_candidate['used_fallback']}"
    )
    for error in action_candidate["validation"]["errors"]:
        print(f"- candidate validation warning: {error}")
    print(
        f"- adjudication: check_type={adjudication['check_type']}, "
        f"requires_check={adjudication['requires_check']}, risk_tags={adjudication['risk_tags']}"
    )
    print(
        f"- narration: source={narration['proposal']['source']}, "
        f"fallback={narration['used_fallback']}"
    )
    for error in runtime["errors"]:
        print(f"- runtime warning: {error}")


def main():
    print(render_title())
    state = create_initial_state()

    while not state.is_game_over:
        print(render_status(state))
        user_text = safe_input(action_prompt()).strip()
        if should_use_llm() and user_text:
            print(color_text("正在调用 Phase 4 Runtime，请稍等...", CYAN))
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
            print_runtime_debug(response)
            if response.ending_text:
                print(response.ending_text)
        else:
            print(response.text)


if __name__ == "__main__":
    main()
