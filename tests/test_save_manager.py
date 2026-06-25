import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.save_manager import load_game, save_game


class SaveManagerTests(unittest.TestCase):
    def test_character_creation_applies_class_config(self):
        character = build_character("阿洛", "warrior", "死亡之神")

        self.assertEqual(character.class_name, "骑士")
        self.assertEqual(character.max_hp, 25)
        self.assertEqual(character.stats["strength"], 8)
        self.assertIn("制式佩剑", character.inventory)
        self.assertEqual(character.rule_modifiers["attack_bonus"], 2)

    def test_save_and_load_round_trip(self):
        character = build_character("莉娅", "mage", "真理之神")
        state = GameState(character)
        state.record_turn()
        state.move_to("前厅")
        state.player.add_clue("泥泞脚印")
        state.add_event("测试事件")

        with TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "save.json"
            save_game(state, save_path)
            loaded_state = load_game(save_path)

        self.assertEqual(loaded_state.turn, 1)
        self.assertEqual(loaded_state.current_location, "前厅")
        self.assertEqual(loaded_state.player.name, "莉娅")
        self.assertEqual(loaded_state.player.class_id, "mage")
        self.assertIn("泥泞脚印", loaded_state.player.clues)
        self.assertIn("前厅", loaded_state.visited_locations)
        self.assertEqual(loaded_state.event_log, ["测试事件"])
        self.assertEqual(loaded_state.player.rule_modifiers["analyze_bonus"], 2)


if __name__ == "__main__":
    unittest.main()
