# 神座纪元 / Pantheon Age

**神座纪元（Pantheon Age）** 是一个以固定神明体系、维多利亚神秘学、调查冒险和规则裁定为核心的文字冒险系统。当前版本是 `v5.8.0 Phase 5 Final Integration`，已经把 Phase 1 CLI 核心能力暴露成 REST API，把 API 游戏会话持久化到 SQLite，并建立受规则约束的 LLM 运行时契约、provider 接口、prompt/policy 文件、语义行动候选、开放生成 proposal、场景/事件提案验证、通用裁定请求、可选 OpenAI provider，以及 Phase 5 的 Agentic Runtime baseline。

Phase 4 的目标已经完成：CLI 可以启用真实 LLM，也能在没有 API key、模型失败或输出越权时安全回退。Phase 5 的 Agentic Runtime baseline 也已经完成：项目不再继续给旧的 `ActionCandidate(intent=...)` 工作流打补丁，而是引入 `agentic_runtime/`，让 Agent 负责理解、生成、裁定建议、记忆整理和叙事组织，程序负责验证、提交状态、持久化和审计。

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

## 版本状态

```text
内部里程碑：Phase 5 Agentic Runtime Baseline
对外起点版本：v1.0.0
当前公开版本：v5.8.0
Phase 5 状态：Agentic Runtime baseline 完成。world-mode 支持八个重要国家出身、开局城市、奥斯特民族选择、常用身份选择、本地宗教合法性上下文、动态国家关系接口、OpenAI Turn Director 默认快速路径、旧版 Intent/RuleArbiter/WorldBundle 多调用路径可选回退、OpenAI NPC/Event/Item/Narrator Agents full 模式可选启用、跨回合 Agentic Memory Store 检索、故事化 CLI 输出，以及完整 Phase 5 收口文档和服务层集成测试
```

