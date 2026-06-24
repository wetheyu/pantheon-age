# 神座纪元 / Pantheon Age

**神座纪元（Pantheon Age）** 是一个以固定神明体系、维多利亚神秘学、调查冒险和规则裁定为核心的文字冒险系统。当前版本是 `v3.1.0 Phase 3 Persistence Complete`，已经把 Phase 1 CLI 核心能力暴露成 REST API，并把 API 游戏会话从内存升级为 SQLite 持久化。当前阶段不接 LLM、不做前端、不做 Docker，目标是先把「可复用规则核心 + FastAPI 服务层 + SQLite 游戏会话 + 事件日志持久化 + API 测试 + 系统设计文档」完整跑通。

## 项目动机

这个项目的灵感来源于《诡秘之主》和《诸神愚戏》两部小说。我很喜欢其中神秘学、神明体系、异常事件、调查冒险和世界观层层展开的感觉，但这类题材在市面上并不算多。

LLM 的出现让我看到了一种新的可能：不只是被动阅读故事，而是构建一个由规则约束、由 AI 生成内容、由玩家自由探索的故事世界。因此我希望用 `Pantheon Age` 打造一个属于自己的 AI Agent 项目，让它既能作为工程实践，也能成为一个可以长期娱乐和扩展的个人世界。

核心原则：

```text
LLM 负责创造可能性，规则系统确认现实。
LLM 只能 propose，系统负责 validate，只有 validated content 才能 commit。
```

当前版本先由固定模板负责叙事，Rule Engine 负责所有会影响游戏结果的事情。FastAPI 只负责暴露接口，不决定规则。长期方向是把它扩展成受规则约束的 LLM Agent 无限流冒险框架。

## 版本状态

```text
内部里程碑：Phase 3 Persistence Complete
对外起点版本：v1.0.0
当前公开版本：v3.1.0
```

`v3.1.0` 已完成：

- 命令行连续游玩；
- 角色创建、职业、神明选择；
- 关键词意图识别；
- d20 属性检定；
- Rule Engine 状态裁定；
- HP / SAN / Suspicion / Corruption 管理；
- 道具、线索、地点移动；
- 三类主要结局；
- 终端颜色和行动结果分隔；
- 修正“前往祈祷大厅”误判为祈祷的问题；
- 本地 JSON 存档 / 读档；
- 最小自动化测试；
- `目标` 命令：查看当前通关目标和核心线索进度；
- `线索` 命令：查看已发现线索及核心/普通标记；
- `地图` 命令：查看当前位置、已到达地点、未探索地点和可前往出口；
- `日志` 命令：查看最近行动事件；
- `game_service.py` 服务层：把玩家输入处理从 CLI 中抽离；
- `GameResponse.to_dict()`：为未来 API 响应准备结构化返回；
- `Character.to_public_dict()` / `GameState.to_public_dict()`：为未来状态查询接口准备公开数据结构；
- `phase2_api/` FastAPI 服务层；
- `GET /health`；
- `GET /classes`；
- `GET /gods`；
- `GET /locations`；
- `POST /characters`；
- `POST /games`；
- `GET /games`；
- `GET /games/{game_id}`；
- `GET /games/{game_id}/events`；
- `DELETE /games/{game_id}`；
- `POST /games/{game_id}/actions`；
- SQLite 游戏会话持久化：`game_id -> versioned GameState JSON snapshot`；
- SQLite 事件日志持久化：`game_id -> ordered game events`；
- 可通过 `PANTHEON_DB_PATH` 配置 API 数据库路径；
- 持久化层错误统一转换为 API 错误；
- 基础会话管理：创建、读取、列出、提交行动后保存、删除指定游戏局；
- API response model：为健康检查、职业、神明、地点、游戏会话等接口补充响应结构；
- API 自动化测试；
- SQLite repository 自动化测试；
- Phase 2 API 计划文档；
- 系统设计文档 `docs/system_design.md`；
- 世界观设定集 `docs/world_bible.md`；
- LLM 运行逻辑设计 `docs/llm_runtime_design.md`；
- 完整技术路线图 `docs/technical_roadmap.md`；
- 项目长期开发规则 `AGENTS.md`；
- README Demo 路线；
- README 和 CHANGELOG 项目记录。

## 项目结构

