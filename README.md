# 神座纪元 / Pantheon Age

**神座纪元（Pantheon Age）** 是一个 rule-stabilized LLM Agent text adventure framework。项目以固定神明体系、维多利亚神秘学、调查冒险和规则裁定为核心，目标是让 LLM 负责生成可能性，让程序负责验证、记忆和提交世界现实。

当前版本是 `v6.0.0 Phase 6 World Knowledge And Persistent Memory`。项目已经具备 CLI 可玩闭环、FastAPI 服务层、SQLite 持久化、Agentic Runtime、canon retrieval、长期记忆、generated fact commit、relationship memory、memory summarizer、embedding provider 边界和 SQLite vector cache。

当前主线是 `agentic_runtime/`。旧的 `llm_runtime/ActionCandidate` 路径保留为 Phase 4 兼容层和结构化 LLM 示例，不再作为最终玩法方向。

## 项目动机

这个项目的灵感来源于《诡秘之主》和《诸神愚戏》两部小说。我很喜欢其中神秘学、神明体系、异常事件、调查冒险和世界观层层展开的感觉，但这类题材在市面上并不算多。

LLM 的出现让我看到了一种新的可能：不只是被动阅读故事，而是构建一个由规则约束、由 AI 生成内容、由玩家自由探索的故事世界。因此我希望用 `Pantheon Age` 打造一个属于自己的 AI Agent 项目，让它既能作为工程实践，也能成为一个可以长期娱乐和扩展的个人世界。

核心原则：

```text
LLM 负责创造可能性。
规则限制的是改变现实的权限，而不是想象力。
规则系统确认现实。
LLM 只能 propose，系统负责 validate，只有 validated content 才能 commit。
```

当前版本先建立 CLI、API、持久化和 LLM 运行时边界。长期方向不是让 LLM 只给固定规则文本润色，而是让 LLM 生成行动、场景、NPC、事件和叙事可能性，再由规则引擎、validator 和 memory 层决定哪些内容有权改变世界现实。

## 项目状态

```text
当前里程碑：v6.0.0 / Phase 6 World Knowledge And Persistent Memory
当前主线：Agentic Runtime + Canon Retrieval + Persistent Memory
下一阶段：Phase 7 Minimum Playable Experience Calibration
```

当前版本已经完成从“CLI 文字冒险原型”到“Agentic Runtime 地基”的转变：

- `phase1_cli/`：保留教程模式、CLI 入口、核心状态模型和服务层；
- `phase2_api/`：提供 FastAPI 游戏会话接口；
- `phase3_persistence/`：使用 SQLite 持久化游戏会话、事件日志和长期记忆；
- `llm_runtime/`：保留 Phase 4 结构化 LLM provider、prompt 和 fallback 能力；
- `agentic_runtime/`：作为当前 world-mode 主线，负责开放行动理解、裁定建议、临时世界生成、验证、状态提交和记忆整理；
- `rag/` + `docs/canon/`：提供 canon chunk、keyword / embedding / hybrid / vector 检索、OpenAI embedding provider 边界和 SQLite vector cache。

## 核心能力

### 可玩闭环

- CLI tutorial mode：雾中修道院固定场景、职业/神明选择、d20 检定、HP / SAN / Suspicion / Corruption、线索、背包、地图、日志、存档/读档和多结局。
- Agentic world mode：八个重要国家出身、开局城市、身份背景、本地宗教合法性、开放自然语言行动、具体场景锚点 `current_scene_focus` 和玩家可读叙事。

### API 与持久化

- FastAPI endpoints：健康检查、职业、神明、地点、角色创建、游戏创建、游戏读取、事件日志、提交行动和删除游戏局。
- SQLite persistence：版本化 `GameState` snapshot、事件日志、结构化 `MemoryRecord`，并默认隔离 secret / system_secret 记忆。

### LLM / Agentic Runtime

- OpenAI-backed Turn Director：可选真实模型调用，一次结构化返回开放行动理解、规则裁定建议、临时场景、NPC、事件、物件和紧凑叙事。
- Validator + State Commit：LLM 只能提出内容，程序负责拒绝越权死亡、奖励、线索、地点变化、秘密泄露和未授权状态修改。
- Local fallback providers：没有 API key、模型失败或输出不合规时可以回退到本地 provider。

