"""Deterministic rule engine for 神座纪元 v1.4.

The key project idea starts here:
- LLM/future story layer can describe events.
- Code decides rolls, HP/SAN changes, items, clues, movement, and endings.
"""

import random

from .data import (
    CLUE_DESCRIPTIONS,
    CORE_TRUTH_CLUES,
    ENDINGS,
    ITEMS,
    LOCATIONS,
    POLLUTION_KEYWORDS,
)
from .utils import clamp


def apply_rule(state, action):
    state.record_turn()
    result = new_result(state, action)

    intent = action["intent"]
    if intent == "move":
        handle_move(state, action, result)
    elif intent == "investigate":
        handle_investigate(state, action, result)
    elif intent == "analyze":
        handle_analyze(state, action, result)
    elif intent == "attack":
        handle_attack(state, action, result)
    elif intent == "pray":
        handle_pray(state, action, result)
    elif intent == "rest":
        handle_rest(state, result)
    elif intent == "use_item":
        handle_use_item(state, action, result)
    elif intent == "stealth":
        handle_stealth(state, result)
    elif intent == "talk":
        handle_talk(state, result)
    else:
        result["messages"].append("雾吞掉了你的声音。系统还不能理解这个行动，可以输入“帮助”查看示例。")

    check_ending(state, result)
    state.add_event("; ".join(result["messages"]))
    return result


def new_result(state, action):
    return {
        "turn": state.turn,
        "intent": action["intent"],
        "raw_text": action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "messages": [],
        "state_changes": [],
        "new_clues": [],
        "roll": None,
        "success": None,
        "ending": None,
    }


def roll_check(state, stat, dc, modifier=0, modifier_label="职业修正"):
    roll = random.randint(1, 20)
    stat_value = state.player.stats.get(stat, 0)
    total = roll + stat_value + modifier
    return {
        "d20": roll,
        "stat": stat,
        "stat_value": stat_value,
        "modifier": modifier,
        "modifier_label": modifier_label,
        "total": total,
        "dc": dc,
        "success": total >= dc,
    }


def best_modifier(player, keys):
    values = [player.rule_modifiers.get(key, 0) for key in keys]
    values.append(0)
    return max(values)


def sum_modifiers(player, keys):
    return sum(player.rule_modifiers.get(key, 0) for key in keys)


def has_pollution_focus(text):
    return any(keyword in text for keyword in POLLUTION_KEYWORDS)


def change_hp(state, amount, result, reason):
    player = state.player
    before = player.hp
    player.hp = clamp(player.hp + amount, 0, player.max_hp)
    record_delta(result, "HP", before, player.hp, reason)


def change_san(state, amount, result, reason):
    player = state.player
    before = player.san
    player.san = clamp(player.san + amount, 0, player.max_san)
    record_delta(result, "SAN", before, player.san, reason)


def change_suspicion(state, amount, result, reason):
    player = state.player
    before = player.suspicion
    player.suspicion = clamp(player.suspicion + amount, 0, 10)
    record_delta(result, "Suspicion", before, player.suspicion, reason)


def change_corruption(state, amount, result, reason):
    player = state.player
    before = player.corruption
    player.corruption = clamp(player.corruption + amount, 0, 10)
    record_delta(result, "Corruption", before, player.corruption, reason)


def record_delta(result, name, before, after, reason):
    delta = after - before
    if delta == 0:
        return
    sign = "+" if delta > 0 else ""
    result["state_changes"].append(f"{name} {sign}{delta}（{reason}）")


def add_clue(state, clue_name, result):
    if state.player.add_clue(clue_name):
        result["new_clues"].append(clue_name)
        description = CLUE_DESCRIPTIONS.get(clue_name, "")
        result["messages"].append(f"你获得线索「{clue_name}」。{description}")
    else:
        result["messages"].append(f"你再次确认了线索「{clue_name}」，但没有发现新的信息。")


def next_archive_clue(state):
    if "被撕掉的档案页" not in state.player.clues:
        return "被撕掉的档案页"
    return "修女失踪名单"


def handle_move(state, action, result):
    current = state.current_location
    target = action["target"]
    exits = LOCATIONS[current]

    if not target:
        result["messages"].append(f"你需要说明要去哪里。当前位置可前往：{', '.join(exits)}。")
        return

    if target == current:
        result["messages"].append(f"你已经在{current}。雾贴着墙壁缓慢流动。")
        return

    if target not in exits:
        result["messages"].append(f"从{current}不能直接前往{target}。可前往：{', '.join(exits)}。")
        return

    state.move_to(target)
    result["location_after"] = target
    result["messages"].append(f"你从{current}来到{target}。")


