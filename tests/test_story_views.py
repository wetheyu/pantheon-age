import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "phase1_cli"))

from character import build_character
from game_state import GameState
from story import render_clues, render_goal


class StoryViewTests(unittest.TestCase):
    def test_goal_shows_core_clue_progress(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.player.add_clue("被撕掉的档案页")

        text = render_goal(state)

        self.assertIn("当前目标", text)
        self.assertIn("核心线索进度：1/5", text)
        self.assertIn("揭露真相需要至少 4 个核心线索", text)

    def test_clues_show_empty_hint(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))

        text = render_clues(state)

        self.assertIn("当前线索：暂无", text)
        self.assertIn("旧档案室", text)

    def test_clues_mark_core_clues(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.player.add_clue("泥泞脚印")
        state.player.add_clue("深渊污染痕迹")

        text = render_clues(state)

        self.assertIn("[普通] 泥泞脚印", text)
        self.assertIn("[核心] 深渊污染痕迹", text)
        self.assertIn("核心线索进度：1/5", text)


if __name__ == "__main__":
    unittest.main()