### RAG 与长期记忆

- `docs/canon/`：将国家、城市、神明、教会、职业、文风、禁区和事实权限拆成可检索 canon corpus。
- `rag/canon.py`：支持 `keyword`、`embedding`、`hybrid`、`vector`、`vector_hybrid` 检索策略。
- `rag/embeddings.py` / `rag/vector_store.py`：提供本地 deterministic embedding、可选 OpenAI embedding 和 SQLite vector cache。
- Generated Fact / Relationship Memory：临时 NPC、地点、传闻、事件、关系和派系压力只有通过验证后才会写入长期记忆。

## 文档入口

完整文档索引见 [docs/README.md](docs/README.md)。

建议阅读顺序：

1. [docs/phase1_6_architecture_summary.md](docs/phase1_6_architecture_summary.md)：当前架构基线；
2. [docs/agentic_runtime_architecture.md](docs/agentic_runtime_architecture.md)：长期 Agentic Runtime 思路；
3. [docs/phase6_completion_summary.md](docs/phase6_completion_summary.md)：世界知识与长期记忆完成情况；
4. [docs/future_phase_plan.md](docs/future_phase_plan.md)：Phase 7-10 小任务开发路线；
5. [docs/world_bible.md](docs/world_bible.md)：世界观总览。

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
    scenarios.py
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
  agentic_runtime/
    __init__.py
    contracts.py
    event_agent.py
    generated_facts.py
    intent_agent.py
    item_agent.py
    memory_store.py
    memory_summarizer.py
    memory_curator.py
    memory_retriever.py
    narrator_agent.py
    npc_agent.py
    orchestrator.py
    providers.py
    relationship_memory.py
    rule_arbiter_agent.py
    scene_agent.py
    state_commit.py
    validators.py
    world_slice.py
    world_relations.py
  llm_runtime/
    __init__.py
    adjudication.py
    actions.py
    contracts.py
    narrator.py
    proposals.py
    providers.py
    prompts.py
  rag/
    __init__.py
    canon.py
    embeddings.py
    vector_store.py
  prompts/
    action_candidate.md
    event_agent.md
    item_agent.md
    narrator.md
    npc_agent.md
    open_generation.md
    open_action.md
    scene_event.md
  tests/
    test_agentic_runtime.py
    test_llm_runtime_adjudication.py
    test_llm_runtime_actions.py
    test_llm_runtime_narrator.py
    test_llm_runtime_proposals.py
    test_llm_runtime_providers.py
    test_llm_runtime_prompts.py
    test_phase2_api.py
    test_sqlite_repository.py
    test_game_service.py
    test_intent_parser.py
    test_save_manager.py
    test_story_views.py
  docs/
    canon/
      README.md
      cities.md
      classes_identities.md
      countries.md
      fact_authority.md
      gods_churches.md
      policy_forbidden_outputs.md
      tone.md
      world_geography.md
    README.md
    inspiration_notes.md
    tone_guide.md
    forbidden_outputs.md
    rag_seed_cards.md
    progression_design.md
    agentic_runtime_architecture.md
    phase5_agentic_runtime_plan.md
    phase5_completion_summary.md
    phase6_world_memory_plan.md
    phase6_completion_summary.md
    phase1_6_architecture_summary.md
    future_phase_plan.md
    phase2_api_plan.md
    phase4_llm_runtime_plan.md
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

完整索引见 [docs/README.md](docs/README.md)。

核心文档：

- [AGENTS.md](AGENTS.md)：长期工程规则和架构边界；
- [docs/phase1_6_architecture_summary.md](docs/phase1_6_architecture_summary.md)：当前架构基线；
- [docs/agentic_runtime_architecture.md](docs/agentic_runtime_architecture.md)：长期 Agentic Runtime 设计；
- [docs/future_phase_plan.md](docs/future_phase_plan.md)：Phase 7-10 小任务路线；
- [docs/world_bible.md](docs/world_bible.md)：世界观总览；
- [docs/canon/](docs/canon/README.md)：可检索 canon corpus。

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

