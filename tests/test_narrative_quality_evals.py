import unittest
from dataclasses import replace
from unittest.mock import patch

from agentic_runtime.narrative_quality_evals import (
    collect_narrative_quality_failures,
    evaluate_narrative_quality,
    run_narrative_quality_evals,
)
from agentic_runtime.playtest_fixtures import run_playtest_fixture


class NarrativeQualityEvalTests(unittest.TestCase):
    def test_default_local_playtest_narration_passes_quality_gate(self):
        with patch("phase1_cli.rule_engine.random.randint", side_effect=[12] * 50):
            playtest_results = run_playtest_fixture()

        quality_results = run_narrative_quality_evals(playtest_results)
        failures = collect_narrative_quality_failures(quality_results)

        self.assertEqual(failures, ())
        self.assertTrue(all(result.score >= 80 for result in quality_results))

    def test_quality_eval_catches_backend_report_style_text(self):
        with patch("phase1_cli.rule_engine.random.randint", side_effect=[12] * 50):
            playtest_result = run_playtest_fixture()[0]
        bad_result = replace(
            playtest_result,
            text="系统裁定报告：world_attempt_recorded。玩家行动完成。",
        )

        quality = evaluate_narrative_quality(bad_result)

        self.assertFalse(quality.passed)
        self.assertTrue(any("backend" in failure for failure in quality.failures))
        self.assertTrue(any("report-style" in failure for failure in quality.failures))


if __name__ == "__main__":
    unittest.main()
