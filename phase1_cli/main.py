"""Command-line entry point for 神座纪元 v5.8.0."""

import os

if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from phase1_cli.character import build_character
    from phase1_cli.data import CLASSES, GODS
    from phase1_cli.game_service import handle_player_input, should_use_agentic_runtime_for_state
    from phase1_cli.game_state import GameState
    from phase1_cli.save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
    from phase1_cli.scenarios import (
        WORLD_GAME_MODE,
        background_names,
        background_options,
        city_names_for_origin,
        configure_character_for_game_mode,
        ethnicity_names_for_origin,
        ethnicity_options_for_origin,
        game_mode_from_env,
        get_origin_country,
        is_world_mode_state,
        origin_country_ids,
    )
    from phase1_cli.story import render_opening, render_status, render_title
    from phase1_cli.utils import CYAN, YELLOW, color_text, numbered_choice, print_divider, safe_input
else:
    from .character import build_character
    from .data import CLASSES, GODS
    from .game_service import handle_player_input, should_use_agentic_runtime_for_state
    from .game_state import GameState
    from .save_manager import DEFAULT_SAVE_PATH, load_game, save_exists, save_game
    from .scenarios import (
        WORLD_GAME_MODE,
        background_names,
        background_options,
        city_names_for_origin,
        configure_character_for_game_mode,
        ethnicity_names_for_origin,
        ethnicity_options_for_origin,
        game_mode_from_env,
        get_origin_country,
        is_world_mode_state,
        origin_country_ids,
    )
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


def choose_origin_country():
    print("\n请选择出身国家（当前开放八个重要国家）：")
    country_ids = origin_country_ids()
    for index, country_id in enumerate(country_ids, start=1):
        country = get_origin_country(country_id)
        print(f"{index}. {country['formal_name']} / {country['identity']} - {country['summary']}")

    while True:
        answer = safe_input("输入国家编号或国家名称：").strip()
        if answer.isdigit():
            index = int(answer) - 1
            if 0 <= index < len(country_ids):
                return country_ids[index]

        for country_id in country_ids:
            country = get_origin_country(country_id)
            if answer in {country_id, country["name"], country["formal_name"], country["identity"]}:
                return country_id

        print("没有找到这个国家，请重新输入。")


def choose_origin_city(country_id):
    country = get_origin_country(country_id)
    print(f"\n请选择开局城市（{country['formal_name']}）：")
    for index, city in enumerate(country["cities"], start=1):
        title_text = f" / {city['title']}" if city["title"] else ""
        print(f"{index}. {city['name']}{title_text} - {city['description']}")

    city_names = city_names_for_origin(country_id)
    return numbered_choice(city_names, "输入城市编号或完整名称：")


def choose_origin_ethnicity(country_id):
    ethnicities = ethnicity_options_for_origin(country_id)
    if not ethnicities:
        return None

    print("\n请选择民族：")
    for index, ethnicity in enumerate(ethnicities, start=1):
        print(f"{index}. {ethnicity['name']} - {ethnicity['description']}")

    ethnicity_names = ethnicity_names_for_origin(country_id)
    return numbered_choice(ethnicity_names, "输入民族编号或完整名称：")


def choose_background():
    print("\n请选择开局身份：")
    for index, background in enumerate(background_options(), start=1):
        print(f"{index}. {background['name']} - {background['description']}")

    return numbered_choice(background_names(), "输入身份编号或完整名称：")


def choose_world_origin():
    country_id = choose_origin_country()
    city_name = choose_origin_city(country_id)
    ethnicity_name = choose_origin_ethnicity(country_id)
    background_name = choose_background()
    return country_id, city_name, ethnicity_name, background_name


