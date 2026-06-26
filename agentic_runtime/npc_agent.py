"""NPC Agent baseline for temporary local characters."""

from .contracts import NPCProposal
from .world_slice import city_label, is_world_slice, origin_line, target_text, visible_memory_line


def propose_npcs(state, open_action, memory_retrieval=None):
    target = target_text(state, open_action)
    if is_world_slice(state):
        npc = NPCProposal(
            name="谨慎的当地人",
            role="本地见闻者",
            description=(
                f"这个人属于{city_label(state)}的日常秩序，凭口音和衣着大概看出你来自{origin_line(state)}。"
                "他注意到你的靠近，目光里有警惕，也有一点愿意开口的犹豫。"
            ),
            visible_knowledge=(
                f"看见玩家在{state.current_location}附近行动。",
                f"记得当前可见上下文：{visible_memory_line(memory_retrieval)}",
            ),
            attitude="watchful",
            short_term_goal="判断玩家是否会给本地秩序带来麻烦。",
        )
        return (npc,)

    npc = NPCProposal(
        name="无名见证者",
        role="谨慎路人",
        description=(
            f"一个停留在{state.current_location}边缘的人影注意到了你围绕「{target}」的行动。"
            "他的神情谨慎，像是既害怕被卷入麻烦，又不愿错过正在发生的异常。"
        ),
        visible_knowledge=(
            f"知道{state.current_location}附近刚刚发生了动静。",
        ),
        attitude="cautious",
        short_term_goal="弄清楚玩家是否会带来危险。",
    )
    return (npc,)
