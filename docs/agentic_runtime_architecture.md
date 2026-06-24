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

Phase 5 应该从这里开始：

```text
Phase 5: Agentic Runtime Baseline
```

最小目标：

1. 新增 `OpenActionProposal`；
2. 新增 `RuleAdjudicationProposal`；
3. 新增 `StateCommitProposal`；
4. 新增 `MemoryCandidate`；
5. 实现 `Intent Agent -> Rule Arbiter Agent -> Validator -> Commit -> Narrator Agent` 的最小 CLI 闭环；
6. 将修道院降级为 tutorial/demo scenario；
7. 新增 world mode，让 LLM 生成临时场景、NPC 和事件；
8. 为每个 Agent 增加 fake provider test 和可选 live LLM smoke test。

Phase 5 的目标不是立刻做完整开放世界，而是证明：

```text
LLM 可以自由理解和生成。
程序可以稳定裁定、验证、记忆和写入。
```
