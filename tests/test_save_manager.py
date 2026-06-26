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
        self.assertEqual(character.attributes["physique"], 15)
        self.assertEqual(character.class_level, 1)
        self.assertEqual(character.faith_level, 1)
        self.assertEqual(character.ascension_rank, 0)
        self.assertEqual(character.favor, 1)
        self.assertIn("正面战斗基础", character.progression_skills)
        self.assertIn("临终残响", character.talents)
        self.assertIn("安魂", character.prayers)
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
        self.assertEqual(loaded_state.player.attributes["knowledge"], 15)
        self.assertEqual(loaded_state.player.class_level, 1)
        self.assertEqual(loaded_state.player.faith_level, 1)
        self.assertIn("异常解析基础", loaded_state.player.progression_skills)
        self.assertIn("证词敏感", loaded_state.player.talents)
        self.assertIn("白塔明证", loaded_state.player.prayers)
        self.assertIn("泥泞脚印", loaded_state.player.clues)
        self.assertIn("前厅", loaded_state.visited_locations)
        self.assertEqual(loaded_state.event_log, ["测试事件"])
        self.assertEqual(loaded_state.player.rule_modifiers["analyze_bonus"], 2)

    def test_old_character_payload_gets_phase8_defaults(self):
        old_payload = build_character("旧档", "rogue", "隐秘之神").to_dict()
        old_payload.pop("attributes")
        old_payload.pop("progression")

        character = build_character("占位", "warrior", "战争之神").from_dict(old_payload)

        self.assertEqual(character.name, "旧档")
        self.assertEqual(character.attributes["agility"], 15)
        self.assertEqual(character.class_level, 1)
        self.assertEqual(character.faith_level, 1)
        self.assertEqual(character.ascension_rank, 0)
        self.assertEqual(character.favor, 1)
        self.assertIn("潜行开锁基础", character.progression_skills)
        self.assertIn("影中低语", character.talents)
        self.assertIn("无声祈祷", character.prayers)


if __name__ == "__main__":
    unittest.main()