默认 CLI 不会调用真实 LLM，可以离线、本地、零成本运行。

启用真实 LLM 推荐使用本地 `.env`，不要把 API key 写进命令，也不要把 key 发到聊天里：

```bash
cp .env.example .env
```

然后打开 `.env`，填入：

```text
OPENAI_API_KEY=你的真实_key
PANTHEON_USE_LLM=1
PANTHEON_OPENAI_MODEL=gpt-4o-mini
PANTHEON_CANON_RETRIEVAL=keyword
PANTHEON_EMBEDDING_PROVIDER=local
```

程序会自动读取项目根目录的 `.env`。`.env` 已被 `.gitignore` 忽略，不会上传 GitHub。

`PANTHEON_CANON_RETRIEVAL` 可选值为 `keyword`、`embedding`、`hybrid`、`vector`、`vector_hybrid`。默认推荐 `keyword`；`vector` 和 `vector_hybrid` 会把 canon chunk embedding 缓存进 SQLite。

`PANTHEON_EMBEDDING_PROVIDER` 默认是 `local`，不会调用网络。设置为 `openai` 时，会使用 `PANTHEON_OPENAI_EMBEDDING_MODEL` 调用 OpenAI Embeddings API，并把结果缓存到 `PANTHEON_VECTOR_DB_PATH` 指定的 SQLite 文件中。

只查看 runtime 调试摘要，不调用真实 LLM：

```bash
PANTHEON_SHOW_RUNTIME=1 ./.venv/bin/python -m phase1_cli.main
```

确认真实 LLM 是否接入成功：

```bash
./.venv/bin/python -m llm_runtime.smoke_test
```

如果输出里看到：

```text
Result: OpenAI action provider returned a candidate.
```

说明这次确实调用到了模型。如果看到 fallback、missing key、model not found、timeout 等错误，就说明没有成功接入。

运行真实 LLM 自动测试：

```bash
./.venv/bin/python -m unittest tests.test_live_openai_provider
```

这条测试会真实调用一次模型，验证类似“跳向前厅”的自然表达是否被模型归一为合法 `move` action。它只有在 `.env` 中设置 `PANTHEON_RUN_LIVE_LLM_TESTS=1` 时才会运行，默认测试套件不会消耗 API token。

CLI 交互输入会优先使用 `prompt_toolkit`，它比原生 `input()` 更适合中文输入、删除和光标移动。如果你的终端环境和 `prompt_toolkit` 不兼容，可以强制退回原生输入：

```bash
PANTHEON_SIMPLE_INPUT=1 ./.venv/bin/python -m phase1_cli.main
```

`PANTHEON_SIMPLE_INPUT=1` 可以直接放在 `.env` 里。world-mode 默认使用普通 `你>` 提示，不再依赖彩色提示来区分输入和输出。

启用 Phase 5 Agentic Runtime：

```text
PANTHEON_USE_AGENTIC_RUNTIME=1
```

启用 Phase 5 world-mode：

```text
PANTHEON_GAME_MODE=world
```

world-mode 会在创建角色时要求选择出身国家和开局城市，并自动使用 Phase 5 Agentic Runtime。奥斯特帝国出身会额外选择民族。默认 `tutorial` 模式仍然是雾中修道院教程场景。需要查看 Agent 内部结构时，再额外设置 `PANTHEON_SHOW_RUNTIME=1`。

当前 world-mode 开放八个重要国家：

```text
阿尔比昂联合王国：格兰威克、布莱摩尔、圣维兰
卢米埃共和国：卢塞恩、圣雷米尔、维拉尔
瓦尔德铁血邦联：格莱芬、科伦海姆、霍恩维克
奥斯特帝国：维伦纳、卡洛维茨、佩斯塔
伊斯特亚王冠领：阿尔卡萨、贝拉诺、米拉诺
诺克提亚：诺克提亚城
塞勒米亚苏丹国：萨莱姆
罗斯维亚大公国：维亚洛夫
```

