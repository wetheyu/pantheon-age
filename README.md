# 神座纪元 / Pantheon Age

**神座纪元（Pantheon Age）** 是一个受规则稳定约束的 LLM Agent 文字冒险项目。

项目以固定神明体系、维多利亚神秘学、调查冒险和规则裁定为核心。它的目标不是让 LLM 给固定剧情润色，而是让 LLM 生成行动、场景、NPC、事件和叙事可能性，再由程序负责验证、记忆和提交世界现实。

当前版本：

```text
v8.7.0 / Phase 8 Progression And Core Mechanics Baseline
```

当前主线：

```text
Agentic Runtime + Canon Retrieval + Persistent Memory + Progression Mechanics
```

下一阶段：

```text
Phase 9 Web UI And API Product Experience
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
docs/                  世界观、架构、阶段计划和运行文档
docs/canon/            可检索世界设定语料
prompts/               LLM / Agent prompt 文件
tests/                 自动化测试
```

## 快速运行

进入项目根目录：

```bash
cd <project-root>
```

安装依赖：

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

启动 CLI：

```bash
./.venv/bin/python -m phase1_cli.main
```

默认模式不会调用真实 LLM，可以离线、本地、零成本运行。

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
POST   /characters
POST   /games
GET    /games
GET    /games/{game_id}
GET    /games/{game_id}/events
DELETE /games/{game_id}
POST   /games/{game_id}/actions
```

默认数据库：

```text
data/pantheon_age.sqlite3
```

可通过环境变量修改：

```text
PANTHEON_DB_PATH=data/dev.sqlite3
```

## 运行测试

普通测试不会调用真实 LLM 或真实向量接口：

```bash
./.venv/bin/python -m py_compile phase1_cli/*.py phase2_api/*.py phase2_api/routes/*.py phase2_api/services/*.py phase3_persistence/*.py agentic_runtime/*.py llm_runtime/*.py rag/*.py tests/*.py
env PANTHEON_USE_AGENTIC_LLM=0 PANTHEON_USE_LLM=0 PANTHEON_EMBEDDING_PROVIDER=local PANTHEON_CANON_RETRIEVAL=keyword ./.venv/bin/python -m unittest discover -s tests
```

真实 LLM 测试需要显式开启：

```text
PANTHEON_RUN_LIVE_LLM_TESTS=1
```

手动检查 Agentic Runtime 分支与耗时：

```bash
./.venv/bin/python -m agentic_runtime.smoke_test
```

手动试玩清单：

- [docs/playtest_checklist.md](docs/playtest_checklist.md)

## 文档

完整文档入口：

- [docs/README.md](docs/README.md)

建议阅读顺序：

1. [docs/phase1_8_architecture_summary.md](docs/phase1_8_architecture_summary.md)：当前架构基线；
2. [docs/agentic_runtime_architecture.md](docs/agentic_runtime_architecture.md)：长期 Agentic Runtime 设计；
3. [docs/phase6_completion_summary.md](docs/phase6_completion_summary.md)：Phase 6 完成情况；
4. [docs/phase7_completion_summary.md](docs/phase7_completion_summary.md)：Phase 7 完成情况；
5. [docs/phase8_completion_summary.md](docs/phase8_completion_summary.md)：Phase 8 完成情况；
6. [docs/playtest_checklist.md](docs/playtest_checklist.md)：世界模式试玩清单；
7. [docs/future_phase_plan.md](docs/future_phase_plan.md)：Phase 9-10 开发路线；
8. [docs/phase9_10_execution_plan.md](docs/phase9_10_execution_plan.md)：Phase 9/10 执行计划；
9. [docs/world_bible.md](docs/world_bible.md)：世界观总览。

## 当前限制

- 世界模式已经可试玩；地点连续性、风险反馈、基本安全边界和 Phase 8 核心机制已有回归测试，长期玩法仍需要继续打磨。
- Phase 8 已完成技能、天赋、祷告、六属性检定、仪式晋升和道具机制的基础基线，完整成长体验仍会继续扩展。
- 网页界面尚未开始。
- 真实 LLM 与真实向量接口调用需要用户自行配置 API key，并会产生 API 成本。

## 后续阶段

```text
Phase 9: 网页界面与 API 产品体验
Phase 10: 工程质量与最终体验优化
```
