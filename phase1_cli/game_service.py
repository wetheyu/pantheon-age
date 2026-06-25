"""Reusable game service layer for 神座纪元 v5.8.0.

This module has no input() or print() calls. The current CLI and the future
FastAPI layer can both call handle_player_input().
"""

import os
from dataclasses import dataclass
from typing import Optional

from agentic_runtime.orchestrator import run_agentic_turn
from llm_runtime.actions import build_keyword_action_candidate, resolve_action_candidate
from llm_runtime.adjudication import adjudicate_candidate
from llm_runtime.narrator import render_safe_narration
from llm_runtime.providers import (
    KeywordActionCandidateProvider,
    OpenAIProviderError,
    TemplateNarrationProvider,
    build_runtime_providers_from_env,
    load_local_env,
)

from .game_state import GameState
from .rule_engine import apply_rule
from .scenarios import is_world_mode_state
from .story import (
    render_clues,
    render_ending,
    render_goal,
    render_help,
    render_log,
    render_map,
    render_mechanical_summary,
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
AGENTIC_RUNTIME_ENV_VAR = "PANTHEON_USE_AGENTIC_RUNTIME"
TRUTHY_VALUES = {"1", "true", "yes", "on"}


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
    llm_runtime: Optional[dict] = None
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
            "llm_runtime": self.llm_runtime,
            "ending_text": self.ending_text,
            "state": self.state.to_public_dict(),
        }


def normalize_command(user_text):
    return user_text.strip().lower()


def is_agentic_runtime_enabled():
    load_local_env()
    return os.getenv(AGENTIC_RUNTIME_ENV_VAR, "").strip().lower() in TRUTHY_VALUES


def should_use_agentic_runtime_for_state(state):
    return is_agentic_runtime_enabled() or is_world_mode_state(state)


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
        quit_text = "你合上冒险日志，暂时离开神座纪元。"
        if not is_world_mode_state(state):
            quit_text = "你合上冒险日志，暂时离开雾中修道院。"
        return GameResponse(
            kind="quit",
            text=quit_text,
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

    if should_use_agentic_runtime_for_state(state):
        return handle_agentic_player_input(state, raw_text)

    runtime = build_runtime_providers_from_env()
    runtime_errors = []

    try:
        action_candidate_result = resolve_action_candidate(
            raw_text,
            state.current_location,
            provider=runtime.action_provider,
        )
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        fallback_provider = KeywordActionCandidateProvider()
        action_candidate_result = resolve_action_candidate(
            raw_text,
            state.current_location,
            provider=fallback_provider,
        )

    action = action_candidate_result.action
    adjudication_candidate = action_candidate_result.candidate
    if action_candidate_result.used_fallback:
        adjudication_candidate = build_keyword_action_candidate(raw_text, state.current_location)
    adjudication_result = adjudicate_candidate(adjudication_candidate)

    result = apply_rule(state, action)
    ending_text = render_ending(state) if state.is_game_over else ""

    response = GameResponse(
        kind="action",
        text=render_result(result),
        state=state,
        consumes_turn=True,
        action=action,
        rule_result=result,
        ending_text=ending_text,
    )

    try:
        narration_result = render_safe_narration(response, provider=runtime.narration_provider)
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        narration_result = render_safe_narration(response, provider=TemplateNarrationProvider())

    response.text = narration_result.text
    response.llm_runtime = {
        "providers": runtime.to_dict(),
        "action_candidate": action_candidate_result.to_dict(),
        "adjudication": adjudication_result.to_dict(),
        "narration": narration_result.to_dict(),
        "errors": runtime_errors,
    }
    return response


def handle_agentic_player_input(state, raw_text):
    result = run_agentic_turn(state, raw_text)
    ending_text = render_ending(state) if state.is_game_over else ""
    response_text = result.narration.text
    if is_world_mode_state(state):
        mechanical_summary = render_mechanical_summary(result.commit.rule_result)
        if mechanical_summary:
            response_text = f"{mechanical_summary}\n\n{response_text}"

    return GameResponse(
        kind="action",
        text=response_text,
        state=state,
        consumes_turn=True,
        action=result.commit.rule_action,
        rule_result=result.commit.rule_result,
        llm_runtime={
            "phase": "phase5-agentic-runtime",
            "agentic_runtime": result.to_dict(),
        },
        ending_text=ending_text,
    )
