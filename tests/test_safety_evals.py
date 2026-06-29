import unittest
from unittest.mock import patch

from agentic_runtime.safety_evals import (
    DEFAULT_SAFETY_EVAL_CASES,
    collect_safety_eval_failures,
    run_safety_evals,
)


class SafetyEvalTests(unittest.TestCase):
    def test_default_local_safety_evals_preserve_authority_boundaries(self):
        with patch("phase1_cli.rule_engine.random.randint", side_effect=[12] * 50):
            results = run_safety_evals()

        failures = collect_safety_eval_failures(results)
        by_name = {result.case.name: result for result in results}

        self.assertEqual(len(results), len(DEFAULT_SAFETY_EVAL_CASES))
        self.assertEqual(failures, ())
        self.assertTrue(all(result.runtime_branch == "local" for result in results))
        self.assertIn("feasibility_blocked", by_name["impossible_property_purchase"].committed_effects)
        self.assertIn("unconfirmed_death", by_name["unauthorized_kill"].rejected_effects)
        self.assertIn("unconfirmed_city_travel", by_name["instant_cross_city_travel"].rejected_effects)
        self.assertEqual(by_name["instant_cross_city_travel"].location, "卢塞恩")
        self.assertEqual(by_name["scene_continuity_after_setup"].scene_focus, "码头")


if __name__ == "__main__":
    unittest.main()
