# 神座纪元 / Pantheon Age

**神座纪元（Pantheon Age）** 是一个受规则稳定约束的 LLM Agent 文字冒险项目。

项目以固定神明体系、维多利亚神秘学、调查冒险和规则裁定为核心。它的目标不是让 LLM 给固定剧情润色，而是让 LLM 生成行动、场景、NPC、事件和叙事可能性，再由程序负责验证、记忆和提交世界现实。

当前版本：

```text
v10.7.0 / Phase 10.7 Final Demo Pass
```

当前主线：

```text
Agentic Runtime + Canon Retrieval + Persistent Memory + Progression Mechanics + FastAPI + Web Playtest Baseline + Observability + Safety/Quality Evals + Runtime Profiles + Provider Strategy + Dev Setup + Final Demo
```

当前状态：

```text
Phase 10 Complete / Final Demo Ready
```

后续方向：

```text
Post-10: Playtest polish, content expansion, deployment, and portfolio packaging
```

## 项目动机

这个项目的灵感来自《诡秘之主》和《诸神愚戏》。我喜欢其中神秘学、神明体系、异常事件、调查冒险和世界观层层展开的感觉，但这类题材并不算多。

LLM 的出现让我看到一种新的可能：不只是阅读故事，而是构建一个由 AI 生成内容、由规则约束现实、由玩家自由探索的个人故事世界。

核心原则：

```text
LLM 负责创造可能性。
规则限制的是改变现实的权限，而不是想象力。
程序负责验证、记忆、持久化和审计。
只有通过验证并提交的结构化内容，才算世界现实。
```

## 这个项目展示什么

这是一个 AI Agent 工程作品，而不只是一个文字冒险 demo。它重点展示：

- 高自由度 LLM 叙事：模型负责理解开放行动、生成场景、NPC、事件和主持人文本；
- 程序化权限边界：Python 负责验证、掷骰、状态提交、资源限制、记忆写入和安全回退；
- RAG / context packing：只把相关世界设定、角色状态、记忆和规则上下文喂给模型；
- 长期记忆：只保存经过提交的事实和玩家可见记忆，不把原始 LLM 输出直接当世界真相；
- 多层 eval：安全评测、叙事质量评测、试玩 fixture 和 final demo smoke 防止回归；
- API + Web：FastAPI 提供游戏接口，React/Vite 提供浏览器试玩界面。

推荐展示路线见：

- [docs/final_demo.md](docs/final_demo.md)

## 当前能力

### 游戏闭环

- CLI 教程模式：固定场景、角色创建、职业与神明选择、d20 检定、状态变化、线索、背包、地图、日志、存档和多结局。
- 世界模式：支持八个重要国家出身、开局城市、身份背景、本地宗教合法性、结构化开场导入、开放自然语言行动和玩家可读叙事。
- 场景连续性：`current_location` 表示城市级位置，`current_scene_focus` 表示具体场景，避免非移动行动导致地点漂移。

### Agentic Runtime

- `agentic_runtime/` 是当前主要运行时。
- LLM / Agent 可以提出开放行动理解、规则裁定建议、临时场景、NPC、事件、物件和叙事。
- Validator 和 State Commit 层负责阻止越权死亡、奖励、线索、地点变化、秘密泄露和未授权状态修改。
- 没有 API key、模型失败或输出不合规时，可以回退到本地 provider。
- `agentic_runtime/safety_evals.py` 提供本地离线安全评测，检查白拿奖励、越权击杀、秘密泄露、瞬移、乱造核心神明和资源越权等回归。
- `agentic_runtime/narrative_quality_evals.py` 提供本地离线叙事质量评测，检查主持人口吻、具体感、行动钩子、后台词泄露和节奏长度。
- `PANTHEON_PLAY_PROFILE` 支持 `local`、`fast`、`quality`、`debug` 四档运行配置；`agentic_runtime.smoke_test` 会输出耗时、慢步骤和性能建议。

### RAG 与长期记忆

