# Phase 2 API Plan

Phase 2 的目标是把当前 CLI 游戏拆成 FastAPI 服务。Phase 1.4 已经先抽出 `game_service.py`，所以未来 API 不需要调用 `input()`、`print()` 或终端颜色逻辑。

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

## Phase 2 第一版不做什么

- 不接 LLM；
- 不做用户登录；
- 不做复杂多存档系统；
- 不做前端；
- 不做 Docker；
- 不做 RAG。

第一版只需要把当前 CLI 能力稳定地暴露成 REST API。

## Phase 2 推荐实现顺序

1. 添加 `fastapi` 和 `uvicorn` 依赖。
2. 新建 `phase2_api/`。
3. 添加 Pydantic request/response schema。
4. 用内存 dict 暂存 `game_id -> GameState`。
5. 接入 `game_service.handle_player_input()`。
6. 给 API 加最小测试。
7. 再考虑 JSON 文件或 SQLite 持久化。
