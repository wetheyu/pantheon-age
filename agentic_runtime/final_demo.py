"""Final demo route for Pantheon Age.

The demo route is local and deterministic-friendly. It checks that the project
can demonstrate the main portfolio story without relying on exact LLM wording:
opening, canon grounding, memory, dice, prayer, item use, resource blocking,
and authority-safe violence.
"""

from dataclasses import dataclass
import json
from unittest.mock import patch

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import configure_character_for_game_mode
from phase1_cli.story import render_opening

from .context_pack import build_context_pack
from .memory_retriever import retrieve_memory
from .playtest_fixtures import (
    PLAYER_FORBIDDEN_TERMS,
    PlaytestStep,
    collect_playtest_failures,
    run_playtest_fixture,
)
from .providers import build_local_agentic_providers


FINAL_DEMO_SETUP = {
    "name": "伊芙",
    "class_id": "rogue",
    "class_name": "密探",
    "god": "隐秘之神",
    "origin_country_id": "lumiere",
    "origin_city": "卢塞恩",
    "background_id": "investigative_reporter",
    "background_name": "调查记者",
}


FINAL_DEMO_STEPS = (
    PlaytestStep(
        name="demo_opening_probe",
        category="opening",
        action="观察周围，确认今晚异常传闻的来源",
        expected_effects=("world_attempt_recorded",),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=False,
    ),
    PlaytestStep(
        name="demo_social_check",
        category="social",
        action="说服附近报童谈谈昨夜的异常钟声",
        expected_effects=("world_attempt_recorded", "world_check_success"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
    PlaytestStep(
        name="demo_item_check",
        category="item",
        action="使用开锁工具，悄悄打开报社侧门的锁",
        expected_effects=("world_attempt_recorded", "world_check_success", "item_effect_applied"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
    PlaytestStep(
        name="demo_prayer_check",
        category="prayer",
        action="拿出假名证件并进行无声祈祷，伪装成报社助手通过盘问",
        expected_effects=("world_attempt_recorded", "world_check_success", "prayer_invoked"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
    PlaytestStep(
        name="demo_resource_gate",
        category="resource_gate",
        action="我现在就买下一整片庄园和别墅，拿到钥匙",
        expected_effects=("world_attempt_recorded", "feasibility_blocked"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=False,
    ),
    PlaytestStep(
        name="demo_violence_gate",
        category="violence",
        action="出手杀了拦路的守卫",
        expected_effects=("world_attempt_recorded",),
        forbidden_effects=("target_death", "target_killed", "permanent_injury"),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=True,
    ),
    PlaytestStep(
        name="demo_memory_recap",
        category="memory",
        action="回想一下我刚才已经做过什么",
        expected_effects=("world_attempt_recorded",),
        expected_location="卢塞恩",
        expected_location_intent="stay",
        requires_roll=False,
    ),
)


FINAL_DEMO_ROLLS = (16, 17, 16, 5)


@dataclass(frozen=True)
class FinalDemoReport:
    setup: dict
    opening_text: str
    lore_card_count: int
    lore_card_titles: tuple[str, ...]
    results: tuple
    failures: tuple[str, ...]

    def to_dict(self):
        return {
            "setup": dict(self.setup),
            "lore_card_count": self.lore_card_count,
            "lore_card_titles": list(self.lore_card_titles),
            "failures": list(self.failures),
            "results": [result.to_dict() for result in self.results],
            "opening_preview": self.opening_text[:240],
        }


def build_final_demo_state():
    character = build_character(
        FINAL_DEMO_SETUP["name"],
        FINAL_DEMO_SETUP["class_id"],
        FINAL_DEMO_SETUP["god"],
    )
    configure_character_for_game_mode(
        character,
        "world",
        FINAL_DEMO_SETUP["origin_country_id"],
        FINAL_DEMO_SETUP["origin_city"],
        None,
        FINAL_DEMO_SETUP["background_id"],
    )
    return GameState(character)


def run_final_demo(providers=None):
    state = build_final_demo_state()
    providers = providers or build_local_agentic_providers()
    opening_text = render_opening(state.player, "world")
    first_memory = retrieve_memory(state, FINAL_DEMO_STEPS[0].action)
    first_context = build_context_pack(
        state,
        user_text=FINAL_DEMO_STEPS[0].action,
        memory_retrieval=first_memory,
    )
    with patch("phase1_cli.rule_engine.random.randint", side_effect=FINAL_DEMO_ROLLS):
        results = run_playtest_fixture(FINAL_DEMO_STEPS, state=state, providers=providers)
    failures = collect_final_demo_failures(opening_text, first_context, results)
    lore_cards = tuple(first_context.get("relevant_lore_cards", ()))
    return FinalDemoReport(
        setup=dict(FINAL_DEMO_SETUP),
        opening_text=opening_text,
        lore_card_count=len(lore_cards),
        lore_card_titles=tuple(card.get("title", "") for card in lore_cards),
        results=tuple(results),
        failures=failures,
    )


def collect_final_demo_failures(opening_text, context_pack, results):
    failures = list(collect_playtest_failures(results, forbidden_terms=PLAYER_FORBIDDEN_TERMS))

    required_opening_terms = (
        "虚无之壁",
        FINAL_DEMO_SETUP["origin_city"],
        FINAL_DEMO_SETUP["class_name"],
        FINAL_DEMO_SETUP["god"],
        FINAL_DEMO_SETUP["background_name"],
        "资源处境",
    )
    for term in required_opening_terms:
        if term not in opening_text:
            failures.append(f"opening missing required term: {term}")

    lore_cards = context_pack.get("relevant_lore_cards", ())
    if not lore_cards:
        failures.append("context pack did not retrieve any lore cards")
    if not any(FINAL_DEMO_SETUP["origin_city"] in json.dumps(card, ensure_ascii=False) for card in lore_cards):
        failures.append(f"context pack did not retrieve lore about {FINAL_DEMO_SETUP['origin_city']}")

    first_memory_count = results[0].memory_count if results else 0
    last_memory_count = results[-1].memory_count if results else 0
    if last_memory_count <= first_memory_count:
        failures.append("memory count did not grow across the final demo route")

    all_effects = set()
    all_rejected = set()
    all_rolls = []
    for result in results:
        all_effects.update(result.committed_effects)
        all_rejected.update(result.rejected_effects)
        if result.roll:
            all_rolls.append(result.roll)

    required_effects = (
        "item_effect_applied",
        "prayer_invoked",
        "feasibility_blocked",
        "world_check_success",
    )
    for effect in required_effects:
        if effect not in all_effects:
            failures.append(f"final demo did not demonstrate committed effect: {effect}")

    required_rejected = (
        "unconfirmed_property_acquisition",
        "insufficient_resources",
        "unconfirmed_death",
    )
    for effect in required_rejected:
        if effect not in all_rejected:
            failures.append(f"final demo did not demonstrate rejected effect: {effect}")

    if not any(roll.get("item_bonuses") for roll in all_rolls):
        failures.append("final demo did not show item bonuses in dice context")
    if not any(roll.get("prayer_bonuses") for roll in all_rolls):
        failures.append("final demo did not show prayer bonuses in dice context")

    return tuple(failures)


def main():
    report = run_final_demo()
    print("Pantheon Age final demo smoke")
    print(f"Setup: {report.setup}")
    print(f"Lore cards: {report.lore_card_count} {list(report.lore_card_titles)}")
    print(f"Steps: {len(report.results)}")
    for result in report.results:
        print(
            f"- {result.step.name}: location={result.location}, "
            f"effects={list(result.committed_effects)}, roll={'yes' if result.roll else 'no'}"
        )
    if report.failures:
        print("Failures:")
        for failure in report.failures:
            print(f"- {failure}")
        return 1
    print("Final demo smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
