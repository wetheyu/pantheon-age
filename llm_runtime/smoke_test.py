"""Small command-line probe for Phase 4 LLM providers."""

from .providers import OpenAIProviderError, build_runtime_providers_from_env


def main():
    runtime = build_runtime_providers_from_env()
    print("Phase 4 LLM smoke test")
    print(f"- action_provider: {runtime.action_provider.provider_name}")
    print(f"- narration_provider: {runtime.narration_provider.provider_name}")
    print(f"- llm_enabled: {runtime.llm_enabled}")
    print(f"- model: {runtime.model}")
    print(f"- reason: {runtime.reason}")

    if not runtime.llm_enabled:
        print("Result: LLM is not enabled. Check PANTHEON_USE_LLM and OPENAI_API_KEY.")
        return

    try:
        candidate = runtime.action_provider.propose_action_candidate("跳向前厅", "修道院门口")
    except OpenAIProviderError as exc:
        print(f"Result: OpenAI action provider failed: {exc}")
        return

    print("Result: OpenAI action provider returned a candidate.")
    print(f"- intent: {candidate.intent}")
    print(f"- target: {candidate.target}")
    print(f"- source: {candidate.source}")


if __name__ == "__main__":
    main()
