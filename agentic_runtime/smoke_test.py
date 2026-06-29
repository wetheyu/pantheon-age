"""Manual smoke test for Agentic Runtime live/fallback behavior.

This module is intentionally not part of the normal unit test suite.
It may call a real LLM only when local `.env` enables Agentic LLM providers.
"""

from llm_runtime.providers import load_local_env

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import configure_character_for_game_mode

from .orchestrator import run_agentic_turn
from .performance import summarize_runtime_performance
from .runtime_profiles import PLAY_PROFILE_ENV_VAR, active_runtime_profile, available_runtime_profiles


def main():
    load_local_env()
    profile = active_runtime_profile()
    character = build_character("测试员", "rogue", "隐秘之神")
    configure_character_for_game_mode(character, "world", "albion", "格兰威克")
    state = GameState(character)

    result = run_agentic_turn(state, "我在当前街区寻找一个愿意谈论异常传闻的人")
    trace = result.runtime_trace

    print("Agentic Runtime smoke test completed.")
    if profile:
        print(f"Runtime profile: {profile.name} ({profile.label})")
    else:
        print(
            "Runtime profile: none "
            f"(set {PLAY_PROFILE_ENV_VAR} to one of: "
            + ", ".join(profile.name for profile in available_runtime_profiles())
            + ")"
        )
    print(f"Branch: {trace.branch}")
    print(f"Total: {trace.total_ms}ms")
    print(f"Provider reason: {result.providers.get('reason')}")
    print(f"LLM enabled: {result.providers.get('llm_enabled')}")
    endpoint = result.providers.get("provider_endpoint")
    if endpoint and (
        result.providers.get("llm_enabled") or endpoint.get("base_url_configured")
    ):
        label = "Provider endpoint"
        if not result.providers.get("llm_enabled"):
            label = "Configured provider endpoint (inactive)"
        print(
            f"{label}: "
            f"{endpoint.get('provider')} / {endpoint.get('endpoint')}"
        )
        if endpoint.get("base_url_origin"):
            print(f"Provider origin: {endpoint.get('base_url_origin')}")
    if result.providers.get("runtime_profile"):
        print(f"Provider profile: {result.providers.get('runtime_profile')}")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"- {error}")
    print("Steps:")
    for step in trace.steps:
        print(f"- {step.name}: {step.elapsed_ms}ms")
    slowest = sorted(trace.steps, key=lambda step: step.elapsed_ms, reverse=True)[:3]
    if slowest:
        print("Slowest steps:")
        for step in slowest:
            print(f"- {step.name}: {step.elapsed_ms}ms")
    performance = summarize_runtime_performance(trace, result.providers)
    print("Performance:")
    print(
        f"- status={performance['status']} "
        f"profile={performance['profile']} "
        f"budget={performance['budget_ms']}ms"
    )
    print(f"- advice={performance['advice']}")
    print("Narration preview:")
    print(result.narration.text[:500])


if __name__ == "__main__":
    main()
