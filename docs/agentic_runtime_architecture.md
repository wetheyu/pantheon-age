# Agentic Runtime Architecture

本文档记录 `Pantheon Age` 的长期 Agentic Runtime 架构。

它是 Phase 5 之后的核心方向，用来替代“旧 CLI 规则系统 + LLM 辅助润色”的思路。

## 核心定位

`Pantheon Age` 不应该是一个把玩家输入压缩成固定按钮的文字冒险。

目标是：

```text
LLM provides imagination.
Agents organize possibilities.
Programs provide stability, memory, validation, and authority boundaries.
Only committed structured state becomes reality.
```

中文表达：

```text
LLM 负责想象力。
Agent 负责理解、生成、裁定建议、记忆整理和叙事组织。
程序负责规避 LLM 的缺点：上下文漂移、逻辑不统一、长期记忆弱、容易迎合玩家、容易乱给奖励。
只有通过验证并写入状态/记忆的结构化结果，才算世界现实。
```

程序不是 LLM 想象力的天花板。

程序是 LLM 的骨架、记忆、法律和审计系统。

## LLM 的缺点

程序主要补足这些问题：

- 上下文影响大；
- 长期记忆弱；
- 没有天然统一的裁定标准；
- 容易把玩家猜测当事实；
- 容易乱给奖励、道具、线索和结局；
- 容易暴露隐藏真相；
- 难以追踪 NPC、地点、关系和任务状态；
- 长上下文会变慢、变贵、不稳定。

因此程序应该构建：

- state；
- memory；
- validators；
- commit boundaries；
- trace；
- tests；
- cost/latency controls；
- RAG retrieval boundaries。

## 总运行流

长期目标流程：

```text
Player Input
  ↓
Memory Retrieval
  ↓
Intent Agent
  ↓
Scene / NPC / Event / Item Agents
  ↓
Rule Arbiter Agent
  ↓
Validation Layer
  ↓
State Commit Layer
  ↓
Memory Curator Agent
  ↓
Narrator Agent
  ↓
CLI / API / Web UI
  ↓
Observability / Evals
```

## Agent 角色

### Intent Agent

职责：

- 理解玩家真正想做什么；
- 保留复杂行动、复合目标、方法、语气和猜测；
- 不把行动过早压扁成 `move`、`talk`、`investigate`；
- 区分玩家意图、玩家猜测和世界事实。

输出应接近：

```json
{
  "action_summary": "玩家翻过长椅，借着阴影跳向前厅，并试图观察是否有人跟踪。",
  "primary_goal": "到达前厅",
  "secondary_goals": ["保持隐蔽", "观察身后动静"],
  "method": "翻过长椅，借阴影快速移动",
  "targets": ["前厅", "身后动静"],
  "player_assumptions": ["可能有人跟踪"],
  "requested_effects": ["location_change", "minor_observation"]
}
```

### Scene Agent

职责：

- 生成当前地点的临时场景；
- 生成可交互物体、感官细节、局部异常、环境变化；
- 不需要所有具体地点预先写死；
- 默认生成 `flavor` 或 `temporary` 内容。

不能：

- 直接创造永久地点；
- 直接给线索；
- 直接改变地图事实；
- 直接暴露隐藏真相。

### NPC Agent

职责：

- 生成普通 NPC；
- 生成 NPC 的可见知识、态度、短期目标、说话风格；
- 生成对话候选；
- 区分 NPC 知道什么、玩家知道什么、世界真实是什么。

不能：

- 让 NPC 透露未解锁主线真相；
- 把玩家猜测改成 NPC 事实；
- 随意让 NPC 死亡或加入阵营；
- 绕过关系和记忆系统。

### Event Agent

职责：

- 生成局部事件；
- 生成支线钩子；
- 生成城市新闻、街头传闻、旅途事件、异常征兆；
- 给世界带来新鲜感。

不能：

- 直接改变国家大势；
- 直接改写核心历史；
- 直接启动重大主线阶段；
- 直接创造超出权限的神明或外神事件。

### Item Agent

职责：

- 生成临时物品、可调查对象、材料、道具候选；
- 描述物品外观和可能用途；
- 提出道具使用风险。

不能：

- 直接把道具写入背包；
- 直接授予强力装备；
- 直接绕过检定、资源和代价。

### Rule Arbiter Agent

规则裁定也可以由 Agent 负责。

职责：

- 阅读当前状态、角色能力、场景、玩家意图和规则摘要；
- 判断行动是否可能；
- 判断是否需要检定；
- 建议检定类型、属性、难度、风险、代价；
- 区分允许结果、条件结果和拒绝结果；
- 为复杂行动拆分主要目标和次要目标。

输出应接近：

