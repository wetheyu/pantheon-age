# Phase 2 API Plan

Phase 2 的目标是把当前 CLI 游戏拆成 FastAPI 服务。Phase 1.4 已经先抽出 `game_service.py`，所以未来 API 不需要调用 `input()`、`print()` 或终端颜色逻辑。

当前状态：`v2.1.0 Phase 2 Complete` 已经实现最小 API 骨架、基础配置查询、基础会话管理、schema 打磨和 API 测试，并使用内存 dict 暂存 `game_id -> GameState`。

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
save_manager.py 当前负责本地 JSON，Phase 2 可替换成数据库仓储层。
```

## 模块映射

- `game_service.handle_player_input(state, user_text)`：未来 `POST /games/{game_id}/actions` 的核心逻辑。
- `GameResponse.to_dict()`：未来接口响应 JSON 的起点。
- `GameState.to_public_dict()`：未来 `GET /games/{game_id}` 的响应起点。
- `Character.to_public_dict()`：未来角色展示响应的起点。
- `Character.to_dict()` / `GameState.to_dict()`：数据库持久化字段的参考。

## 建议接口

以下接口已在 Phase 2 中实现。

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

响应应包含：

- `game_id`
- `state`
- `opening_text`

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
  "text": "进入前厅"
}
```

响应可以直接参考：

```python
handle_player_input(state, text).to_dict()
```

### `GET /games`

列出当前内存中仍然存在的游戏会话摘要。

响应包含：

- `game_id`
- 玩家名
- 职业
- 信仰神明
- 当前位置
- 回合数
- 是否已经结束

### `DELETE /games/{game_id}`

删除当前内存中的某一局游戏。

说明：这不是数据库删除，因为 Phase 2 还没有数据库。它只会从当前运行中的 API 进程内存里移除这一局游戏。

## Phase 2 第一版不做什么

- 不接 LLM；
- 不做用户登录；
- 不做复杂多存档系统；
- 不做前端；
- 不做 Docker；
- 不做 RAG。

第一版只需要把当前 CLI 能力稳定地暴露成 REST API。

当前已完成这一目标。`v2.1.0` 又补齐了神明配置查询、基础会话管理、schema response model、API 测试和系统设计文档。Phase 2 到这里已经可以作为进入 Phase 3 持久化之前的完整收尾版本。

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
11. 再考虑 JSON 文件、SQLite 或 PostgreSQL 持久化。后续 Phase 3。