每个出身国家还会带入初始本地宗教合法性上下文，例如国教/主导教会、合法公开教会、受限/异端风险教会和敌对异教/邪教。合法公开不等于政治友好，有些教会只是因为条约、港口贸易、侨民保护或列强压力而被允许存在。五大列强通常把深渊信仰视为敌对异教；塞勒米亚则把密仪会作为国教，同时因为列强实力和金门海峡贸易压力，允许其他七神教会在境内合法存在。这个信息会进入公开状态和 Agentic Runtime memory context，方便后续 Agent 判断公开祈祷、传教、调查教会和接触异端时的社会风险。宗教合法性是初始值，后续可以被世界事件和验证后的 memory/state commit 改变。

国家关系不会写死成固定表。世界观只固定国家的政体、地理、城市、官方信仰、经济利益和地缘压力；两国当前亲疏、外交危机、联盟、制裁、战争风险等关系状态，后续由 Agent 根据事件提出 `relation signal`，再由程序验证后写入长期世界记忆。当前代码已提供 `agentic_runtime/world_relations.py` 作为动态国家关系接口。

如果还想让 Phase 5 的 Agentic Runtime 调用 OpenAI，而不是使用完全本地 deterministic providers：

```text
PANTHEON_USE_AGENTIC_LLM=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
OPENAI_API_KEY=你的真实_key
```

当前 Phase 5 默认 live 路径使用 OpenAI Turn Director。这样每回合通常只需要一次模型调用：Turn Director 一次返回玩家开放行动理解、规则裁定建议、临时场景、NPC、事件、物件，以及紧凑玩家叙事。程序随后负责验证裁定范围、掷骰、提交状态、拒绝越权结果，并在高风险场景补充或回退安全叙事。Memory / State Commit 默认仍使用本地 provider，以便守住现实写入、记忆边界和最终提交。

如果要调试旧版多 Agent 分离链路，可以关闭导演快速路径：

```text
PANTHEON_AGENTIC_TURN_DIRECTOR=0
```

关闭后会回到 OpenAI Intent Agent + OpenAI Rule Arbiter Agent + OpenAI WorldBundle Agent，速度会比默认路径慢，但方便单独观察各个 Agent。

如果想让 NPC / Event / Item / Narrator Agents 分别调用 OpenAI，可以额外开启 full 模式：

```text
PANTHEON_AGENTIC_FULL_LLM=1
```

full 模式更适合拆分调试各个 Agent，但每回合调用次数更多，速度会明显变慢。普通试玩优先使用默认 Turn Director 路径。

试玩时建议给 Turn Director 留出足够结构化输出空间，避免 JSON 被截断后回退：

```text
PANTHEON_OPENAI_MAX_OUTPUT_TOKENS=1400
```

然后运行：

```bash
./.venv/bin/python -m phase1_cli.main
```

默认情况下，Phase 5 路径仍使用本地 deterministic agents，不会额外消耗 LLM token。开启 `PANTHEON_USE_AGENTIC_LLM=1` 且提供 `OPENAI_API_KEY` 后，默认由 Turn Director 调用 OpenAI；任一模型调用失败或裁定不合规时会自动回退到旧链路或本地 provider。Phase 5 默认快速链路是：

```text
Memory Retriever -> Turn Director Agent
-> Validators -> State Commit Layer -> Memory Curator Agent
-> Narration Branch Selection -> CLI 输出
```

如果使用旧的 Phase 4 LLM 路径，也就是只设置 `PANTHEON_USE_LLM=1` 而不启用 Phase 5，玩家输入会先进入 `OpenAIActionCandidateProvider`，生成结构化 `ActionCandidate`，通过本地 validator 后再交给 `rule_engine.py`。规则结果出来后，`OpenAINarrationProvider` 会生成结构化 `NarrationProposal`，再次通过本地 validator 后才展示给玩家。没有 API key、调用失败或输出不合规时，系统会自动回退到本地关键词解析和模板叙事。

