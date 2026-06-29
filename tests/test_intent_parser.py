import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase1_cli.intent_parser import parse_intent


class IntentParserTests(unittest.TestCase):
    def test_move_to_prayer_hall_is_move_not_pray(self):
        action = parse_intent("前往祈祷大厅", "前厅")

        self.assertEqual(action["intent"], "move")
        self.assertEqual(action["target"], "祈祷大厅")
        self.assertFalse(action["requires_check"])

    def test_pray_without_movement_is_pray(self):
        action = parse_intent("向死亡之神祈祷", "前厅")

        self.assertEqual(action["intent"], "pray")
        self.assertTrue(action["requires_check"])
        self.assertEqual(action["check_stat"], "communion")

    def test_use_item_alias(self):
        action = parse_intent("喝下镇静", "前厅")

        self.assertEqual(action["intent"], "use_item")
        self.assertEqual(action["item"], "镇静药剂")


if __name__ == "__main__":
    unittest.main()
