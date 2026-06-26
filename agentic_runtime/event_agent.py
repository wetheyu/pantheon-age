"""Event Agent baseline for temporary local events."""

from .contracts import EventProposal
from .world_slice import city_label, is_world_slice


def propose_events(state, open_action, memory_retrieval=None, npcs=()):
    npc_names = tuple(npc.name for npc in npcs)
    if is_world_slice(state):
        event = EventProposal(
            event_type="world_local_reaction",
            summary=(
                f"{city_label(state)}的街面、教区或办事机构出现了细微反应。"
                "有人压低声音，有人移开视线，也有人把刚才的动静记进随身的小册子。"
            ),
            hooks=(
                "可以追问附近的人。",
                "可以观察本地教会、商会或治安机构的反应。",
                "可以把这个反应当作下一步追问的入口。",
            ),
            involved_npcs=npc_names,
        )
        return (event,)

    event = EventProposal(
        event_type="local_reaction",
        summary=(
            f"{state.current_location}里的声音因你的行动短暂改变，"
            "像是有什么东西在回应玩家的选择。"
        ),
        hooks=(
            "可以继续观察这个反应。",
            "可以询问附近的人是否注意到异常。",
        ),
        involved_npcs=npc_names,
    )
    return (event,)