注意：这是 Phase 4 的过渡式接入，用来证明“真实 LLM provider + structured output + 本地 validator + fallback”可以跑通。它不是最终玩法架构。Phase 5 不会继续靠给 `ActionCandidate` 增加关键词或枚举来解决自然语言理解问题，而会改成更开放的 Agentic Runtime。

在当前 Phase 4 里，真实模型输出仍使用 structured output schema 约束。类似“跳向前厅”的动作，模型应保留玩家动作方式，同时归一为当前旧规则系统能接受的行动候选：

```json
{
  "intent": "move",
  "target": "前厅",
  "method": "跳向前厅"
}
```

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
./.venv/bin/python -m py_compile llm_runtime/*.py
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
- `llm_runtime/contracts.py`：LLM 输出的结构化 proposal/result 契约。
- `llm_runtime/narrator.py`：叙事提案验证与安全回退。
- `llm_runtime/providers.py`：行动候选 provider、叙事 provider、本地 fallback provider 和可选 OpenAI provider。
- `llm_runtime/prompts.py`：加载 prompt/policy 文件。
- `prompts/narrator.md`：Narrator 的输入、输出 schema 和禁止行为。

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

当前 CLI 显示名已经与世界观文档统一为 `骑士 / 密探`，内部 `class_id` 仍保留 `warrior / rogue` 以兼容旧存档和旧接口。

职业通过三类配置影响规则：

- `stat_bonus`：改变初始力量、敏捷、智力、信仰。
- `hp_bonus` / `san_bonus`：改变初始 HP 和 SAN。
- `rule_modifiers`：给特定行动加成或惩罚。

当前 CLI 例子：

- 骑士攻击和护卫更强：`attack_bonus +2`。
- 法师分析神秘知识更强：`analyze_bonus +2`、`lore_bonus +2`，但接触禁忌知识 SAN 风险更高。
- 密探潜行、开锁和伪装更强，但隐秘路线会增加 Suspicion。
- 游侠追踪和侦察更强。
- 牧师祈祷、净化、抵抗污染更强。
- 炼金术士使用药剂、鉴定异常物质更强。

## 当前限制

- 意图识别是关键词规则，不是真正的自然语言理解。
- 默认剧情文本可以本地模板运行；设置 `PANTHEON_USE_LLM=1` 且提供 `OPENAI_API_KEY` 后，可启用真实 LLM 行动候选和叙事 provider。
- CLI 当前只有单一默认本地存档，还没有多存档位或账号系统。
- API 当前使用 SQLite 保存游戏会话，还没有 PostgreSQL、账号系统或多用户隔离。
- API 当前不处理本地 JSON 存档/读档，CLI 仍保留本地存档功能。
- 默认 tutorial 模式仍是「雾中修道院」小副本；`PANTHEON_GAME_MODE=world` 已可选择八个重要国家出身与开局城市，并支持奥斯特民族选择、本地宗教合法性上下文、可见长期记忆和故事化 CLI 输出。
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

## Phase 4：Open Generation Proposal Runtime

当前 Phase 4 已经开始建立 LLM 运行时的第一层边界：

- `llm_runtime/actions.py`：验证 LLM 或本地 provider 提出的行动候选；
- `llm_runtime/adjudication.py`：把语义行动候选转成通用裁定请求；
- `llm_runtime/contracts.py`：定义叙事提案、验证结果和最终叙事结果；
- `llm_runtime/proposals.py`：验证 LLM 提出的场景和事件 proposal；
- `llm_runtime/narrator.py`：验证 LLM 叙事提案是否越权；
- `llm_runtime/providers.py`：定义 provider 接口，让未来真实模型接入不需要改规则引擎；
- `llm_runtime/prompts.py`：集中加载 prompt/policy 文件；
- `prompts/action_candidate.md`：记录 Action Candidate Agent 的输出 schema、支持 intent 和禁止行为；
- `prompts/open_generation.md`：记录开放生成内容的输出 schema、内容类型和禁止行为；
- `prompts/scene_event.md`：记录 Scene/Event proposal 的输出 schema、权限等级和禁止行为；
- `prompts/narrator.md`：记录 Narrator 的输出 schema、允许行为和禁止行为；
- `resolve_action_candidate()`：验证通过则使用候选行动，验证失败则回退到当前关键词 parser；
- `adjudicate_candidate()`：把候选行动整理成 check type、primary stat、difficulty、risk tags 和 possible costs；
- `render_safe_narration()`：验证通过则使用提案，验证失败则回退到原始规则文本；
- `docs/phase4_llm_runtime_plan.md`：记录 Phase 4 的详细拆分顺序。

当前还没有真实 LLM API 调用。这个阶段只做契约、provider 抽象、prompt 文件化、行动候选验证、开放生成 proposal 验证、场景/事件 proposal 验证、通用裁定请求和安全回退。

开放生成原则：

```text
不要把所有具体地点、道具、NPC、关系、团队、组织、路线、传闻和事件都写死。
LLM 负责自由提出具体内容。
程序负责验证权限、统一逻辑、长期记忆、机械结果和持久化边界。
```

行动候选现在会保留语义信息：

```text
method：玩家具体怎么做。
desired_outcome：玩家想达成什么。
risk_tags：可能风险，但不是已发生后果。
skill_tags：可能相关能力，但不是自动加成。
assumptions：玩家猜测，不是世界事实。
```

场景/事件提案必须遵守：

```text
可以生成 flavor / temporary 内容。
不能提交 persistent 世界事实。
不能 claim mechanical 结果。
不能揭露 secret 隐藏真相。
```

叙事提案必须遵守：

```text
只能 claim rule_result 已经授权的状态变化、线索和地点。
不能通过自然语言绕过 rule_engine。
不能直接修改 GameState。
```

这一步的意义是：接入真实 LLM 后，LLM 仍然不是直接输出最终现实，而是先输出结构化 proposal，再被系统验证。

## 这个阶段学到什么

通过 `v4.7.0`，你会接触到：

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
- LLM proposal 契约；
- provider interface；
- prompt/policy 文件管理；
- LLM 输出验证；
- 安全回退机制；
- OpenAI provider 接入；
- 环境变量控制真实 LLM 调用；
- fake client 测试真实 provider 路径；
- API 自动化测试；
- 关键词意图识别；
- d20 随机检定；
- 配置化职业系统；
- 规则引擎与剧情文本解耦；
- 为 FastAPI、数据库和 LLM Agent Workflow 预留接口。

## 长期 LLM Agent 方向

项目未来不是让 LLM 直接扮演全能游戏主持人，也不是让 LLM 只润色固定规则文本，而是让 LLM 在规则系统稳定器的帮助下生成开放内容。

规则引擎的职责不是穷举所有故事，而是补足 LLM 的缺点：

- 防止上下文漂移；
- 提供统一裁判标准；
- 控制长期节奏和核心秘密释放；
- 决定机械结果和状态变化权限；
- 判断哪些生成内容可以持久化。

目标流程：

```text
玩家输入
  ↓
Memory Retriever 检索当前地点、NPC、任务和玩家已知信息
  ↓
Intent Agent 保留开放行动意图、方法、目标、语气和玩家猜测
  ↓
Scene / NPC / Event / Item Agents 生成临时场景、人物、事件和道具候选
  ↓
Rule Arbiter Agent 提出裁定、检定、代价、风险和允许结果
  ↓
validators 检查世界观、隐藏信息、奖励权限和状态权限
  ↓
State Commit Layer 写入真正发生的结构化状态
  ↓
Memory Curator Agent 判断哪些信息需要保存、丢弃、压缩或隐藏
  ↓
Narrator Agent 生成最终叙事
  ↓
validator 再次校验最终文本 claims
  ↓
输出给玩家
```

关键边界：

- 玩家输入不是事实；
- LLM 输出不是事实；
- RAG 提供背景，不提供权限；
- 状态变化必须结构化；
- 规则限制的是“改变现实的权限”，不是限制 LLM 的想象力；
- 世界观核心事实由 `world_bible.md` 维护；
- LLM 运行规则由 `llm_runtime_design.md` 维护；
- 长期 Agentic Runtime 架构由 `agentic_runtime_architecture.md` 维护。