```text
project-root/
  phase1_cli/
    main.py
    __init__.py
    character.py
    game_state.py
    game_service.py
    intent_parser.py
    rule_engine.py
    save_manager.py
    story.py
    data.py
    utils.py
  phase2_api/
    main.py
    schemas.py
    routes/
      health.py
      classes.py
      gods.py
      locations.py
      characters.py
      games.py
    services/
      session_store.py
  phase3_persistence/
    __init__.py
    config.py
    errors.py
    sqlite_repository.py
  tests/
    test_phase2_api.py
    test_sqlite_repository.py
    test_game_service.py
    test_intent_parser.py
    test_save_manager.py
    test_story_views.py
  docs/
    phase2_api_plan.md
    system_design.md
    world_bible.md
    llm_runtime_design.md
    technical_roadmap.md
  AGENTS.md
  CHANGELOG.md
  README.md
  requirements.txt
```

## 设计文档

- [AGENTS.md](AGENTS.md)：项目长期开发规则。记录架构边界、测试命令、Git 操作边界和 Phase 2 方向。
- [docs/world_bible.md](docs/world_bible.md)：世界观设定集。记录维多利亚时代背景、五大列强、其他重要国家、核心城市、八大神明、六大职业、身份系统和世界事实分级。
- [docs/llm_runtime_design.md](docs/llm_runtime_design.md)：LLM 运行逻辑设计。记录 `propose -> validate -> commit`、RAG、内容分级、场景提案、事件生成和防止上下文污染的规则。
- [docs/phase2_api_plan.md](docs/phase2_api_plan.md)：Phase 2 FastAPI 拆分计划。
- [docs/system_design.md](docs/system_design.md)：系统设计文档。记录 Phase 1、Phase 2、Phase 3 的模块职责、数据流和演进边界。
- [docs/technical_roadmap.md](docs/technical_roadmap.md)：完整愿景所需技术栈与分阶段采用路线。

## 怎么运行

需要 Python 3.10+。

本机已创建好虚拟环境：

```bash
cd <project-root>
source .venv/bin/activate
./.venv/bin/python --version
```

当前虚拟环境版本：

```text
Python 3.12.13
```

安装依赖：

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

启动 CLI 游戏：

```bash
cd <project-root>
./.venv/bin/python -m phase1_cli.main
```

启动后按提示创建角色、选择职业和信仰神明，然后输入自然语言行动。

启动 FastAPI 服务：

```bash
cd <project-root>
./.venv/bin/uvicorn phase2_api.main:app --reload
```

启动后可以访问：

```text
http://127.0.0.1:8000/docs
```

这是 FastAPI 自动生成的 API 文档页面。

## API 接口

当前 API 提供：

```text
GET    /health
GET    /classes
GET    /gods
GET    /locations
POST   /characters
POST   /games
GET    /games
GET    /games/{game_id}
GET    /games/{game_id}/events
DELETE /games/{game_id}
POST   /games/{game_id}/actions
```

创建游戏请求示例：

```json
{
  "name": "阿洛",
  "class_id": "warrior",
  "god": "死亡之神"
}
```

提交行动请求示例：

```json
{
  "text": "进入前厅"
}
```

查看当前数据库中的游戏局：

```text
GET /games
```

查看某局游戏的事件日志：

```text
GET /games/{game_id}/events
```

删除当前数据库中的游戏局：

```text
DELETE /games/{game_id}
```

API 当前使用 SQLite 保存游戏状态，默认数据库文件位于：

```text
data/pantheon_age.sqlite3
```

也可以通过环境变量指定数据库路径：

```bash
PANTHEON_DB_PATH=data/dev.sqlite3 ./.venv/bin/uvicorn phase2_api.main:app
```

这个文件属于本地运行数据，已通过 `.gitignore` 忽略，不会提交到 GitHub。

## 支持的行动

示例：

```text
进入前厅
前往祈祷大厅
调查脚印
搜索档案柜
分析墙上的符文
攻击黑影
向死亡之神祈祷
悄悄撬开档案柜
使用止血药剂
喝下镇静药剂
休息一下
目标
线索
地图
日志
```

系统命令：

```text
帮助
状态
目标
线索
地图
日志
存档
读档
退出
```

## Demo 路线

普通逃离路线：

```text
进入前厅
进入旧档案室
调查档案柜
返回前厅
返回修道院门口
```

揭露真相路线建议选择法师、牧师或炼金术士。因为检定有 d20 随机性，失败时可以重复调查、休息、祈祷或读档重试。

```text
进入前厅
进入旧档案室
调查档案柜
调查档案柜
进入地下墓室
分析深渊污染
祈祷亡者
返回旧档案室
返回前厅
进入祈祷大厅
进入钟楼
分析钟声
```

