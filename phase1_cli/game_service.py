"""Reusable game service layer for 神座纪元 v1.4.

This module has no input() or print() calls. The current CLI and the future
FastAPI layer can both call handle_player_input().
"""

from dataclasses import dataclass
from typing import Optional

from .game_state import GameState
from .intent_parser import parse_intent
from .rule_engine import apply_rule
from .story import (
    render_clues,
    render_ending,
    render_goal,
    render_help,
    render_log,
    render_map,
    render_result,
    render_status,
)


QUIT_COMMANDS = {"退出", "quit", "exit", "q"}
HELP_COMMANDS = {"帮助", "help", "h", "?"}
STATUS_COMMANDS = {"状态", "status", "s"}
SAVE_COMMANDS = {"存档", "save"}
LOAD_COMMANDS = {"读档", "load"}
GOAL_COMMANDS = {"目标", "goal", "objective"}
CLUE_COMMANDS = {"线索", "clues", "clue"}
MAP_COMMANDS = {"地图", "map"}
LOG_COMMANDS = {"日志", "log", "history"}


@dataclass
class GameResponse:
    kind: str
    text: str
    state: GameState
    consumes_turn: bool = False
    should_exit: bool = False
    should_save: bool = False
    should_load: bool = False
    action: Optional[dict] = None
    rule_result: Optional[dict] = None
    ending_text: str = ""

    def to_dict(self):
        return {
            "kind": self.kind,
            "text": self.text,
            "consumes_turn": self.consumes_turn,
            "should_exit": self.should_exit,
            "should_save": self.should_save,
            "should_load": self.should_load,
            "action": self.action,
            "rule_result": self.rule_result,
            "ending_text": self.ending_text,
            "state": self.state.to_public_dict(),
        }


def normalize_command(user_text):
    return user_text.strip().lower()


def handle_player_input(state, user_text):
    raw_text = user_text.strip()
    command = normalize_command(user_text)

    if not raw_text:
        return GameResponse(
            kind="empty",
            text="你停在原地，雾也停在原地。请输入一个行动，或输入“帮助”。",
            state=state,
        )

    if command in QUIT_COMMANDS:
        return GameResponse(
            kind="quit",
            text="你合上冒险日志，暂时离开雾中修道院。",
            state=state,
            should_exit=True,
        )

    if command in HELP_COMMANDS:
        return GameResponse(kind="help", text=render_help(), state=state)

    if command in STATUS_COMMANDS:
        return GameResponse(kind="status", text=render_status(state), state=state)

    if command in GOAL_COMMANDS:
        return GameResponse(kind="goal", text=render_goal(state), state=state)

    if command in CLUE_COMMANDS:
        return GameResponse(kind="clues", text=render_clues(state), state=state)

    if command in MAP_COMMANDS:
        return GameResponse(kind="map", text=render_map(state), state=state)

    if command in LOG_COMMANDS:
        return GameResponse(kind="log", text=render_log(state), state=state)

    if command in SAVE_COMMANDS:
        return GameResponse(kind="save", text="请求保存当前游戏。", state=state, should_save=True)

    if command in LOAD_COMMANDS:
        return GameResponse(kind="load", text="请求读取本地存档。", state=state, should_load=True)

    action = parse_intent(raw_text, state.current_location)
    result = apply_rule(state, action)
    ending_text = render_ending(state) if state.is_game_over else ""

    return GameResponse(
        kind="action",
        text=render_result(result),
        state=state,
        consumes_turn=True,
        action=action,
        rule_result=result,
        ending_text=ending_text,
    )