当前已完成：

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
- `llm_runtime/` LLM 运行时契约；
- `NarrationProposal` / `NarrationValidation` / `NarrationResult`；
- `NarrationProvider` provider 接口；
- `TemplateNarrationProvider` 本地模板 provider；
- `OpenAIActionCandidateProvider` 真实 OpenAI 行动候选 provider；
- `OpenAINarrationProvider` 真实 OpenAI 叙事 provider；
- `PANTHEON_USE_LLM=1`：启用真实 LLM；
- `PANTHEON_OPENAI_MODEL`：覆盖默认模型；
- `PANTHEON_SHOW_RUNTIME=1`：在 CLI 显示 Phase 4 / Phase 5 runtime 调试摘要；
- `prompts/narrator.md` 叙事 prompt 与禁止行为文件；
- `ActionCandidate` / `ActionCandidateValidation` / `ActionCandidateResult`；
- `ActionCandidate` 语义字段：`method`、`desired_outcome`、`risk_tags`、`skill_tags`、`assumptions`；
- `llm_runtime/actions.py`：验证行动候选并在无效时回退到关键词 parser，同时保留语义字段；
- `llm_runtime/adjudication.py`：把语义行动候选转成通用裁定请求；
- `AdjudicationRequest` / `AdjudicationValidation` / `AdjudicationResult`；
- `ActionCandidateProvider` / `KeywordActionCandidateProvider` / `OpenAIActionCandidateProvider`；
- `prompts/action_candidate.md` 行动候选 prompt 与禁止行为文件；
- `SceneProposal` / `EventProposal` / `ProposalValidation`；
- `GeneratedContentProposal`：承接 LLM 自由生成的地点、NPC、道具、关系、团队、组织、事件、传闻、路线等内容；
- `llm_runtime/proposals.py`：验证场景/事件提案，阻止越权写入永久事实、机械结果和隐藏真相；
- `prompts/open_generation.md` 开放生成 prompt 与权限边界说明；
- `prompts/scene_event.md` 场景/事件提案 prompt 与权限等级说明；
- `llm_runtime/prompts.py` prompt 加载器；
- 叙事提案验证：只能 claim 已由 `rule_result` 授权的状态变化、线索和地点；
- 安全回退：非法 LLM 提案自动回退到确定性规则文本；
- 安全回退：没有 API key 或 LLM 调用失败时自动回退到关键词 parser 和模板 narrator；
- Phase 4 LLM Runtime 计划文档；
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
- `agentic_runtime/` Phase 5 最小运行时；
- `OpenActionProposal`：保留玩家开放行动、方法、目标、猜测和请求效果；
- `RuleAdjudicationProposal`：由 Rule Arbiter Agent 提出裁定建议、允许效果、拒绝效果和桥接行动；
- `StateCommitProposal`：由 State Commit Layer 统一写入 `GameState`；
- `MemoryCandidate`：由 Memory Curator Agent 提出哪些信息应保存、丢弃或保持临时；
- `MemoryRetrievalResult`：为行动前上下文检索预留结构；
- `TemporaryContentProposal`：让 Scene Agent 生成临时场景细节但不能写入世界事实；
- `NarrationProposal`：由 Narrator Agent 基于已确认结果生成最终文本；
- `PANTHEON_USE_AGENTIC_RUNTIME=1`：启用 Phase 5 CLI 路径；
- `PANTHEON_USE_AGENTIC_LLM=1`：启用 Phase 5 OpenAI-backed Agentic Runtime；
- `PANTHEON_AGENTIC_TURN_DIRECTOR=1`：默认快速路径，一次 OpenAI 调用返回 intent、rule adjudication、scene、NPC、event、item 和 narration；
- `PANTHEON_AGENTIC_TURN_DIRECTOR=0`：关闭快速路径，回到旧版 OpenAI Intent + Rule Arbiter + WorldBundle 多调用路径；
- `PANTHEON_AGENTIC_FULL_LLM=1`：改用较慢的 OpenAI NPC/Event/Item/Narrator 分离 agents；
- `OpenAITurnDirectorProvider`：真实 OpenAI 回合导演 provider，把一回合的理解、裁定建议、临时世界内容和叙事草稿合并到一次结构化调用中；
- `OpenAIIntentAgentProvider`：真实 OpenAI Intent Agent provider；
- `OpenAIWorldBundleProvider`：真实 OpenAI 世界总包 provider，一次生成场景、NPC、事件、物件和玩家可见叙事；
- `OpenAINarratorAgentProvider`：真实 OpenAI 主持人叙事 provider，用于 full 模式或 WorldBundle 回退；
- `OpenAINPCAgentProvider` / `OpenAIEventAgentProvider` / `OpenAIItemAgentProvider`：真实 OpenAI 临时世界内容 provider，用于 full 模式实验；
- `prompts/open_action.md`：Phase 5 Open Action prompt，不要求模型输出旧式固定 intent；
- `prompts/npc_agent.md` / `prompts/event_agent.md` / `prompts/item_agent.md`：Phase 5 NPC、事件和物件生成 prompt；
- `MemoryRecord`：经过验证后写入本地 memory store 的长期记忆记录；
- `agentic_runtime/memory_store.py`：按 player / npc / location / quest / secret 分桶保存 validated memory candidates；
- `memory_retriever.py` 会读取 memory store，让 validated memory candidates 进入后续回合上下文；
- secret memory 保留在内部 `hidden_context`，默认不会进入 runtime 序列化、公开状态或叙事文本；
- `world_slice.py`：为 world-mode 本地 agents 提供城市、出身和可见记忆上下文；
- world-mode Narrator 默认输出玩家可读的故事文本；Agent 结构、边界和 provider 信息只在 `PANTHEON_SHOW_RUNTIME=1` 时显示；
- `NPCProposal` / `EventProposal` / `ItemProposal`：临时人物、事件、物品候选；
- `LocalNPCAgentProvider` / `LocalEventAgentProvider` / `LocalItemAgentProvider`：本地临时世界内容生成；
- NPC / Event / Item validators：拒绝临时内容直接 claim 线索、背包变化、状态变化或永久事实；
- `phase1_cli/scenarios.py`：区分 Mist Abbey tutorial 与 Phase 5 world-mode；
- `PANTHEON_GAME_MODE=world`：进入 Agentic World Mode，并在创建角色时选择八个重要国家出身和开局城市；
- 奥斯特帝国出身会额外选择民族：`奥斯特人`、`佩斯塔人`、`波西恩人`；
- 出身信息：公开状态会记录 `origin_country`、`origin_identity`、`origin_ethnicity`、`origin_city`、`background_name` 和本地宗教合法性上下文；
- `world_action`：world-mode 专用提交类型，记录开放行动但不自动改写地点、线索、背包或角色状态；
- Phase 5 runtime debug 输出；
- `跳向前厅` 通过 Phase 5 开放意图和 Rule Arbiter 桥接为移动，不需要给旧 parser 增加“跳向”关键词；
- Phase 5 Agentic Runtime 自动化测试；
- [docs/phase5_completion_summary.md](docs/phase5_completion_summary.md)：Phase 5 最终完成总结。

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
    intent_agent.py
    item_agent.py
    memory_store.py
    memory_curator.py
    memory_retriever.py
    narrator_agent.py
    npc_agent.py
    orchestrator.py
    providers.py
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
    inspiration_notes.md
    tone_guide.md
    forbidden_outputs.md
    rag_seed_cards.md
    progression_design.md
    agentic_runtime_architecture.md
    phase5_agentic_runtime_plan.md
    phase5_completion_summary.md
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