随时可以输入：

```text
目标
线索
地图
日志
存档
读档
```

## 存档 / 读档

游戏中输入：

```text
存档
```

会把当前游戏状态保存到：

```text
saves/save.json
```

游戏中输入：

```text
读档
```

会从本地 JSON 存档恢复角色、地点、回合、线索、背包和事件日志。

本地存档属于个人运行数据，已通过 `.gitignore` 忽略，不会提交到 GitHub。

## 运行测试

```bash
cd <project-root>
./.venv/bin/python -m py_compile phase1_cli/*.py tests/*.py
./.venv/bin/python -m py_compile phase2_api/*.py phase2_api/routes/*.py phase2_api/services/*.py
./.venv/bin/python -m py_compile phase3_persistence/*.py
./.venv/bin/python -m unittest discover -s tests
```

## 文件职责

- `main.py`：CLI 程序入口，负责创建角色、启动循环、读取玩家输入、打印结果、处理本地存档。
- `character.py`：角色数据结构、职业选择、初始属性/HP/SAN/道具计算。
- `game_state.py`：保存当前回合、当前位置、是否结束、访问地点和事件日志。
- `game_service.py`：可复用服务层，负责把玩家输入转换成结构化 `GameResponse`。未来 FastAPI 会优先复用这里。
- `intent_parser.py`：使用关键词把自然语言行动解析成标准 intent dict。
- `rule_engine.py`：当前版本的工程核心，负责 d20、属性检定、职业加成、战斗、状态变化、道具、线索和结局。
- `save_manager.py`：负责本地 JSON 存档与读档。
- `story.py`：根据规则结果输出固定剧情文本。未来可替换为 LLM 叙事层。
- `data.py`：项目名、版本号、职业、地图、地点描述、神明、道具、线索、关键词等配置。
- `utils.py`：通用小工具，例如安全输入、数值限制、编号选择、终端颜色。
- `phase2_api/main.py`：FastAPI 应用入口。
- `phase2_api/schemas.py`：API 请求和响应 schema。
- `phase2_api/routes/`：API 路由。
- `phase2_api/services/session_store.py`：API 会话服务，负责创建、读取、列出、删除和提交行动；Phase 3 起底层调用 SQLite repository。
- `phase3_persistence/sqlite_repository.py`：SQLite 持久化层，负责保存和恢复 API 游戏会话。

## Rule Engine 控制了什么

Rule Engine 负责所有核心状态：

- HP 变化；
- SAN 变化；
- Suspicion 变化；
- Corruption 变化；
- d20 属性检定；
- 职业加成；
- 地点移动；
- 战斗结果；
- 道具消耗；
- 线索获得；
- 三个主要结局判断。

基础检定公式：

```text
d20 + 属性值 + 职业修正 >= DC
```

## 职业如何影响检定

长期世界观中的六大职业为：

```text
骑士、法师、密探、游侠、牧师、炼金术士
```

当前 CLI 代码中仍保留早期命名 `战士 / 盗贼`，后续会与世界观文档统一为 `骑士 / 密探`。

职业通过三类配置影响规则：

- `stat_bonus`：改变初始力量、敏捷、智力、信仰。
- `hp_bonus` / `san_bonus`：改变初始 HP 和 SAN。
- `rule_modifiers`：给特定行动加成或惩罚。

当前 CLI 例子：

- 战士攻击更强：`attack_bonus +2`。
- 法师分析神秘知识更强：`analyze_bonus +2`、`lore_bonus +2`，但接触禁忌知识 SAN 风险更高。
- 盗贼潜行和开锁更强，但隐秘路线会增加 Suspicion。
- 游侠追踪和侦察更强。
- 牧师祈祷、净化、抵抗污染更强。
- 炼金术士使用药剂、鉴定异常物质更强。

## 当前限制

- 意图识别是关键词规则，不是真正的自然语言理解。
- 剧情文本是固定模板，不接 LLM。
- CLI 当前只有单一默认本地存档，还没有多存档位或账号系统。
- API 当前使用 SQLite 保存游戏会话，还没有 PostgreSQL、账号系统或多用户隔离。
- API 当前不处理本地 JSON 存档/读档，CLI 仍保留本地存档功能。
- 代码职业命名还未完全对齐世界观文档，后续会把 `战士 / 盗贼` 统一为 `骑士 / 密探`。
- 地图只有「雾中修道院」一个小副本。
- API 已经持久化行动日志，但还没有搜索、分类或完整时间线界面。
- 战斗和道具系统是最小可玩版本，还没有复杂怪物、装备或任务系统。

