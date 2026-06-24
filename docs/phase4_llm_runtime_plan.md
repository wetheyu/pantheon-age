# Phase 4 LLM Runtime Plan

Phase 4 的目标不是立刻让 LLM 接管游戏，而是建立一条可控的 LLM 运行链路。

核心原则仍然是：

```text
LLM creates possibilities.
Rules constrain authority, not imagination.
The rule system confirms reality.
Only validated structured state becomes game truth.
```

Phase 4 的方向不是把 LLM 降级成润色器，而是先建立 proposal
runtime，让 LLM 可以提出行动、场景、事件和叙事可能性，再由验证器和规则系统裁定权限。

## Phase 4 总目标

Phase 4 要让项目具备“可接入 LLM”的工程结构：

- LLM 可以生成叙事提案；
- LLM 可以生成结构化行动候选；
- LLM 可以生成 NPC 对话或场景细节；
- 所有 LLM 输出都必须先变成结构化 proposal；
- proposal 必须验证后才能展示或写入记忆；
- LLM 不能直接修改 `GameState`；
- LLM 不能直接授予 HP、SAN、物品、线索、地点、阵营变化或结局。

## Phase 4 不做什么

第一轮 Phase 4 已经不做或仍暂缓：

- 不做完整向量数据库 RAG；
- 不做多智能体框架；
- 不做长期世界记忆；
- 不做前端；
- 不新增数据库表；
- 不让 LLM 输出直接写入 `GameState`。

这些会在后续阶段逐步加入。

## 推荐拆分

### 4.0 LLM Runtime Contracts

目标：先定义 LLM 输出必须长什么样。

任务：

- 新增 `llm_runtime/`；
- 定义 `NarrationProposal`；
- 定义 `NarrationValidation`；
- 定义 `NarrationResult`；
- 实现叙事提案验证；
- 实现安全回退：提案不合法时返回原始规则文本；
- 添加单元测试。

完成标准：

- LLM 叙事只能 claim 已经由 `rule_result` 授权的状态变化；
- 不能 claim 未获得的线索；
- 不能 claim 未发生的地点变化；
- 空文本会被拒绝；
- 测试通过。

### 4.1 LLM Provider Interface

目标：定义“以后怎么接模型”，但仍不绑定某个模型。

任务：

- 定义 `NarrationProvider` 接口；
- 提供 `TemplateNarrationProvider`；
- 为未来 OpenAI provider 预留结构；
- 记录模型调用输入输出边界。

完成标准：

- 当前系统不用 API key 也能跑；
- 未来替换 provider 不需要改 `rule_engine.py`；
- provider 不接触 `GameState` 写操作。

### 4.2 Prompt And Policy Files

目标：把 prompt 从代码里分离出来。

任务：

- 新增 `prompts/`；
- 新增 `prompts/narrator.md`；
- 写清楚 Narrator 的输入、输出 schema、禁止行为；
- 添加 prompt 文档说明。
- 补充 RAG-ready 文档：`tone_guide.md`、`forbidden_outputs.md`、`rag_seed_cards.md`、`inspiration_notes.md`。

完成标准：

- prompt 不散落在业务代码里；
- prompt 明确要求结构化输出；
- prompt 明确禁止越权状态变化。
- RAG 起步资料使用原创项目 canon 和高层风格指南，不使用其他小说全文。

### 4.3 Structured Action Candidate

目标：让 LLM 能辅助解析玩家自然语言，但不能直接执行。

任务：

- 定义 `ActionCandidate`、`ActionCandidateValidation` 和 `ActionCandidateResult`；
- 将玩家输入解析为候选 action；
- 候选 action 进入现有 `rule_engine.py` 前必须验证；
- 验证 supported intent、target 文本、item 文本和 confidence；
- target 和 item 可以是 LLM 生成的临时 NPC、物体、道具、房间、街道、区域或路线，但不能自动成为 canon 或机械奖励；
- 保留当前关键词 parser 作为 fallback；
- 为未来真实模型准备 `ActionCandidateProvider` 接口和 prompt 文件。

完成标准：

- LLM parser 输出只是候选；
- 无效候选会 fallback 到当前规则 parser；
- `rule_engine.py` 仍然只接受结构化 action。
- 当前本地运行不需要 API key，不调用真实网络模型。

### 4.4 Scene And Event Proposals

目标：让 LLM 不只润色，而是可以提出局部场景、NPC 和事件。

任务：

- 定义 `SceneProposal`；
- 定义 `EventProposal`；
- 定义通用 `ProposalValidation`；
- 给 proposal 增加 authority level；
- 区分 `flavor`、`temporary`、`persistent`、`mechanical`、`secret`；
- 添加基础 validator，阻止 LLM 直接 claim 机械结果或隐藏真相。

完成标准：

- LLM 可以提出临时场景；
- LLM 可以提出普通 NPC 或传闻；
- 机械结果仍必须由规则系统授权；
- 持久内容必须等待 memory commit。
- 当前只允许 `flavor` 和 `temporary`。

### 4.5 Generic Rule Adjudication

目标：让规则引擎从“固定副本规则”逐渐升级为通用裁判，并让结构化候选保留玩家行动的想象力。

任务：

- 扩展 `ActionCandidate`，保留 `method`、`desired_outcome`、`risk_tags`、`skill_tags` 和 `assumptions`；
- 定义通用检定类型；
- 定义行动风险和代价；
- 支持社交、潜行、调查、旅行、神秘学分析等通用裁定；
- 将 LLM proposal 转成可裁定的 `AdjudicationRequest`。

完成标准：

- LLM 可以提出丰富情境；
- 结构化候选不会把玩家输入压缩成按钮；
- 规则系统可以用统一标准裁定成功、失败、代价和授权结果；
- 不需要为每个场景写死一条规则。