```json
{
  "action_type": "compound_action",
  "main_goal": "移动到前厅",
  "secondary_goals": ["保持隐蔽", "观察追踪者"],
  "required_checks": [
    {
      "type": "movement",
      "stat": "agility",
      "dc": 12
    },
    {
      "type": "stealth",
      "stat": "agility",
      "dc": 14
    }
  ],
  "allowed_effects": ["location_change"],
  "conditional_effects": ["suspicion_change", "minor_observation"],
  "denied_effects": ["guaranteed_clue"],
  "reasoning_summary": "玩家可以尝试复合行动，但观察信息需要检定成功后才能授权。"
}
```

边界：

```text
Rule Arbiter Agent 可以 propose 裁定。
程序 validator 必须检查裁定是否合理。
State Commit Layer 才能真正写入状态。
```

### Memory Retriever

行动前运行。

职责：

- 根据当前地点、NPC、任务、玩家输入提取相关记忆；
- 控制上下文长度；
- 避免把隐藏真相或 NPC 私有知识喂给不该知道的 Agent；
- 区分 player-known、npc-known、system-secret。

### Memory Curator Agent

行动后运行。

这是核心 Agent 之一。

它不只是“保存聊天记录”，而是判断：

```text
什么值得存？
存到哪里？
以什么粒度存？
什么应该丢弃？
什么只是玩家猜测？
什么是临时场景？
什么可以成为当前存档的长期事实？
```

职责：

- 信息筛选；
- 信息分类；
- 信息压缩；
- 信息提取建议；
- 防止上下文污染；
- 生命周期管理。

记忆类型：

- `player_memory`；
- `npc_memory`；
- `location_memory`；
- `faction_memory`；
- `quest_memory`；
- `world_event_memory`；
- `temporary_scene_memory`；
- `secret_memory`。

输出示例：

```json
{
  "memory_candidates": [
    {
      "type": "npc_memory",
      "subject": "码头搬运工艾文",
      "content": "艾文曾向玩家透露潮汐圣会最近封锁了三号码头。",
      "authority_level": "persistent",
      "visibility": "player_known",
      "source_event": "turn_12",
      "confidence": 0.92
    }
  ],
  "discarded": [
    {
      "content": "玩家猜测艾文是深渊信徒",
      "reason": "player speculation, not confirmed fact"
    }
  ]
}
```

### State Commit Layer

严格来说，它不是 Agent，而是程序边界。

职责：

- 写入 `GameState`；
- 写入数据库；
- 更新 HP、SAN、地点、线索、物品、关系、阵营、任务状态；
- 记录事件日志；
- 保存通过验证的 memory。

原则：

```text
Agents can propose.
Validators can approve.
Commit layer writes reality.
```

### Narrator Agent

职责：

- 根据已确认的 RuleAdjudication 和 StateCommit 输出最终叙事；
- 保持文风；
- 展示结果、代价、气氛和下一步钩子；
- 不新增未授权事实。

不能：

- 修改状态；
- 添加未授权线索；
- 让未发生的死亡、移动、奖励、结局出现在文本里。

### Observer / Trace Agent

长期可选。

职责：

- 记录每次 Agent 调用；
- 记录 prompt、输入摘要、输出、验证结果、fallback、耗时、token、成本；
- 为 eval 和 debug 提供证据。

## 数据对象

长期建议的数据对象：

```text
OpenActionProposal
SceneProposal
NPCProposal
EventProposal
ItemProposal
RuleAdjudicationProposal
StateCommitProposal
MemoryCandidate
MemoryRetrievalResult
NarrationProposal
ValidationResult
TraceRecord
```

当前 Phase 4 已经实现了部分早期对象：

```text
ActionCandidate
SceneProposal
EventProposal
GeneratedContentProposal
AdjudicationRequest
NarrationProposal
```

这些是向 Agentic Runtime 过渡的第一版契约，不是最终形态。

## 程序该限制什么

程序应该限制的是：

- 状态写入权限；
- 奖励权限；
- 线索释放权限；
- 隐藏真相暴露；
- 记忆持久化；
- 世界 canon 修改；
- 数值结算；
- DB 写入；
- API 输出结构；
- 成本和延迟。

程序不应该限制的是：

- 玩家行动表达方式；
- 临时地点；
- 临时 NPC；
- 临时事件；
- 环境细节；
- 对话风格；
- 传闻、钩子、道具候选；
- 合理的复合行动。

## Phase 5 起点

Phase 5 baseline 已经完成：

```text
Phase 5: Agentic Runtime Baseline
```