def create_character_interactive():
    print_divider("=")
    print("创建角色")
    print_divider("=")
    name = safe_input("请输入角色名：").strip() or "无名冒险者"
    class_id = choose_class()
    god = choose_god()
    character = build_character(name, class_id, god)
    game_mode = game_mode_from_env()
    origin_country_id = None
    origin_city = None
    origin_ethnicity = None
    background_name = None
    if game_mode == WORLD_GAME_MODE:
        origin_country_id, origin_city, origin_ethnicity, background_name = choose_world_origin()
    configure_character_for_game_mode(
        character,
        game_mode,
        origin_country_id,
        origin_city,
        origin_ethnicity,
        background_name,
    )

    print("\n角色创建完成：")
    print(f"- 名字：{character.name}")
    print(f"- 职业：{character.class_name}")
    print(f"- 信仰：{character.god}")
    print(f"- 模式：{character.flags['game_mode']}")
    if character.flags["game_mode"] == WORLD_GAME_MODE:
        print(f"- 出身：{character.flags['origin_country_formal_name']} / {character.flags['origin_identity']}")
        print(f"- 民族：{character.flags['origin_ethnicity']}")
        print(f"- 开局城市：{character.flags['origin_city']}")
        print(f"- 身份：{character.flags['background_name']}")
    print(f"- 六属性：{character.attributes}")
    print(f"- HP/SAN：{character.hp}/{character.san}")
    print(f"- 初始道具：{', '.join(character.inventory)}")
    return character


def create_new_state():
    character = create_character_interactive()
    state = GameState(character)
    print(render_opening(character, character.flags.get("game_mode")))
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
    return os.getenv("PANTHEON_SHOW_RUNTIME", "").strip().lower() in TRUTHY_VALUES


def should_use_llm():
    return os.getenv("PANTHEON_USE_LLM", "").strip().lower() in TRUTHY_VALUES


def should_use_plain_prompt(state=None):
    return (
        os.getenv("PANTHEON_PLAIN_PROMPT", "").strip().lower() in TRUTHY_VALUES
        or (state is not None and is_world_mode_state(state))
    )


def action_prompt(state=None):
    if should_use_plain_prompt(state):
        return "你> "
    return color_text("行动> ", CYAN, bold=True)


def print_runtime_debug(response):
    if not should_show_runtime_debug() or not response.llm_runtime:
        return

    runtime = response.llm_runtime
    if runtime.get("phase") == "phase5-agentic-runtime":
        print_agentic_runtime_debug(runtime["agentic_runtime"])
        return

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


def print_agentic_runtime_debug(runtime):
    print(color_text("【Phase 5 Agentic Runtime】", CYAN, bold=True))
    providers = runtime["providers"]
    open_action = runtime["open_action"]
    adjudication = runtime["adjudication"]
    commit = runtime["commit"]
    observability = runtime.get("observability", {})
    trace = runtime.get("runtime_trace", {})
    if trace:
        steps = ", ".join(
            f"{step['name']}={step['elapsed_ms']}ms"
            for step in trace.get("steps", ())
        )
        print(
            f"- trace: branch={trace.get('branch')}, "
            f"total={trace.get('total_ms')}ms, steps={steps}"
        )
    if observability:
        slowest = observability.get("trace", {}).get("slowest_step") or {}
        print(
            f"- observability: schema={observability.get('schema_version')}, "
            f"failed_validations={observability.get('validations', {}).get('failed_count')}, "
            f"memory_writes={observability.get('memory', {}).get('written_record_count')}, "
            f"slowest={slowest.get('name')}:{slowest.get('elapsed_ms')}ms"
        )
    print(
        f"- providers: intent={providers['intent_agent']}, "
        f"bundle={providers['world_bundle']}, scene={providers['scene_agent']}, "
        f"arbiter={providers['rule_arbiter']}, model={providers['model']}"
    )
    print(f"- runtime: llm_enabled={providers['llm_enabled']}, reason={providers['reason']}")
    print(f"- open action: primary_goal={open_action['primary_goal']}, method={open_action['method']}")
    print(
        f"- adjudication: action_type={adjudication['action_type']}, "
        f"allowed_effects={adjudication['allowed_effects']}"
    )
    print(
        f"- generated: npcs={len(runtime['npcs'])}, "
        f"events={len(runtime['events'])}, items={len(runtime['items'])}"
    )
    print(f"- commit: committed={commit['committed']}, effects={commit['committed_effects']}")
    for key, validation in runtime["validations"].items():
        if not validation["is_valid"]:
            print(f"- validation warning [{key}]: {validation['errors']}")
    for error in runtime["errors"]:
        print(f"- runtime warning: {error}")


def main():
    print(render_title())
    state = create_initial_state()

    while not state.is_game_over:
        if not is_world_mode_state(state):
            print(render_status(state))
        user_text = safe_input(action_prompt(state)).strip()
        if should_use_agentic_runtime_for_state(state) and user_text:
            print("主持人思考中...")
        elif should_use_llm() and user_text:
            print("主持人思考中...")
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
            if is_world_mode_state(response.state):
                print(response.text)
            else:
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
