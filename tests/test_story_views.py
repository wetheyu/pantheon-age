import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.story import (
    render_clues,
    render_goal,
    render_help,
    render_log,
    render_map,
    render_roll_line,
    render_status,
)


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

    def test_map_marks_current_and_visited_locations(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.move_to("前厅")

        text = render_map(state)

        self.assertIn("[当前位置][已到达] 前厅", text)
        self.assertIn("[已到达] 修道院门口", text)
        self.assertIn("[未探索] 钟楼", text)
        self.assertIn("当前可前往：修道院门口, 祈祷大厅, 旧档案室", text)

    def test_log_shows_recent_events(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.add_event("第一条事件")
        state.add_event("第二条事件")

        text = render_log(state, limit=1)

        self.assertIn("最近 1 条 / 共 2 条", text)
        self.assertIn("2. 第二条事件", text)
        self.assertNotIn("第一条事件", text)

    def test_log_shows_empty_hint(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))

        text = render_log(state)

        self.assertIn("行动日志：暂无", text)

    def test_status_shows_phase8_progression_fields(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))

        text = render_status(state)

        self.assertIn("职业等级 1", text)
        self.assertIn("信仰等级 1", text)
        self.assertIn("神秘阶位 0", text)
        self.assertIn("Favor 1", text)
        self.assertIn("Revelation 0", text)
        self.assertIn("六属性：体魄 15", text)
        self.assertIn("职业技能：正面战斗基础", text)
        self.assertIn("信仰天赋：临终残响", text)
        self.assertIn("祷告：安魂", text)
        self.assertIn("可用道具：制式佩剑[普通]", text)
        self.assertIn("晋升状态：暂不可晋升", text)

    def test_help_explains_phase8_world_mode_mechanics(self):
        text = render_help()

        self.assertIn("开放世界模式可以直接说自然语言行动", text)
        self.assertIn("使用开锁工具撬开仓库门锁", text)
        self.assertIn("职业技能、信仰天赋、祷告和道具", text)
        self.assertIn("晋升必须满足资源和等级条件", text)

    def test_roll_line_shows_faith_bonuses(self):
        roll = {
            "d20": 10,
            "stat": "faith",
            "stat_value": 8,
            "modifier": 6,
            "modifier_label": "行动修正",
            "total": 24,
            "dc": 17,
            "success": True,
            "risk_label": "神秘学",
            "margin": 7,
            "outcome_label": "小成功",
            "attribute_profile": {
                "primary_label": "共鸣",
                "primary_attribute": "communion",
                "primary_value": 14,
                "modifier": 2,
            },
            "talent_bonuses": [{"name": "临终残响", "bonus": 1}],
            "prayer_bonuses": [{"name": "安魂", "bonus": 3}],
            "item_bonuses": [{"name": "圣徽", "bonus": 1}],
            "consumed_items": ["仪式粉末"],
        }

        text = render_roll_line(roll)

        self.assertIn("属性：共鸣 14 +2", text)
        self.assertIn("天赋：临终残响 +1", text)
        self.assertIn("祷告：安魂 +3", text)
        self.assertIn("道具：圣徽 +1", text)
        self.assertIn("消耗：仪式粉末", text)


if __name__ == "__main__":
    unittest.main()
