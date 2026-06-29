import unittest

from agentic_runtime.contracts import RuntimeStep, RuntimeTrace
from agentic_runtime.performance import summarize_runtime_performance


class PerformanceSummaryTests(unittest.TestCase):
    def test_fast_profile_under_budget_is_ok(self):
        trace = RuntimeTrace(
            branch="creative_gm",
            total_ms=12000,
            steps=(RuntimeStep("creative_gm_provider", 11900),),
        )

        summary = summarize_runtime_performance(trace, {"runtime_profile": "fast"})

        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["budget_ms"], 20000)
        self.assertIn("within", summary["advice"])

    def test_fast_profile_over_budget_points_to_llm_provider(self):
        trace = RuntimeTrace(
            branch="creative_gm",
            total_ms=24000,
            steps=(
                RuntimeStep("creative_gm_provider", 23900),
                RuntimeStep("state_commit", 1),
            ),
        )

        summary = summarize_runtime_performance(trace, {"runtime_profile": "fast"})

        self.assertEqual(summary["status"], "warn")
        self.assertEqual(summary["slowest_steps"][0]["name"], "creative_gm_provider")
        self.assertIn("LLM provider dominates latency", summary["advice"])


if __name__ == "__main__":
    unittest.main()