当前 `v5.8.0` 已完成第一条最小链路、第一层 provider interface、临时
NPC / Event / Item Agents、tutorial/world-mode 分流、八个重要国家出身选择、奥斯特民族选择、常用身份选择、本地教会合法性上下文、动态国家关系接口、OpenAI-backed Turn Director 默认快速路径、旧版 Intent / Rule Arbiter / WorldBundle 多调用路径、可选 full OpenAI NPC / Event / Item / Narrator Agents、本地 Agentic Memory Store baseline、跨回合 memory retrieval 集成、CLI 故事化输出，以及 Phase 5 最终集成测试和完成总结：

```text
Memory Retriever
  -> Turn Director Agent
  -> Validator Layer
  -> State Commit Layer
  -> Memory Curator Agent
  -> Narration Branch Selection
```

当前实现位于：

```text
agentic_runtime/
phase1_cli/scenarios.py
```

最终完成总结位于：

```text
docs/phase5_completion_summary.md
```

新增 provider 边界：

```text
agentic_runtime/providers.py
```

当前已支持：

- local Memory Retriever；
- local Intent Agent；
- optional OpenAI Intent Agent；
- local Scene Agent；
- local NPC Agent；
- optional OpenAI NPC Agent；
- local Event Agent；
- optional OpenAI Event Agent；
- local Item Agent；
- optional OpenAI Item Agent；
- local Rule Arbiter Agent；
- local Memory Curator Agent；
- local Memory Store；
- local World Slice helpers；
- local Narrator Agent；
- optional OpenAI Turn Director Agent。

当前默认 live 路径让 Turn Director Agent 可选接入真实 LLM。Turn Director 在一次
模型调用里返回开放行动理解、规则裁定建议、Scene / NPC / Event / Item 和紧凑叙事；
程序随后验证裁定、掷骰、提交状态，并在高风险场景补充或回退安全叙事。
Memory 和 Commit 仍保持本地 provider，避免一次性把整个运行时变成不可控的模型调用链。
关闭 `PANTHEON_AGENTIC_TURN_DIRECTOR` 后，旧版 Intent / Rule Arbiter / WorldBundle
多调用路径仍可用于 agent-level 调试。full 模式仍可让 NPC / Event / Item / Narrator
Agents 分别接入真实 LLM，主要用于更细粒度调试。NPC / Event / Item Agents 目前只生成
`temporary` 候选内容，不会写入长期世界事实。

`v5.5` 新增本地 memory store。它只保存通过 validator 的
`MemoryCandidate`，并按 `player_known`、`npc_known`、`location`、`quest`
和 `secret` 分桶。直接来自 OpenAI / LLM provider 的原始生成内容不能被当成
长期事实写入；secret memory 只能进入系统秘密桶。

`v5.6` 让 memory store 进入下一回合检索：`player_known` / `quest` 进入
玩家已知上下文，`location` 进入地点上下文，`npc_known` / `secret` 进入内部
`hidden_context`。默认 `to_dict()` 不序列化 hidden context，避免秘密记忆出现在
CLI/API runtime payload、公开状态或玩家叙事里。

`v5.7` 让 world-mode 在 CLI 中形成可见小切片：本地 Scene / NPC / Event /
Item Agents 会根据城市、出身和可见记忆生成临时内容。随后 CLI 默认输出调整为
玩家可读的故事文本；Agent 结构、provider、验证和边界摘要只在
`PANTHEON_SHOW_RUNTIME=1` 时显示。

`v5.3` 新增：

```text
PANTHEON_GAME_MODE=world
```

默认 `tutorial` 仍然是雾中修道院固定地图。`world` 会让玩家从八个重要国家中
选择出身国家和开局城市，自动进入 Phase 5 Agentic Runtime，并使用
`world_action` 记录开放行动，避免把开放世界行动硬塞进修道院教程地图。

当前 CLI 可通过以下开关启用：

```text
PANTHEON_USE_AGENTIC_RUNTIME=1
```

第一条链路证明了：

- 开放玩家行动会先进入 `OpenActionProposal`；
- Rule Arbiter Agent 只在规则边界生成 `bridge_action`；
- State Commit Layer 才调用 deterministic `rule_engine` 写入状态；
- Memory Curator Agent 只提出 memory candidates，不直接持久化；
- Narrator Agent 基于已提交结果生成输出；
- `跳向前厅` 可以在不新增 Phase 1 关键词的情况下桥接为移动。

剩余目标：

1. 为 Scene / NPC / Event / Item / Rule Arbiter / Memory / Narrator 增加真实 LLM-backed providers；
2. 增加 Phase 5 可选 live LLM smoke test；
3. 增加持久化 memory store；
4. 让 world-mode 开始写入经过验证的长期 NPC、地点和事件记忆。

Phase 5 的目标不是立刻做完整开放世界，而是证明：

```text
LLM 可以自由理解和生成。
程序可以稳定裁定、验证、记忆和写入。
```
