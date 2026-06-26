import sys
from pathlib import Path
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_runtime.playtest_fixtures import (
    DEFAULT_PLAYTEST_STEPS,
    collect_playtest_failures,
    run_playtest_fixture,
)


class PlaytestFixtureTests(unittest.TestCase):
    def test_default_local_playtest_fixture_preserves_core_safety_properties(self):
        with patch("phase1_cli.rule_engine.random.randint", side_effect=[10, 12, 14]):
            results = run_playtest_fixture()

        failures = collect_playtest_failures(results)

        self.assertEqual(len(results), len(DEFAULT_PLAYTEST_STEPS))
        self.assertEqual(failures, ())
        self.assertTrue(all(result.runtime_branch == "local" for result in results))
        self.assertTrue(any(result.roll for result in results))
        self.assertTrue(
            any("travel_request_recorded" in result.committed_effects for result in results)
        )
        self.assertEqual(results[-1].location, "卢塞恩")
        self.assertNotIn("target_death", results[-1].committed_effects)
        self.assertGreater(results[-1].memory_count, 0)


if __name__ == "__main__":
    unittest.main()
