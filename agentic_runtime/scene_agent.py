"""Temporary scene generation for the Phase 5 baseline."""

from .contracts import TemporaryContentProposal
from .world_slice import (
    is_world_slice,
    visible_memory_line,
)


def propose_temporary_scene(state, open_action, memory_retrieval=None):
    if is_world_slice(state):
        memory_text = visible_memory_line(memory_retrieval)
        memory_sentence = "" if memory_text == "暂无可见长期记忆。" else f"你还记得：{memory_text}。"
        description = (
            "你照着自己的打算向前试探，城市的声响、人群和本地势力开始围绕你的行动产生反应。"
            f"{memory_sentence}"
        )
        return TemporaryContentProposal(
            content_type="world_scene_slice",
            title=f"{state.current_location}行动切片",
            description=description,
            authority_level="temporary",
            related_targets=open_action.targets,
        )

    description = (
        f"{state.current_location}的空气因你的行动短暂改变。"
        "周围出现了一些可观察的细节，但它们还不是长期世界事实。"
    )
    return TemporaryContentProposal(
        content_type="scene_detail",
        title="临时场景细节",
        description=description,
        authority_level="temporary",
        related_targets=open_action.targets,
    )
