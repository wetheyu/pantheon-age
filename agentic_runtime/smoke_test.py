"""Manual smoke test for Agentic Runtime live/fallback behavior.

This module is intentionally not part of the normal unit test suite.
It may call a real LLM only when local `.env` enables Agentic LLM providers.
"""

from llm_runtime.providers import load_local_env

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import configure_character_for_game_mode

from .orchestrator import run_agentic_turn


def main():
    load_local_env()
    character = build_character("测试员", "rogue", "隐秘之神")
    configure_character_for_game_mode(character, "world", "albion", "格兰威克")
    state = GameState(character)

    result = run_agentic_turn(state, "我在当前街区寻找一个愿意谈论异常传闻的人")
    trace = result.runtime_trace

    print("Agentic Runtime smoke test completed.")
    print(f"Branch: {trace.branch}")
    print(f"Total: {trace.total_ms}ms")
    print(f"Provider reason: {result.providers.get('reason')}")
    print(f"LLM enabled: {result.providers.get('llm_enabled')}")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"- {error}")
    print("Steps:")
    for step in trace.steps:
        print(f"- {step.name}: {step.elapsed_ms}ms")
    print("Narration preview:")
    print(result.narration.text[:500])


if __name__ == "__main__":
    main()
