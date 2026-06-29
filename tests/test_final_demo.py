import unittest

from agentic_runtime.final_demo import (
    FINAL_DEMO_SETUP,
    FINAL_DEMO_STEPS,
    run_final_demo,
)


class FinalDemoTests(unittest.TestCase):
    def test_final_demo_route_demonstrates_core_portfolio_capabilities(self):
        report = run_final_demo()

        self.assertEqual(report.failures, ())
        self.assertEqual(report.setup["origin_city"], "卢塞恩")
        self.assertEqual(report.setup["class_id"], FINAL_DEMO_SETUP["class_id"])
        self.assertEqual(len(report.results), len(FINAL_DEMO_STEPS))
        self.assertGreater(report.lore_card_count, 0)

        effects = {
            effect
            for result in report.results
            for effect in result.committed_effects
        }
        rejected = {
            effect
            for result in report.results
            for effect in result.rejected_effects
        }

        self.assertIn("item_effect_applied", effects)
        self.assertIn("prayer_invoked", effects)
        self.assertIn("feasibility_blocked", effects)
        self.assertIn("unconfirmed_death", rejected)
        self.assertIn("insufficient_resources", rejected)
        self.assertTrue(any(result.roll for result in report.results))
        self.assertGreater(report.results[-1].memory_count, report.results[0].memory_count)


if __name__ == "__main__":
    unittest.main()