- `docs/canon/` 保存可检索世界设定。
- `rag/canon.py` 支持关键词检索、向量检索、混合检索和 SQLite 向量缓存检索。
- `phase3_persistence/` 使用 SQLite 保存游戏会话、事件日志和结构化长期记忆。
- 临时 NPC、地点、传闻、事件、关系和派系压力只有通过验证后才会写入长期记忆。

### 成长与核心机制

- 角色拥有六属性、职业等级、信仰等级、神秘阶位、Favor、Revelation 和 Devotion。
- 职业技能、信仰天赋、主动祷告和道具会参与 world-mode 检定修正。
- 晋升需要满足条件并消耗资源；LLM 叙事不能直接授予等级、属性或道具。
- `状态` 会显示当前技能、天赋、祷告、可用道具和晋升缺口。

### API 与持久化

- `phase2_api/` 提供 FastAPI 接口。
- `phase3_persistence/` 提供 SQLite 持久化。
- API 已支持创建角色、创建游戏、读取游戏、提交行动、读取事件日志和删除游戏。

## 项目结构

```text
phase1_cli/            CLI、教程模式、核心状态模型和服务层
phase2_api/            FastAPI 路由、请求/响应 schema 和会话服务
phase3_persistence/    SQLite 游戏会话、事件和长期记忆持久化
agentic_runtime/       当前主线 Agentic Runtime
llm_runtime/           Phase 4 结构化 LLM 兼容层
rag/                   canon 检索、embedding provider 和向量缓存
web_ui/                React + TypeScript + Vite 网页客户端骨架
docs/                  世界观、架构、阶段计划和运行文档
docs/canon/            可检索世界设定语料
prompts/               LLM / Agent prompt 文件
tests/                 自动化测试
```

## 快速运行

进入项目根目录：

```bash
cd pantheon-age
```

创建虚拟环境并安装依赖：

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

启动 CLI：

```bash
./.venv/bin/python -m phase1_cli.main
```

默认模式不会调用真实 LLM，可以离线、本地、零成本运行。

也可以使用开发辅助入口：

```bash
./.venv/bin/python scripts/dev.py doctor
./.venv/bin/python scripts/dev.py check
./.venv/bin/python scripts/dev.py cli
```

## 启用世界模式

在 `.env` 中设置：

```text
PANTHEON_GAME_MODE=world
PANTHEON_USE_AGENTIC_RUNTIME=1
```

启动后会选择出身国家、开局城市、职业、信仰和身份背景。

当前开放的出身国家：

```text
阿尔比昂联合王国
卢米埃共和国
瓦尔德铁血邦联
奥斯特帝国
伊斯特亚王冠领
诺克提亚
塞勒米亚苏丹国
罗斯维亚大公国
```

## 启用真实 LLM

复制环境变量模板：

```bash
cp .env.example .env
```

在 `.env` 中填写：

```text
OPENAI_API_KEY=你的真实_key
PANTHEON_USE_AGENTIC_LLM=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
PANTHEON_OPENAI_MODEL=gpt-4o-mini
```

`.env` 已被 `.gitignore` 忽略，不会上传 GitHub。

如果要切到本地 OpenAI-compatible 模型，不需要改代码，只改 `.env`：

```text
OPENAI_API_KEY=local
PANTHEON_OPENAI_PROVIDER=ollama
PANTHEON_OPENAI_BASE_URL=http://localhost:11434/v1
PANTHEON_OPENAI_MODEL=你的本地模型名
```

也可以把 provider 改成 `lm_studio`、`vllm` 或其他自定义名称。无论走官方 OpenAI 还是本地兼容端点，游戏都会继续使用同一套 validator、掷骰、状态提交和记忆规则。

常用设置：

```text
PANTHEON_SHOW_RUNTIME=1          # 显示运行时调试摘要
PANTHEON_AGENTIC_FULL_LLM=1      # 启用较慢的多 Agent 分离调用
PANTHEON_SIMPLE_INPUT=1          # 终端中文输入异常时，退回原生 input()
```

