# Changelog

## v2.1.0 - Phase 2 Complete

在 `v2.0.0` FastAPI baseline 上补齐 Phase 2 进入 Phase 3 前需要的配置查询、基础会话管理、schema 打磨、测试和系统设计文档。

已完成：

- 新增 `GET /games`：列出当前内存中的游戏会话摘要；
- 新增 `DELETE /games/{game_id}`：删除指定内存游戏会话；
- 新增 `GET /gods`：返回固定神明列表，方便未来前端创建角色；
- 为 `health`、`classes`、`gods`、`locations` 等只读接口补充 response model；
- 新增 `GameSessionSummary`、`GameListResponse`、`GameDeleteResponse`；
- 扩展 `session_store.py`，支持会话摘要、会话列表和会话删除；
- 扩展 `tests/test_phase2_api.py`，覆盖神明列表、游戏列表、删除成功、删除不存在游戏、空行动文本、OpenAPI schema；
- 新增 `docs/system_design.md`，记录 Phase 1、Phase 2、Phase 3 的系统设计、模块职责和数据流；
- 更新 `README.md`、`AGENTS.md`、`docs/phase2_api_plan.md`、`docs/technical_roadmap.md`；
- 将当前版本更新为 `v2.1.0 Phase 2 Complete`。

## v2.0.0 - Phase 2 FastAPI Baseline

在 `v1.4.0` API Readiness 结构上正式进入 Phase 2，把 Phase 1 CLI 核心能力暴露成最小 FastAPI 服务。

已完成：

- 新增 `phase2_api/`；
- 新增 FastAPI app 入口 `phase2_api/main.py`；
- 新增 Pydantic schemas；
- 新增 route modules：
  - `GET /health`
  - `GET /classes`
  - `GET /locations`
  - `POST /characters`
  - `POST /games`
  - `GET /games/{game_id}`
  - `POST /games/{game_id}/actions`
- 新增内存会话存储 `phase2_api/services/session_store.py`；
- API 通过 `phase1_cli.game_service.handle_player_input()` 复用 Phase 1 游戏核心；
- 新增 `tests/test_phase2_api.py`；
- 新增 FastAPI / Uvicorn / HTTPX 依赖；
- 更新 README 的运行方式、API 接口说明和 Phase 2 状态。

## v1.4.0 - Phase 1 CLI API Readiness

在 `v1.3.0` 导航辅助版本上做 Phase 2 前置整理，让当前 CLI 逻辑更容易迁移到 FastAPI。

已完成：

- 新增 `game_service.py`；
- 新增 `phase1_cli/__init__.py`，让 Phase 1 代码成为可导入 Python package；
- 把系统命令和玩家行动处理从 `main.py` 抽到 `handle_player_input()`；
- 新增 `GameResponse`，统一表达行动结果、系统命令、存档/读档信号和退出信号；
- 新增 `GameResponse.to_dict()`，为未来 API response 准备结构；
- 新增 `Character.to_public_dict()`；
- 新增 `GameState.to_public_dict()`；
- 新增 `docs/phase2_api_plan.md`；
- 新增 `tests/test_game_service.py`；
- 测试改为通过 `phase1_cli.xxx` 包路径导入模块；
- 更新 README 的项目结构、文件职责和 Phase 2 说明。

## v1.3.0 - Phase 1 CLI Navigation Polish

在 `v1.2.0` Demo 展示版本上继续打磨导航和回顾体验，让玩家更清楚自己在哪里、去过哪里、最近发生过什么。

已完成：

- 新增 `地图 / map` 命令；
- 新增 `日志 / log / history` 命令；
- `地图` 会显示当前位置、已到达地点、未探索地点和当前位置出口；
- `日志` 会显示最近行动事件，默认展示最近 5 条；
- 更新 `HELP_TEXT`，补充地图和日志命令；
- 更新 README 的版本状态、命令说明、项目结构和当前限制；
- 扩展 `tests/test_story_views.py`；
- 自动化测试覆盖地图和行动日志展示逻辑。

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
