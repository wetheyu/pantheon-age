# Phase 2 API Plan

Phase 2 的目标是把当前 CLI 游戏拆成 FastAPI 服务。Phase 1.4 已经先抽出 `game_service.py`，所以未来 API 不需要调用 `input()`、`print()` 或终端颜色逻辑。

当前状态：`v2.1.0 Phase 2 Complete` 已经实现最小 API 骨架、基础配置查询、基础会话管理、schema 打磨和 API 测试。Phase 2 当时使用内存 dict 暂存 `game_id -> GameState`；后续 `v3.1.0 Phase 3 Persistence Complete` 已经把 API 会话底层升级为 SQLite repository，并新增事件日志查询。`v9.1.0 Phase 9.1` 又补齐了前端产品化所需的 world-mode 建档合同和行动响应分层。

当前 `phase1_cli/` 已经是 Python package，Phase 2 可以直接从项目根目录导入：

```python
from phase1_cli.game_service import handle_player_input
```

## 设计原则

```text
CLI 负责输入输出。
game_service.py 负责处理玩家输入。
rule_engine.py 负责规则裁定。
story.py 负责文本渲染。
save_manager.py 负责 CLI 本地 JSON 存档；API 会话在 Phase 3 起由 SQLite repository 持久化。
```

## 模块映射

- `game_service.handle_player_input(state, user_text)`：未来 `POST /games/{game_id}/actions` 的核心逻辑。
- `GameResponse.to_dict()`：未来接口响应 JSON 的起点。
- `GameState.to_public_dict()`：未来 `GET /games/{game_id}` 的响应起点。
- `Character.to_public_dict()`：未来角色展示响应的起点。
- `Character.to_dict()` / `GameState.to_dict()`：数据库持久化字段的参考。

## 建议接口

以下接口已在 Phase 2 及后续 API 产品化阶段中实现。

### `GET /health`

检查服务是否启动。

响应示例：

```json
{
  "status": "ok",
  "project": "Pantheon Age"
}
```

### `GET /classes`

返回职业配置，用于前端创建角色页。

### `GET /gods`

返回固定神明列表，用于前端创建角色页。

### `GET /locations`

返回地图配置，用于前端地图页。

### `GET /origins`

返回 world-mode 可选出身国家、城市、民族和常用身份背景，用于前端创建角色页。

### `POST /characters`

创建角色。

请求示例：

```json
{
  "name": "阿洛",
  "class_id": "warrior",
  "god": "死亡之神"
}
```

### `POST /games`

创建新游戏。

世界模式请求示例：

```json
{
  "name": "伊芙",
  "class_id": "mage",
  "god": "真理之神",
  "game_mode": "world",
  "origin_country_id": "lumiere",
  "origin_city": "维拉尔",
  "background_id": "dock_scribe"
}
```

响应应包含：

- `game_id`
- `state`
- `opening_text`
- `game_mode`
- `setup`

### `GET /games/{game_id}`

读取当前游戏状态。

响应可以直接参考：

```python
state.to_public_dict()
```

### `POST /games/{game_id}/actions`

提交玩家行动。

请求示例：

```json
{
  "text": "去码头账房查昨晚的船只记录",
  "include_debug": false
}
```

响应现在分为前端常用字段和兼容旧字段：

```text
story       玩家可见叙事
state       公开状态
mechanics   掷骰、提交效果和规则结果摘要
debug       可选调试信息，默认不返回
response    兼容旧客户端的完整 GameResponse.to_dict()
```

### `GET /games/{game_id}/events`

读取某一局游戏已经提交并持久化的事件日志。

说明：这个接口在 Phase 3 中新增，用于验证事件日志已经从 `GameState.event_log` 同步到 SQLite 的 `game_events` 表。

### `GET /games`

列出当前游戏会话摘要。

响应包含：

- `game_id`
- 玩家名
- 职业
- 信仰神明
- 当前位置
- 回合数
- 是否已经结束

### `DELETE /games/{game_id}`

删除某一局游戏。

说明：Phase 2 完成时这里删除的是进程内存里的会话；Phase 3 起这里删除的是 SQLite repository 中的会话记录。

## Phase 2 第一版不做什么

- 不接 LLM；
- 不做用户登录；
- 不做复杂多存档系统；
- 不做前端；
- 不做 Docker；
- 不做 RAG。

第一版只需要把当前 CLI 能力稳定地暴露成 REST API。

当前已完成这一目标。`v2.1.0` 又补齐了神明配置查询、基础会话管理、schema response model、API 测试和系统设计文档。Phase 2 到这里已经可以作为进入 Phase 3 持久化之前的完整收尾版本。

后续 `v3.0.0` 已经开始 Phase 3，把 API 会话存储从内存 dict 替换为 SQLite repository，但 API 路由形状保持不变。

后续 `v3.1.0` 又补齐了数据库路径配置、版本化 snapshot、事件日志持久化和 `GET /games/{game_id}/events`。

## Phase 2 推荐实现顺序

1. 添加 `fastapi` 和 `uvicorn` 依赖。已完成。
2. 新建 `phase2_api/`。已完成。
3. 添加 Pydantic request/response schema。已完成。
4. 用内存 dict 暂存 `game_id -> GameState`。已完成。
5. 接入 `game_service.handle_player_input()`。已完成。
6. 给 API 加最小测试。已完成。
7. 补充 `GET /gods`，让角色创建所需配置查询完整。已完成。
8. 增加基础会话管理：`GET /games` 和 `DELETE /games/{game_id}`。已完成。
9. 补充 response model 和 API 测试。已完成。
10. 补充系统设计文档，记录 Phase 1、Phase 2、Phase 3 的数据流。已完成。
11. 再考虑 JSON 文件、SQLite 或 PostgreSQL 持久化。Phase 3 已先采用 SQLite baseline。