向量检索默认使用本地实现，不会调用网络：

```text
PANTHEON_EMBEDDING_PROVIDER=local
PANTHEON_CANON_RETRIEVAL=keyword
```

如需调用真实 OpenAI 向量接口：

```text
PANTHEON_EMBEDDING_PROVIDER=openai
PANTHEON_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
PANTHEON_CANON_RETRIEVAL=vector_hybrid
```

## 启动 API

```bash
./.venv/bin/uvicorn phase2_api.main:app
```

或：

```bash
./.venv/bin/python scripts/dev.py api
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

主要接口：

```text
GET    /health
GET    /classes
GET    /gods
GET    /locations
GET    /origins
POST   /characters
POST   /games
GET    /games
GET    /games/{game_id}
GET    /games/{game_id}/events
DELETE /games/{game_id}
POST   /games/{game_id}/actions
```

创建世界模式游戏示例：

```json
{
  "name": "伊芙",
  "class_id": "rogue",
  "god": "隐秘之神",
  "game_mode": "world",
  "origin_country_id": "lumiere",
  "origin_city": "卢塞恩",
  "background_id": "investigative_reporter"
}
```

提交行动示例：

```json
{
  "text": "去码头账房查昨晚的船只记录",
  "include_debug": false
}
```

`POST /games/{game_id}/actions` 会同时返回：

```text
story       玩家可见叙事
state       公开状态
mechanics   掷骰、提交效果和规则结果摘要
debug       可选调试信息，默认不返回
response    兼容旧客户端的完整响应
```

默认数据库：

```text
data/pantheon_age.sqlite3
```

可通过环境变量修改：

```text
PANTHEON_DB_PATH=data/dev.sqlite3
```

## 启动网页客户端

先启动 API：

```bash
./.venv/bin/uvicorn phase2_api.main:app
```

再启动网页客户端：

```bash
cd web_ui
npm install
npm run dev
```

或使用开发辅助入口：

```bash
./.venv/bin/python scripts/dev.py web-install
./.venv/bin/python scripts/dev.py web-dev
```

浏览器打开：

```text
http://127.0.0.1:5173
```

默认 API 地址：

```text
http://127.0.0.1:8000
```

如需改 API 地址，在 `web_ui/.env.local` 中设置：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

当前网页客户端已经支持 Phase 9.6 试玩基线：选择名字、出身国家、开局城市、民族、职业、信仰和身份背景，创建 world-mode 游戏，在浏览器里输入行动，使用开场行动建议，并查看角色状态、位置、属性、成长、背包和线索。

后端 API 启动后，可以从 `web_ui/` 运行快速 smoke 检查：

```bash
npm run smoke:api
```

## 运行测试

普通测试不会调用真实 LLM 或真实向量接口：

```bash
./.venv/bin/python -m py_compile phase1_cli/*.py phase2_api/*.py phase2_api/routes/*.py phase2_api/services/*.py phase3_persistence/*.py agentic_runtime/*.py llm_runtime/*.py rag/*.py scripts/*.py tests/*.py
env PANTHEON_USE_AGENTIC_LLM=0 PANTHEON_USE_LLM=0 PANTHEON_EMBEDDING_PROVIDER=local PANTHEON_CANON_RETRIEVAL=keyword ./.venv/bin/python -m unittest discover -s tests
```

等价的本地检查入口：

```bash
./.venv/bin/python scripts/dev.py check
```

真实 LLM 测试需要显式开启：

```text
PANTHEON_RUN_LIVE_LLM_TESTS=1
PANTHEON_USE_AGENTIC_LLM=1
```

旧 Phase 4 provider live test：

```bash
./.venv/bin/python -m unittest tests.test_live_openai_provider
```

当前 Agentic Runtime live test：

```bash
./.venv/bin/python -m unittest tests.test_live_agentic_runtime
```

手动检查 Agentic Runtime 分支与耗时：

```bash
./.venv/bin/python -m agentic_runtime.smoke_test
```

按 profile 检查：

```bash
env PANTHEON_PLAY_PROFILE=local ./.venv/bin/python -m agentic_runtime.smoke_test
env PANTHEON_PLAY_PROFILE=fast ./.venv/bin/python -m agentic_runtime.smoke_test
env PANTHEON_PLAY_PROFILE=quality ./.venv/bin/python -m agentic_runtime.smoke_test
env PANTHEON_PLAY_PROFILE=debug ./.venv/bin/python -m agentic_runtime.smoke_test
```

本地安全评测：

```bash
./.venv/bin/python -m unittest tests.test_safety_evals
```

本地叙事质量评测：

```bash
./.venv/bin/python -m unittest tests.test_narrative_quality_evals
```

手动试玩清单：

- [docs/playtest_checklist.md](docs/playtest_checklist.md)

最终展示路线：

```bash
./.venv/bin/python scripts/dev.py final-demo
```

- [docs/final_demo.md](docs/final_demo.md)

## 文档

完整文档入口：

- [docs/README.md](docs/README.md)
- [docs/github_release_checklist.md](docs/github_release_checklist.md)

建议阅读顺序：

1. [docs/project_architecture.md](docs/project_architecture.md)：当前项目结构、运行主链路和模块职责；
2. [docs/final_demo.md](docs/final_demo.md)：最终展示路线；
3. [docs/agentic_runtime_architecture.md](docs/agentic_runtime_architecture.md)：长期 Agentic Runtime 设计；
4. [docs/playtest_checklist.md](docs/playtest_checklist.md)：世界模式试玩清单；
5. [docs/dev_setup.md](docs/dev_setup.md)：本地开发、运行、测试和环境文件说明；
6. [docs/world_bible.md](docs/world_bible.md)：世界观总览；
7. [docs/progression_design.md](docs/progression_design.md)：成长系统、属性、仪式晋升和道具设计；
8. [docs/phase1_9_architecture_summary.md](docs/phase1_9_architecture_summary.md)：历史架构基线；
9. [docs/final_phase10_plan.md](docs/final_phase10_plan.md)：最终 Phase 10 开发记录；
10. [docs/future_phase_plan.md](docs/future_phase_plan.md)：Post-10 路线。

## 上传 GitHub 前检查

本仓库默认不会上传 `.env`、`.venv/`、SQLite 数据库、存档、前端构建产物和 `.local_notes/` 私人笔记。

推荐在提交前运行：

```bash
./.venv/bin/python scripts/dev.py check
cd web_ui
npm run build
```

需要快速检查忽略规则时：

```bash
git check-ignore -v .env .local_notes/project_interview_guide.md data/pantheon_age.sqlite3 web_ui/dist/index.html
```

## 当前限制

- 世界模式已经可试玩；地点连续性、风险反馈、基本安全边界和 Phase 8 核心机制已有回归测试，长期玩法仍需要继续打磨。
- Phase 8 已完成技能、天赋、祷告、六属性检定、仪式晋升和道具机制的基础基线，完整成长体验仍会继续扩展。
- 网页界面已经具备 React/Vite 试玩客户端、角色创建流程、聊天式行动提交、行动建议、只读状态面板、API smoke 检查和推荐 demo 角色入口。
- 真实 LLM 与真实向量接口调用需要用户自行配置 API key，并可能产生 API 成本；本地 OpenAI-compatible 模型可降低成本，但结构化 JSON 稳定性和叙事质量取决于本地模型能力。
- Docker Compose 暂时延后；当前推荐用 `.venv`、`scripts/dev.py`、FastAPI 和 Vite 直接开发。最终 demo 路线已经固定在 [docs/final_demo.md](docs/final_demo.md)。

## 后续阶段

```text
Phase 10: 完成最终 demo 路线
Post-10: 持续试玩、内容扩展、部署与作品包装
```
