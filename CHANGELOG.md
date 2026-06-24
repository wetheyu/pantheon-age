# Changelog

## v3.1.0 - Phase 3 Persistence Complete

在 `v3.0.0` SQLite baseline 基础上完成 Phase 3 持久化收尾，让 API 存储层更接近真实后端服务。

已完成：

- 新增 `phase3_persistence/config.py`，支持通过 `PANTHEON_DB_PATH` 配置 SQLite 数据库路径；
- 新增 `phase3_persistence/errors.py`，统一持久化层异常；
- `game_sessions.state_json` 改为版本化 snapshot envelope：`snapshot_version + state`；
- repository 兼容读取旧版未包裹的 `GameState` JSON；
- 新增 `game_events` 表，用 `game_id + event_index` 保存有序事件日志；
- 新增 `GET /games/{game_id}/events`，读取某局游戏的事件日志；
- `session_store.py` 将持久化异常统一转换为 API 500 错误；
- 补充 SQLite repository 测试：环境变量路径、版本化 snapshot、事件日志、坏 JSON；
- 补充 API 测试：事件日志读取、空事件、缺失游戏事件查询；
- 更新 README、AGENTS、系统设计、Phase 2 API 计划和技术路线文档；
- 将当前版本更新为 `v3.1.0 Phase 3 Persistence Complete`。

## v3.0.0 - Phase 3 Persistence Baseline

在 `v2.1.0` FastAPI Complete 基础上进入 Phase 3，把 API 游戏会话从进程内存升级为 SQLite 持久化。

已完成：

- 新增 `phase3_persistence/`；
- 新增 `phase3_persistence/sqlite_repository.py`；
- 使用 Python 标准库 `sqlite3` 保存 `game_id -> GameState JSON snapshot`；
- `POST /games` 创建游戏后写入 SQLite；
- `POST /games/{game_id}/actions` 执行动作后保存最新游戏状态；
- `GET /games`、`GET /games/{game_id}` 和 `DELETE /games/{game_id}` 改为通过 repository 访问持久化会话；
- 保持 Phase 2 API 路由形状不变；
- 新增 `tests/test_sqlite_repository.py`；
- API 测试改为使用临时 SQLite 数据库；
- `.gitignore` 忽略本地数据库文件 `data/*.sqlite3` 和 `data/*.db`；
- 更新 README、AGENTS、系统设计和技术路线文档。

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
- 将职业显示名从 `猎人 / Hunter` 调整为 `游侠 / Ranger`，内部 `class_id` 暂时保持 `hunter` 以兼容旧数据。
- 将 `圣律之神` 调整为 `审判之神`，并补充八大神明的典籍神名。
- 将伊斯特亚政体设定为海商寡头共和制。
- 扩展五大列强设定，并新增关键海峡国 `塞勒米亚苏丹国`。
- 扩展八大神明和六大职业的详细设定，包括教会、禁忌、祝福、诅咒、职业定位、优势场景和玩法机制倾向。
- 新增五大列强前三核心城市设定，并补充塞勒米亚、罗斯维亚等其他重要国家首都。

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