def handle_investigate(state, action, result):
    if has_pollution_focus(action["raw_text"]):
        handle_pollution_contact(state, result)
        return

    location = state.current_location
    modifier = best_modifier(state.player, ["investigate_bonus", "track_bonus", "scout_bonus"])

    if location == "修道院门口":
        run_location_clue_check(state, result, "intelligence", 12, modifier, "泥泞脚印")
    elif location == "前厅":
        run_location_clue_check(state, result, "intelligence", 12, modifier, "破损圣徽")
    elif location == "祈祷大厅":
        run_location_clue_check(state, result, "intelligence", 13, modifier, "破损圣徽")
    elif location == "旧档案室":
        run_location_clue_check(state, result, "intelligence", 14, modifier, next_archive_clue(state), fail_san_loss=1)
    elif location == "钟楼":
        run_location_clue_check(state, result, "intelligence", 14, modifier, "说谎时响起的钟声", fail_san_loss=1)
    elif location == "地下墓室":
        run_location_clue_check(state, result, "intelligence", 16, modifier, "地下墓室的亡者残响", fail_san_loss=2)


def handle_analyze(state, action, result):
    location = state.current_location
    if location == "地下墓室" or has_pollution_focus(action["raw_text"]):
        handle_pollution_contact(state, result)
        return

    modifier = best_modifier(state.player, ["analyze_bonus", "lore_bonus", "identify_bonus"])

    if location == "旧档案室":
        run_location_clue_check(state, result, "intelligence", 13, modifier, next_archive_clue(state), fail_san_loss=1)
    elif location == "钟楼":
        run_location_clue_check(state, result, "intelligence", 14, modifier, "说谎时响起的钟声", fail_san_loss=1)
    elif location == "祈祷大厅":
        run_location_clue_check(state, result, "intelligence", 13, modifier, "破损圣徽")
    else:
        check = roll_check(state, "intelligence", 12, modifier)
        result["roll"] = check
        result["success"] = check["success"]
        if check["success"]:
            result["messages"].append("你整理出一些局部信息，但这里还没有足够关键的异常痕迹。")
        else:
            result["messages"].append("这些痕迹暂时无法解释。")


def run_location_clue_check(state, result, stat, dc, modifier, clue_name, fail_san_loss=0):
    check = roll_check(state, stat, dc, modifier)
    result["roll"] = check
    result["success"] = check["success"]

    if check["success"]:
        add_clue(state, clue_name, result)
    else:
        result["messages"].append("你没有找到足够明确的线索。")
        if fail_san_loss:
            change_san(state, -fail_san_loss, result, "令人不安的残缺记录")


def handle_pollution_contact(state, result):
    player = state.player
    modifier = best_modifier(player, ["analyze_bonus", "lore_bonus", "identify_bonus"])
    check = roll_check(state, "intelligence", 15, modifier)
    result["roll"] = check
    result["success"] = check["success"]

    san_loss = 1 if check["success"] else 2
    corruption_gain = 1 if check["success"] else 2

    if player.class_id == "mage":
        san_loss += player.rule_modifiers.get("forbidden_knowledge_san_risk", 0)
    if player.class_id == "priest":
        corruption_gain -= player.rule_modifiers.get("corruption_resistance", 0)
    if player.class_id == "alchemist" and check["success"]:
        san_loss = max(0, san_loss - 1)

    change_san(state, -san_loss, result, "接触深渊污染")
    change_corruption(state, corruption_gain, result, "接触深渊污染")

    if check["success"]:
        add_clue(state, "深渊污染痕迹", result)
    else:
        result["messages"].append("黑色痕迹在视线里扭动，你没能稳定理解它。")


def handle_attack(state, action, result):
    location = state.current_location
    dc = 16 if location == "地下墓室" else 14
    modifier = sum_modifiers(state.player, ["attack_bonus", "direct_combat_penalty", "combat_penalty"])
    check = roll_check(state, "strength", dc, modifier)
    result["roll"] = check
    result["success"] = check["success"]

    if check["success"]:
        result["messages"].append("你抓住黑影靠近的一瞬间反击，它像被钟声撕开一样退入雾中。")
        state.player.flags["shadow_defeated"] = True
        if location == "地下墓室":
            add_clue(state, "地下墓室的亡者残响", result)
        else:
            add_clue(state, "破损圣徽", result)
    else:
        result["messages"].append("黑影从破碎长椅后扑出，你的攻击只划开一片冰冷雾气。")
        change_hp(state, -4 if location == "地下墓室" else -3, result, "战斗受伤")
        if location == "地下墓室":
            change_san(state, -1, result, "黑影低语")


def handle_pray(state, action, result):
    location = state.current_location
    player = state.player
    modifier = best_modifier(player, ["pray_bonus", "purify_bonus"])
    check = roll_check(state, "faith", 12, modifier)
    result["roll"] = check
    result["success"] = check["success"]

    if check["success"]:
        if player.corruption > 0:
            change_corruption(state, -1, result, "祈祷净化")
        else:
            change_san(state, 1, result, "祈祷稳定心神")

        if location == "地下墓室":
            add_clue(state, "地下墓室的亡者残响", result)
        elif location == "祈祷大厅":
            add_clue(state, "破损圣徽", result)
        else:
            result["messages"].append(f"你向{player.god}低声祈祷，雾中短暂安静下来。")
    else:
        result["messages"].append("祈祷没有得到明确回应。")
        if location in {"地下墓室", "钟楼"}:
            change_san(state, -1, result, "污染地点的压迫感")