- [AGENTS.md](AGENTS.md)：项目长期开发规则。记录架构边界、测试命令、Git 操作边界和 Phase 2 方向。
- [docs/world_bible.md](docs/world_bible.md)：世界观设定集。记录维多利亚时代背景、五大列强、其他重要国家、核心城市、八大神明、六大职业、身份系统和世界事实分级。
- [docs/inspiration_notes.md](docs/inspiration_notes.md)：创作灵感与原创化边界。记录项目从同类题材中吸收的高层体验，以及不能复刻其他作品的内容。
- [docs/tone_guide.md](docs/tone_guide.md)：文风指南。记录维多利亚神秘学、工业烟尘、调查节奏、NPC 对话和神秘学表达方式。
- [docs/forbidden_outputs.md](docs/forbidden_outputs.md)：LLM 禁止输出规则。记录不能越权生成的世界事实、机械结果、隐藏信息和奖励。
- [docs/rag_seed_cards.md](docs/rag_seed_cards.md)：最小 RAG 设定卡片。把八神、六大职业和国家气质整理成未来 LLM 容易检索的小卡片。
- [docs/progression_design.md](docs/progression_design.md)：成长系统设计。记录职业等级、信仰等级、仪式晋升、道具系统、属性规划和代价系统。
- [docs/agentic_runtime_architecture.md](docs/agentic_runtime_architecture.md)：长期 Agentic Runtime 架构。记录 Intent Agent、Rule Arbiter Agent、Scene/NPC/Event/Item Agents、Memory Curator Agent、State Commit Layer 和 Narrator Agent 的职责边界。
- [docs/phase5_agentic_runtime_plan.md](docs/phase5_agentic_runtime_plan.md)：Phase 5 分阶段计划。记录 v5.0 到 v5.8 的开发顺序、完成情况和非目标。
- [docs/phase5_completion_summary.md](docs/phase5_completion_summary.md)：Phase 5 完成总结。记录最终能力、数据流、边界和后续 Phase 6 方向。
- [docs/future_phase_plan.md](docs/future_phase_plan.md)：Phase 6 之后的合并执行路线。先实现世界知识与长期记忆地基，再做最小可玩体验校准、成长系统、Web/API 体验，最后做工程质量与最终体验优化。
- [docs/llm_runtime_design.md](docs/llm_runtime_design.md)：LLM 运行逻辑设计。记录 `propose -> validate -> commit`、RAG、内容分级、场景提案、事件生成和防止上下文污染的规则。
- [docs/live_llm_testing.md](docs/live_llm_testing.md)：真实 LLM API key、本地 `.env`、smoke test 和 live test 的安全配置方式。
- [docs/phase2_api_plan.md](docs/phase2_api_plan.md)：Phase 2 FastAPI 拆分计划。
- [docs/system_design.md](docs/system_design.md)：系统设计文档。记录 Phase 1、Phase 2、Phase 3、Phase 4 的模块职责、数据流和演进边界。
- [docs/phase4_llm_runtime_plan.md](docs/phase4_llm_runtime_plan.md)：Phase 4 LLM Runtime 拆分计划。
- [docs/refactor_plan.md](docs/refactor_plan.md)：项目方向校准与重构规划。记录“规则限制权限而非想象力”的长期架构。
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
```

程序会自动读取项目根目录的 `.env`。`.env` 已被 `.gitignore` 忽略，不会上传 GitHub。

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
