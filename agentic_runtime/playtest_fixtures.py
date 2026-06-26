"""Repeatable local playtest fixtures for Phase 7.

These fixtures are intentionally local-only. They help us check the basic
world-mode experience without calling a real LLM or depending on exact prose.
"""

from dataclasses import dataclass, field

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import configure_character_for_game_mode, current_scene_focus_for_state

from .orchestrator import run_agentic_turn
from .providers import build_local_agentic_providers


PLAYER_FORBIDDEN_TERMS = (
    "临时",
    "切片",
    "系统没有确认",
    "世界事实",
    "validator",
    "commit",
    "rule_result",
)


@dataclass(frozen=True)
class PlaytestStep:
    name: str
    category: str
    action: str
    expected_effects: tuple[str, ...] = field(default_factory=tuple)
    forbidden_effects: tuple[str, ...] = field(default_factory=tuple)
    expected_location: str | None = None
    expected_location_intent: str | None = None
    requires_roll: bool | None = None

    def __post_init__(self):
        object.__setattr__(self, "expected_effects", tuple(self.expected_effects))
        object.__setattr__(self, "forbidden_effects", tuple(self.forbidden_effects))


@dataclass(frozen=True)
class PlaytestStepResult:
    step: PlaytestStep
    text: str
    location: str
    scene_focus: str
    location_intent: str
    committed_effects: tuple[str, ...]
    rejected_effects: tuple[str, ...]
    roll: dict | None
    memory_count: int
    runtime_branch: str
    errors: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        object.__setattr__(self, "committed_effects", tuple(self.committed_effects))
        object.__setattr__(self, "rejected_effects", tuple(self.rejected_effects))
        object.__setattr__(self, "errors", tuple(self.errors))

    def to_dict(self):
        return {
            "name": self.step.name,
            "category": self.step.category,
            "action": self.step.action,
            "location": self.location,
            "scene_focus": self.scene_focus,
            "location_intent": self.location_intent,
            "committed_effects": list(self.committed_effects),
            "rejected_effects": list(self.rejected_effects),
            "roll": self.roll,
            "memory_count": self.memory_count,
            "runtime_branch": self.runtime_branch,
            "errors": list(self.errors),
            "text_preview": self.text[:160],
        }


DEFAULT_PLAYTEST_STEPS = (
    PlaytestStep(
        name="opening_scene_probe",
        category="opening",
        action="观察周围，确认今晚异常传闻的来源",
        expected_effects=("world_attempt_recorded",),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=False,
    ),
    PlaytestStep(
        name="social_pressure",
        category="social",
        action="说服附近报童谈谈昨夜的异常钟声",
        expected_effects=("world_attempt_recorded", "world_check_success"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
    PlaytestStep(
        name="investigation_without_teleport",
        category="investigation",
        action="检查报社门口的失踪告示，看看有没有被人涂改",
        expected_effects=("world_attempt_recorded",),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=False,
    ),
    PlaytestStep(
        name="prayer_pressure",
        category="prayer",
        action="向隐秘之神祈祷，请求遮蔽我的踪迹",
        expected_effects=("world_attempt_recorded",),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
    PlaytestStep(
        name="travel_request",
        category="travel",
        action="我准备乘船去维拉尔，询问航线和票据",
        expected_effects=("world_attempt_recorded", "travel_request_recorded"),
        expected_location="卢塞恩",
        expected_location_intent="travel_request",
        requires_roll=False,
    ),
    PlaytestStep(
        name="violence_gate",
        category="violence",
        action="出手杀了拦路的守卫",
        expected_effects=("world_attempt_recorded", "world_check_success"),
        forbidden_effects=("target_death", "target_killed", "permanent_injury"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
)


def build_default_playtest_state():
    character = build_character("测试员", "rogue", "隐秘之神")
    configure_character_for_game_mode(
        character,
        "world",
        "lumiere",
        "卢塞恩",
        None,
        "调查记者",
    )
    return GameState(character)


def run_playtest_fixture(steps=DEFAULT_PLAYTEST_STEPS, state=None, providers=None):
    state = state or build_default_playtest_state()
    providers = providers or build_local_agentic_providers()
    results = []

    for step in steps:
        turn = run_agentic_turn(state, step.action, providers=providers)
        rule_result = turn.commit.rule_result or {}
        results.append(
            PlaytestStepResult(
                step=step,
                text=turn.narration.text,
                location=state.current_location,
                scene_focus=current_scene_focus_for_state(state),
                location_intent=rule_result.get("location_intent", ""),
                committed_effects=turn.commit.committed_effects,
                rejected_effects=turn.commit.rejected_effects,
                roll=rule_result.get("roll"),
                memory_count=sum(len(records) for records in state.agentic_memory.values()),
                runtime_branch=turn.runtime_trace.branch,
                errors=turn.errors,
            )
        )

    return tuple(results)


def collect_playtest_failures(results, forbidden_terms=PLAYER_FORBIDDEN_TERMS):
    failures = []

    for result in results:
        step = result.step
        label = f"{step.name} ({step.category})"

        if result.errors:
            failures.append(f"{label}: runtime errors: {', '.join(result.errors)}")

        for term in forbidden_terms:
            if term in result.text:
                failures.append(f"{label}: player-facing text contains forbidden term: {term}")

        for effect in step.expected_effects:
            if effect not in result.committed_effects:
                failures.append(f"{label}: missing committed effect: {effect}")

        for effect in step.forbidden_effects:
            if effect in result.committed_effects:
                failures.append(f"{label}: forbidden committed effect: {effect}")

        if step.expected_location is not None and result.location != step.expected_location:
            failures.append(
                f"{label}: expected location {step.expected_location}, got {result.location}"
            )

        if (
            step.expected_location_intent is not None
            and result.location_intent != step.expected_location_intent
        ):
            failures.append(
                f"{label}: expected location intent {step.expected_location_intent}, "
                f"got {result.location_intent}"
            )

        if step.requires_roll is True and result.roll is None:
            failures.append(f"{label}: expected a roll result")
        if step.requires_roll is False and result.roll is not None:
            failures.append(f"{label}: did not expect a roll result")

    return tuple(failures)
