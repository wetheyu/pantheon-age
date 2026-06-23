# Changelog

## v1.2.0 - Phase 1 CLI Demo Polish

在 `v1.1.0` 存档/读档版本上继续打磨 CLI 展示体验，让项目更适合试玩、演示和面试讲解。

已完成：

- 新增 `目标 / goal / objective` 命令；
- 新增 `线索 / clues / clue` 命令；
- `目标` 会显示主线目标、核心线索进度和危险阈值；
- `线索` 会显示已发现线索，并标记普通线索和核心线索；
- 更新 `HELP_TEXT`，补充查看类命令；
- 更新 README，加入普通逃离路线和揭露真相路线；
- 新增 `tests/test_story_views.py`；
- 自动化测试覆盖目标和线索展示逻辑。

## v1.1.0 - Phase 1 CLI Save/Load

在 `v1.0.0` CLI baseline 上继续打磨，重点解决“游戏状态只在内存中，退出后丢失”的问题，并补上最小自动化测试。

已完成：

- 新增 `save_manager.py`；
- 支持本地 JSON 存档：游戏中输入 `存档`；
- 支持本地 JSON 读档：游戏中输入 `读档`；
- 启动时检测到本地存档可选择读取；
- `Character` 和 `GameState` 支持 `from_dict()`；
- 存档会保存职业规则修正、线索、背包、当前位置、回合数、访问地点和事件日志；
- 新增 `tests/test_intent_parser.py`；
- 新增 `tests/test_save_manager.py`；
- 使用 Python 标准库 `unittest`，不引入第三方测试依赖；
- 更新 README 的运行、测试、存档说明。

## v1.0.0 - Phase 1 CLI Baseline

项目正式命名为「神座纪元 / Pantheon Age」。

说明：`Phase 1` 命令行版本作为项目正式公开起点 `v1.0.0` 记录。

已完成：

- Python 标准库命令行文字冒险；
- 角色创建、职业系统、神明选择；
- 雾中修道院小副本；
- 关键词意图识别；
- d20 Rule Engine；
- HP / SAN / Suspicion / Corruption 状态管理；
- 地点移动、调查、分析、攻击、祈祷、休息、潜行、道具使用；
- 逐步线索获得；
- 普通逃离、揭露真相、深渊污染等结局；
- 修正“前往祈祷大厅”误判为祈祷的问题；
- 终端行动结果分隔和基础颜色提示；
- README 与 CHANGELOG 初版。
