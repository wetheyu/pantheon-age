"""Performance summaries for Agentic Runtime traces."""


PROFILE_BUDGET_MS = {
    "local": 750,
    "fast": 20000,
    "quality": 45000,
    "debug": 30000,
    "custom": 30000,
}


def summarize_runtime_performance(trace, providers=None):
    providers = providers or {}
    profile_name = providers.get("runtime_profile") or "custom"
    budget_ms = PROFILE_BUDGET_MS.get(profile_name, PROFILE_BUDGET_MS["custom"])
    slowest = sorted(trace.steps, key=lambda step: step.elapsed_ms, reverse=True)[:3]
    status = classify_latency(trace.total_ms, budget_ms)
    return {
        "profile": profile_name,
        "branch": trace.branch,
        "total_ms": trace.total_ms,
        "budget_ms": budget_ms,
        "status": status,
        "slowest_steps": [
            {"name": step.name, "elapsed_ms": step.elapsed_ms}
            for step in slowest
        ],
        "advice": build_latency_advice(trace, slowest, profile_name, budget_ms, status),
    }


def classify_latency(total_ms, budget_ms):
    if total_ms <= budget_ms:
        return "ok"
    if total_ms <= budget_ms * 1.5:
        return "warn"
    return "slow"


def build_latency_advice(trace, slowest, profile_name, budget_ms, status):
    if status == "ok":
        return "Runtime is within the current profile budget."

    slowest_name = slowest[0].name if slowest else "unknown"
    if "provider" in slowest_name or "openai" in slowest_name:
        if profile_name == "fast":
            return (
                "The LLM provider dominates latency. Keep fast profile compact, "
                "use a faster model, or switch to local profile for zero-cost checks."
            )
        if profile_name == "quality":
            return (
                "Quality profile is expected to be slower. Use fast profile for "
                "normal play and reserve quality for important scenes."
            )
        return (
            "The LLM provider dominates latency. Check model choice, output budget, "
            "network latency, and prompt/context size."
        )

    if "retrieval" in slowest_name:
        return "Retrieval dominates latency. Reduce lore card limits or cache canon retrieval."

    return (
        f"Runtime exceeded the {budget_ms}ms budget. Inspect slowest steps and "
        "avoid optimizing unrelated code before measuring again."
    )