## Phase 2：FastAPI Complete

Phase 2 已经把 CLI 核心能力暴露成 REST API：

- `POST /characters`：创建角色；
- `POST /games`：创建新游戏；
- `GET /games`：列出当前游戏局；
- `GET /games/{game_id}`：读取当前状态；
- `DELETE /games/{game_id}`：删除当前游戏局；
- `POST /games/{game_id}/actions`：提交玩家行动；
- `GET /classes`：查看职业配置；
- `GET /gods`：查看固定神明列表；
- `GET /locations`：查看地图配置。

当前的模块拆分：

- `phase1_cli/` 已经是可导入 Python package；
- `game_service.py` 可以直接服务 API action 请求；
- `intent_parser.py` 可以直接服务 API 请求；
- `rule_engine.py` 可以直接返回 JSON-like dict；
- `Character.to_dict()` 和 `GameState.to_dict()` 可以作为 Pydantic schema 的起点；
- `Character.to_public_dict()`、`GameState.to_public_dict()` 和 `GameResponse.to_dict()` 可以作为 API response 的起点；
- `story.py` 未来可以替换成 LLM 调用层。
- `phase2_api/` 只负责 API 路由、schema 和会话服务，不复制规则逻辑。

更详细的 Phase 2 拆分计划见 [docs/phase2_api_plan.md](docs/phase2_api_plan.md)。

## Phase 3：Persistence Complete

当前 Phase 3 已经把 API 游戏会话持久化到 SQLite：

- `phase3_persistence/config.py`：负责读取 `PANTHEON_DB_PATH`；
- `phase3_persistence/errors.py`：定义持久化层错误；
- `phase3_persistence/sqlite_repository.py`：负责 SQLite 表结构、保存、读取、列表、删除和事件查询；
- `phase2_api/services/session_store.py`：继续作为 API 服务层，但底层改为调用 repository；
- `POST /games` 创建游戏后会写入数据库；
- `POST /games/{game_id}/actions` 执行行动后会保存最新 `GameState`；
- `GET /games`、`GET /games/{game_id}` 和 `DELETE /games/{game_id}` 都通过 SQLite 查询或删除。
- `GET /games/{game_id}/events` 可以读取某局游戏的有序事件日志。

保存结构：

```text
game_sessions:
  game_id -> snapshot_version + GameState JSON snapshot

game_events:
  game_id + event_index -> event text
```

默认数据库路径：

```text
data/pantheon_age.sqlite3
```

这一步的意义是：API route 形状基本稳定，内部存储从“进程内存”升级成“可重启后保留的本地数据库”，并为后续长期记忆、事件回放和 LLM 记忆总结打基础。

## 这个阶段学到什么

通过 `v3.1.0`，你会接触到：

- Python 文件拆分；
- dict/list/dataclass；
- 命令行输入输出；
- 游戏循环；
- 状态管理；
- JSON 文件读写和本地存档；
- `unittest` 最小自动化测试；
- 地图访问记录和行动日志展示；
- CLI 层和服务层解耦；
- 面向 API 的结构化响应；
- FastAPI 应用结构；
- Pydantic 请求/响应 schema；
- 内存会话管理；
- REST 会话生命周期：创建、列表、读取、行动、删除；
- SQLite 持久化；
- Repository 层；
- 版本化 JSON snapshot 存储；
- 事件日志独立表；
- 环境变量配置；
- 后端异常边界；
- API 自动化测试；
- 关键词意图识别；
- d20 随机检定；
- 配置化职业系统；
- 规则引擎与剧情文本解耦；
- 为 FastAPI、数据库和 LLM Agent Workflow 预留接口。

## 长期 LLM Agent 方向

项目未来不是让 LLM 直接扮演全能游戏主持人，而是让 LLM 在规则系统约束下生成内容。

目标流程：

```text
玩家输入
  ↓
意图解析
  ↓
规则引擎裁定
  ↓
LLM 生成候选场景 / 事件 / 叙事
  ↓
validator 校验
  ↓
memory_manager 决定是否写入记忆
  ↓
最终叙事输出
```

关键边界：

- 玩家输入不是事实；
- LLM 输出不是事实；
- 状态变化必须结构化；
- 叙事必须服从 `rule_engine.py` 的裁定结果；
- 世界观核心事实由 `world_bible.md` 维护；
- LLM 运行规则由 `llm_runtime_design.md` 维护。