### 4.6 Open Generation Proposal Runtime

目标：把 Phase 4 收束成开放生成运行时。LLM 可以自由提出地点、NPC、道具、关系、团队、组织、路线、传闻和事件，但程序负责验证权限和持久化边界。

任务：

- 定义 `GeneratedContentProposal`；
- 支持 `location`、`npc`、`item`、`relationship`、`team`、`organization`、`event`、`rumor`、`route`、`quest_hook`、`object`、`scene_detail`；
- 允许 `flavor` 和 `temporary`；
- 拒绝直接提交 `persistent`、`mechanical`、`secret`；
- 拒绝直接改变背包、关系、阵营、线索、HP/SAN、地点和结局；
- 新增 `prompts/open_generation.md`。

完成标准：

- 程序不要求所有具体内容预设；
- LLM 可以提出丰富内容；
- 生成内容默认不成为 canon；
- 机械结果仍由规则系统裁定；
- 持久内容留给后续 memory commit。

### 4.7 First Real LLM Call

目标：接入真实 LLM，让 CLI 可以使用 LLM 进行行动候选识别和安全叙事，但不影响规则权限。

任务：

- 使用环境变量读取 API key；
- 调用 LLM 生成 `ActionCandidate`；
- 调用 LLM 生成 `NarrationProposal`；
- 对 proposal 做验证；
- 验证失败自动回退；
- 在 CLI 中显示可选 Phase 4 runtime 摘要；
- 记录最小运行时错误和 fallback 状态。

完成标准：

- 没有 API key 时项目仍可运行；
- 有 API key 且 `PANTHEON_USE_LLM=1` 时启用 OpenAI provider；
- LLM 可帮助理解自然语言行动，但候选必须通过本地 validator；
- LLM 可增强叙事，但 narration claims 必须通过本地 validator；
- LLM 不能改变状态；
- 测试不依赖真实网络调用。

## 当前执行的小阶段

当前已完成：

```text
v4.0.0 Phase 4 LLM Runtime Contracts
v4.1.0 Phase 4 LLM Provider Interface
v4.2.0 Phase 4 Prompt And Policy Files
v4.3.0 Phase 4 Structured Action Candidate
v4.4.0 Phase 4 Scene And Event Proposals
v4.5.0 Phase 4 Semantic Action And Generic Adjudication
v4.6.0 Phase 4 Open Generation Proposal Runtime
v4.7.0 Phase 4 Real LLM CLI Runtime
```

`v4.1.0` 增加 provider 接口、本地模板 provider 和 OpenAI provider 占位。
`v4.2.0` 增加 `prompts/narrator.md` 和 prompt loader。
`v4.3.0` 增加 `ActionCandidate`、行动候选验证、keyword fallback、行动候选 provider 和 `prompts/action_candidate.md`。
`v4.4.0` 增加 `SceneProposal`、`EventProposal`、权限等级验证和 `prompts/scene_event.md`。
`v4.5.0` 增加语义行动字段、通用裁定请求和 `llm_runtime/adjudication.py`。
`v4.6.0` 增加 `GeneratedContentProposal`、开放生成 validator 和 `prompts/open_generation.md`。
`v4.7.0` 接入可选 OpenAI provider，并让 CLI 主流程可以走真实 LLM action candidate 和 narration proposal。
`Unreleased` 增加最小 RAG 文档、live LLM 测试入口、schema-first OpenAI 输出约束和 Agentic Runtime 长期架构文档。

## Phase 4 当前完成形态

Phase 4 完成后，CLI 的行动链路是：

```text
玩家输入
  ↓
OpenAIActionCandidateProvider 或 KeywordActionCandidateProvider
  ↓
ActionCandidate validator
  ↓
AdjudicationRequest
  ↓
rule_engine.py
  ↓
OpenAINarrationProvider 或 TemplateNarrationProvider
  ↓
Narration validator
  ↓
CLI 输出
```

启用真实 LLM：

```bash
PANTHEON_USE_LLM=1 OPENAI_API_KEY=... ./.venv/bin/python -m phase1_cli.main
```

查看 CLI runtime 摘要：

```bash
PANTHEON_SHOW_RUNTIME=1 ./.venv/bin/python -m phase1_cli.main
```

没有 `OPENAI_API_KEY` 或 provider 调用失败时，系统会自动回退到本地 keyword parser 和 template narrator。

## Phase 4 完成边界

Phase 4 到此完成。

它完成的是：

- LLM runtime contracts；
- provider abstraction；
- prompt/policy files；
- local fallback provider；
- OpenAI provider；
- structured output；
- narration validation；
- action candidate validation；
- scene/event/open-generation proposal validation；
- generic adjudication request；
- CLI runtime debug output；
- smoke test；
- optional live LLM test；
- documentation for future Agentic Runtime.

Phase 4 不继续扩展：

- 不继续给 `ActionCandidate(intent=...)` 增加大量 one-off intent；
- 不继续靠关键词或 alias 修补自然语言理解；
- 不把旧修道院 CLI 扩展成完整大世界；
- 不在 Phase 4 做长期 memory commit；
- 不在 Phase 4 做完整多 Agent orchestration；
- 不在 Phase 4 做向量 RAG。

原因：

```text
Phase 4 的目标是接入和约束 LLM。
Phase 5 的目标才是重构成 Agentic Runtime。
```

下一阶段应进入：

```text
Phase 5: Agentic Runtime Baseline
```

详见：

```text
docs/agentic_runtime_architecture.md
```

Phase 5 应用 `OpenActionProposal`、`RuleAdjudicationProposal`、`StateCommitProposal` 和 `MemoryCandidate` 替代当前过窄的 `ActionCandidate(intent=...)` 工作流。
