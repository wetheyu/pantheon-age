"""Item Agent baseline for temporary object candidates."""

from .contracts import ItemProposal
from .world_slice import city_label, is_world_slice, target_text


def propose_items(state, open_action, memory_retrieval=None):
    target = target_text(state, open_action)
    if is_world_slice(state):
        item = ItemProposal(
            name=f"{state.current_location}的可疑凭证",
            description=(
                f"一件带有{city_label(state)}本地痕迹的小物件出现在附近。"
                "它不显眼，却足够成为一次追问、一次观察，或一次误会的开端。"
            ),
            possible_uses=(
                "作为调查对象",
                "作为询问本地人的话题",
                "作为后续行动的对象",
            ),
            risk_tags=("social", "unknown"),
        )
        return (item,)

    item = ItemProposal(
        name="可疑的场景物件",
        description=(
            f"在靠近「{target}」的位置，有一个值得留意的小物件。"
            "它安静地躺在那里，像是在等待有人把它和当前的异常联系起来。"
        ),
            possible_uses=(
                "作为调查对象",
                "作为对话话题",
                "作为后续行动的工具候选",
            ),
        risk_tags=("unknown",),
    )
    return (item,)