def handle_rest(state, result):
    location = state.current_location
    change_hp(state, 2, result, "短暂休息")
    change_san(state, 1, result, "短暂休息")
    result["messages"].append("你靠在阴冷的墙边休息片刻。雾没有散去，但呼吸稳定了一些。")
    if location == "地下墓室":
        change_san(state, -1, result, "墓室低语打断休息")


def handle_use_item(state, action, result):
    player = state.player
    item_name = action["item"]

    if not item_name:
        result["messages"].append(f"你要使用哪个道具？当前背包：{format_inventory(player.inventory)}。")
        return

    if not player.has_item(item_name):
        result["messages"].append(f"你的背包里没有「{item_name}」。")
        return

    alchemy_bonus = 1 if player.class_id == "alchemist" else 0

    if item_name == "止血药剂":
        change_hp(state, 4 + alchemy_bonus, result, "使用止血药剂")
        consume_item(player, item_name, result)
    elif item_name == "镇静药剂":
        change_san(state, 2 + alchemy_bonus, result, "使用镇静药剂")
        consume_item(player, item_name, result)
    elif item_name == "小瓶圣水":
        change_corruption(state, -2, result, "使用圣水")
        change_san(state, 1, result, "圣水带来的清明")
        consume_item(player, item_name, result)
    elif item_name == "仪式粉末":
        result["messages"].append("粉末落在地上，短暂显出扭曲纹路。")
        if state.current_location in {"旧档案室", "地下墓室"}:
            add_clue(state, "深渊污染痕迹", result)
        consume_item(player, item_name, result)
    elif item_name == "开锁工具" and state.current_location == "旧档案室":
        result["messages"].append("你用开锁工具打开了卡死的档案抽屉。")
        add_clue(state, next_archive_clue(state), result)
        change_suspicion(state, 1, result, "撬开档案抽屉")
    elif item_name == "圣徽":
        result["messages"].append("圣徽在掌心微微发冷，你的呼吸变得平稳。")
        change_san(state, 1, result, "握紧圣徽")
    else:
        description = ITEMS[item_name]["description"]
        result["messages"].append(f"你检查了「{item_name}」：{description} 现在还没有更具体的使用效果。")


def consume_item(player, item_name, result):
    if ITEMS[item_name]["consumable"] and player.remove_item(item_name):
        result["state_changes"].append(f"消耗道具：{item_name}")


def handle_stealth(state, result):
    location = state.current_location
    player = state.player
    modifier = best_modifier(player, ["stealth_bonus", "lockpick_bonus", "deceive_bonus"])
    dc = 12 if player.class_id == "rogue" else 15
    check = roll_check(state, "agility", dc, modifier)
    result["roll"] = check
    result["success"] = check["success"]

    if check["success"]:
        result["messages"].append("你压低脚步，避开会吱呀作响的木板。")
        change_suspicion(state, 1, result, "隐秘路线留下痕迹")
        if location == "旧档案室":
            add_clue(state, next_archive_clue(state), result)
        elif location == "前厅":
            add_clue(state, "破损圣徽", result)
        else:
            result["messages"].append("这里没有明显可利用的隐秘路线。")
    else:
        result["messages"].append("一块腐朽木板突然断裂，声音在空厅里传得很远。")
        change_suspicion(state, 2, result, "潜行失败")
        change_hp(state, -1, result, "摔伤")


def handle_talk(state, result):
    location = state.current_location
    modifier = best_modifier(state.player, ["deceive_bonus", "lore_bonus"])
    check = roll_check(state, "intelligence", 12, modifier)
    result["roll"] = check
    result["success"] = check["success"]

    if check["success"] and location == "钟楼":
        result["messages"].append("你试探性说出档案里的假名，大钟自行响了一下。")
        add_clue(state, "说谎时响起的钟声", result)
    elif check["success"] and location == "地下墓室":
        result["messages"].append("你对黑暗发问，石棺间传回破碎的名字。")
        add_clue(state, "地下墓室的亡者残响", result)
    elif check["success"]:
        result["messages"].append("没有活人回应你，但你的声音让雾短暂露出回音方向。")
    else:
        result["messages"].append("回应你的只有钟声般的幻听。")
        change_suspicion(state, 1, result, "声音惊动暗处")


def format_inventory(inventory):
    return ", ".join(inventory) if inventory else "空"


def check_ending(state, result):
    player = state.player
    core_count = len(CORE_TRUTH_CLUES.intersection(player.clues))

    if player.san <= 0 or player.corruption >= 5:
        state.mark_game_over("abyss_corruption", ENDINGS["abyss_corruption"])
    elif player.hp <= 0:
        state.mark_game_over("fallen", ENDINGS["fallen"])
    elif core_count >= 4:
        state.mark_game_over("truth_revealed", ENDINGS["truth_revealed"])
    elif (
        state.current_location == "修道院门口"
        and state.turn >= 5
        and len(state.visited_locations) >= 2
        and core_count < 4
    ):
        state.mark_game_over("ordinary_escape", ENDINGS["ordinary_escape"])

    if state.is_game_over:
        result["ending"] = state.ending_id
