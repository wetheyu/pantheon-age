# Pantheon Age LLM Runtime Design

## 核心原则

`Pantheon Age` 需要尽可能利用 LLM 的创造力，但不能把世界现实完全交给 LLM。

原因：

- LLM 输出具有概率性；
- LLM 容易受上下文影响；
- LLM 容易迎合玩家当前说法；
- LLM 可能编造事实；
- LLM 可能破坏已存在设定。

因此项目采用以下原则：

```text
LLM creates possibilities.
Rules constrain authority, not imagination.
LLM 只能 propose。
系统负责 validate。
只有 validated content 才能 commit。
```

更准确地说：

```text
规则引擎不是创作天花板。
规则引擎是 LLM 的稳定器、裁判和长期一致性约束器。
```

LLM 的想象力应该用于生成行动、场景、NPC、事件、对话和叙事可能性。
规则系统负责决定这些可能性是否有权改变现实。

## 当前实现状态

当前版本：`v4.7.0 Phase 4 Real LLM CLI Runtime`。

Phase 4 已经完成它该完成的任务：证明真实 LLM provider、prompt 文件、structured output、本地 validator、安全 fallback 和 CLI 接入可以组成一个可运行的最小闭环。

Phase 4 不是最终玩法架构。当前 `ActionCandidate(intent=...)` 仍然是为了兼容旧 CLI 规则系统的过渡对象，不应该继续用 one-off 关键词、别名或固定枚举补丁来解决开放自然语言理解问题。

下一阶段应进入 Agentic Runtime：

```text
Intent Agent
  -> Scene/NPC/Event/Item Agents
  -> Rule Arbiter Agent
  -> Validator Layer
  -> State Commit Layer
  -> Memory Curator Agent
  -> Narrator Agent
```

长期架构记录在：

```text
docs/agentic_runtime_architecture.md
```

已经实现：

- `llm_runtime/contracts.py`：定义 LLM 叙事提案、验证结果和最终结果；
- `llm_runtime/actions.py`：定义行动候选验证、转换和 fallback；
- `llm_runtime/adjudication.py`：把语义行动候选转成通用裁定请求；
- `llm_runtime/proposals.py`：定义场景、事件和开放生成 content proposal 验证和权限等级检查；
- `llm_runtime/narrator.py`：验证叙事提案是否越权；
- `llm_runtime/providers.py`：定义 provider 接口、本地 fallback provider 和 OpenAI provider；
- `llm_runtime/prompts.py`：集中加载 prompt/policy 文件；
- `prompts/action_candidate.md`：记录行动候选 agent 的输入、输出 schema、支持 intent 和禁止行为；
- `prompts/open_generation.md`：记录开放生成 content proposal 的输入、输出 schema、内容类型和禁止行为；
- `prompts/scene_event.md`：记录场景/事件 proposal 的输入、输出 schema、权限等级和禁止行为；
- `prompts/narrator.md`：记录 Narrator 的输入、输出 schema、允许 claim 和禁止行为；
- 行动候选验证失败时，自动回退到当前关键词 parser；
- 语义行动候选会保留 `method`、`desired_outcome`、`risk_tags`、`skill_tags` 和 `assumptions`；
- 通用裁定请求会给出 `check_type`、`primary_stat`、`difficulty` 和 `possible_costs`；
- 场景/事件 proposal 验证会拒绝永久事实、机械结果和隐藏真相；
- 开放生成 proposal 验证会允许临时地点、NPC、道具、关系、团队、组织、事件、传闻和路线，但拒绝直接写入状态；
- 提案验证失败时，自动回退到确定性规则文本；
- 当前已经支持可选真实 OpenAI provider；
- 默认不调用真实 LLM API，不需要 API key，不依赖网络；
- 设置 `PANTHEON_USE_LLM=1` 且提供 `OPENAI_API_KEY` 后，CLI 会启用 OpenAI action candidate 和 narration provider；
- 如果 provider 调用失败，系统会自动回退到本地 keyword parser 和 template narrator。
- 后续计划支持本地部署模型 provider，用于离线运行、成本控制和 provider portability。

当前阶段处理三个最小契约：

```text
player text -> ActionCandidateProvider -> ActionCandidate -> validation -> rule_engine action or keyword fallback

ActionCandidate -> AdjudicationRequest -> generic rule adjudication metadata

context -> SceneProposal / EventProposal -> authority validation -> display-only proposal or rejection

open context -> GeneratedContentProposal -> authority validation -> temporary content or rejection

GameResponse -> NarrationProvider -> prompt -> NarrationProposal -> validation -> NarrationResult
```

后续才会加入完整向量 RAG、多 Agent 和长期记忆。

更准确地说，后续不只是“多 Agent 越多越好”，而是把不同职责拆开：

- Intent Agent 负责理解开放行动；
- Rule Arbiter Agent 负责提出裁定建议；
- Scene / NPC / Event / Item Agents 负责生成可验证的临时内容；
- Memory Curator Agent 负责判断哪些信息值得保存、丢弃、压缩或隐藏；
- State Commit Layer 负责真正写入状态；
- Narrator Agent 负责在已确认结果上生成最终叙事。

程序的职责不是把玩家表达限制成固定按钮，而是规避 LLM 上下文漂移、长期记忆弱、裁定标准不统一、容易迎合玩家猜测和容易乱给奖励的问题。

RAG 初期不需要大量资料。优先使用项目自己的短文档：

- `docs/world_bible.md`：完整世界 canon；
- `docs/rag_seed_cards.md`：高频检索设定卡；
- `docs/tone_guide.md`：文风指南；
- `docs/forbidden_outputs.md`：禁止输出和越权边界；
- `docs/inspiration_notes.md`：高层灵感和原创化边界。
- `docs/progression_design.md`：成长、属性、职业等级、信仰等级、仪式晋升、道具和代价规则。

不要把其他小说全文作为 RAG 语料。项目应吸收高层题材气质，但保持原创设定和原创表达。

Provider 规则：

- provider 可以返回 `ActionCandidate` 或 `NarrationProposal`；
- provider 只能返回结构化候选或提案，不能执行行动；
- provider 不能修改 `GameState`；
- provider 不能直接写数据库；
- provider 不能绕过 `validate_action_candidate()` 或 `validate_narration_proposal()`；
- 真实模型 provider 必须在没有 API key 时安全失败或回退。
- 本地模型 provider 也必须遵守同一套 validator、fallback 和权限边界。

当前 CLI 中真实 LLM 的启用方式：

```bash
PANTHEON_USE_LLM=1 OPENAI_API_KEY=... ./.venv/bin/python -m phase1_cli.main
```

可选模型覆盖：

```bash
PANTHEON_OPENAI_MODEL=gpt5.5 PANTHEON_USE_LLM=1 OPENAI_API_KEY=... ./.venv/bin/python -m phase1_cli.main
```

查看 Phase 4 runtime 摘要：

```bash
PANTHEON_SHOW_RUNTIME=1 ./.venv/bin/python -m phase1_cli.main
```

未来本地部署方向：

```text
Ollama / LM Studio / vLLM
  ↓
OpenAI-compatible local endpoint
  ↓
LocalActionCandidateProvider / LocalNarrationProvider
  ↓
same validators
  ↓
same rule_engine
```

本地部署不是为了让本地模型绕过规则，而是让同一套 agent runtime 可以在云端模型和本地模型之间切换。

Prompt 规则：

- prompt 放在 `prompts/`；
- prompt 必须说明输入、输出 schema 和禁止行为；
- prompt 只能约束模型行为，不能替代 Python validator；
- prompt 不能要求模型直接修改 `GameState`；
- prompt 不能要求模型直接写数据库。

换句话说：

```text
LLM 输出不是事实。
玩家输入不是事实。
写入 GameState 的结构化结果才是事实。
```

## LLM 可以做什么

LLM 应该用于生成：

- 临时场景；
- 城市细节；
- 旅馆、酒馆、码头、工厂、教堂等地点；
- 普通 NPC；
- 支线委托；
- 报纸新闻；
- 街头传闻；
- 旅途事件；
- 对话内容；
- 氛围描写；
- 神秘异常表现；
- 调查过程中的细节；
- 无限流式的新鲜事件；
- 不同国家风格下的地方特色。

LLM 不是世界本身。

LLM 是世界内容的生成器。

真正的世界状态由系统保存。

## 规则引擎应该做什么

规则引擎不应该试图穷举所有故事内容。

它应该负责：

- 统一裁判标准；
- 机械结果；
- 资源和风险；
- 主线阶段和节奏；
- 线索和秘密释放权限；
- 状态变化权限；
- 长期一致性约束。

也就是说，规则引擎应该回答：

```text
这个行动是否可能？
需要什么检定、代价或风险？
成功可以授权什么结果？
失败会带来什么后果？
这个生成内容能不能进入长期记忆？
```

而不是写死所有可能发生的场景。

## 内容权限等级

LLM 生成内容进入系统前，应该先被分级：

```text
flavor
  氛围描写、感官细节、修辞表达。
  可以自由生成，但不能和事实冲突。

temporary
  临时场景、无名 NPC、小传闻、局部事件。
  可以展示，但默认不写入长期世界。

persistent
  命名 NPC、地方事实、关系变化、城市事件。
  必须通过验证，并显式 commit 到 memory。

mechanical
  HP、SAN、金钱、物品、线索、地点、阵营、结局。
  必须由 deterministic rules 授权。

secret
  隐藏真相、未解锁身份、核心秘密、主线谜底。
  必须由进度规则允许后才能暴露。
```

## LLM 不能做什么

LLM 不能直接决定：

- 玩家 HP 变化；
- 玩家 SAN 变化；
- 玩家属性变化；
- 玩家职业等级变化；
- 玩家信仰等级变化；
- 玩家神秘阶位变化；
- 玩家获得技能、天赋或祷告；
- 玩家获得见证值、神眷或消除代价；
- 玩家金钱变化；
- 玩家获得或失去物品；
- 玩家获得或失去线索；
- 玩家当前位置变化；
- 玩家死亡；
- NPC 死亡；
- 阵营关系变化；
- 未经关系接口验证和提交的国家关系变化；
- 世界重大历史变化；
- 神明设定变化；
- 主线任务阶段变化；
- 结局；
- 骰子判定结果；
- 数据库存储内容。

LLM 不能随意：

- 发明第九位神明；
- 把深渊之神写成外神，或写成八神体系之外的存在；
- 随意发明外神、伪神或外神教派；
- 在当前阶段发明欲望母神之外的外神；
- 把外神写成公开合法正统神明；
- 发明第六大列强；
- 改变 19 世纪科技水平；
- 让角色使用明显超时代科技；
- 让玩家无代价旅行；
- 让 NPC 透露未解锁的核心秘密；
- 把临时生成内容直接变成永久设定；
- 因为玩家暗示某件事，就顺着玩家说法改写世界真相。

## 玩家输入不是事实

玩家输入只代表：

```text
玩家想做什么
```

或者：

```text
玩家认为可能是什么
```

它不代表世界真的如此。

例如玩家说：

```text
我觉得这个警探肯定是深渊教徒。
```

LLM 不能因为玩家这样说，就直接把警探设定成深渊教徒。

正确处理方式：

- LLM 可以生成警探紧张、回避、言辞模糊的表现。
- 规则系统根据真实隐藏状态决定警探到底是不是深渊教徒。
- 如果警探不是，LLM 不能为了迎合玩家猜测改变事实。
- 如果警探是，也要等玩家通过调查获得线索后逐步揭示。

## 区分玩家意图和世界事实

玩家说：

```text
我打开密室门，里面应该有一把神器。
```

系统应解析为：

```json
{
  "action_type": "open",
  "target": "secret_room_door",
  "player_assumption": "there may be an artifact inside"
}
```

而不是直接生成神器。

## 基本运行流程

```text
玩家输入
  ↓
RAG 检索当前相关世界观
  ↓
LLM 生成 ActionCandidate / SceneProposal / EventProposal
  ↓
validator.py 检查世界观、隐藏信息和权限
  ↓
rule_engine.py 裁定机械结果、代价和授权后果
  ↓
memory_manager.py 决定哪些生成内容可以持久化
  ↓
RAG 检索叙事上下文
  ↓
LLM Narrator 生成 NarrationProposal
  ↓
validator.py 再次校验最终 claims
  ↓
CLI / API / Web UI
```

## 结构化状态变化

所有重要变化必须写成结构化数据。

示例：

```json
{
  "hp_delta": 0,
  "san_delta": -1,
  "money_delta": -3,
  "location_changed": true,
  "new_location": "albion_fogport_station",
  "clues_added": ["ticket_with_salt_stain"],
  "items_added": [],
  "faction_changes": {
    "albion_police": -1
  }
}
```

不能只靠一段自然语言描述表示状态变化。

## 叙事必须服从状态

如果结构化结果里没有获得线索，叙事就不能写玩家发现了线索。

如果结构化结果里没有移动地点，叙事就不能写玩家已经到达别的城市。

如果结构化结果里没有 NPC 死亡，叙事就不能写 NPC 死了。

## RAG 的作用

RAG 是控制 LLM 输出的重要手段。

世界观不能全部塞进 prompt，也不能依赖 LLM 记忆。

未来可以把世界设定拆成多个可检索文档，例如：

```text
world_overview.md
countries/albion.md
countries/lumiere.md
countries/walde.md
countries/ost.md
countries/istea.md
gods/ocean.md
gods/truth.md
gods/war.md
gods/judgment.md
gods/abundance.md
gods/death.md
gods/secrecy.md
gods/abyss.md
classes/knight.md
classes/mage.md
classes/agent.md
classes/ranger.md
classes/priest.md
classes/alchemist.md
technology_level.md
tone_guide.md
forbidden_outputs.md
travel_rules.md
faction_rules.md
```

当玩家在某个国家、城市或事件中行动时，系统只检索相关文档给 LLM。

例如玩家在阿尔比昂港口调查潮汐圣会事件时，RAG 应检索：

- 阿尔比昂国家设定；
- 当前城市设定；
- 港口场景规则；
- 海洋之神设定；
- 潮汐圣会设定；
- 当前任务状态；
- 玩家已知线索；
- 技术水平限制；
- 禁止输出规则。

RAG 的作用不是让 LLM 完全可靠，而是减少它乱编的范围。

真正的可靠性还需要：

- 规则引擎；
- 状态管理；
- validator；
- memory manager。

## 内容分级

### Level 0：绝对固定设定

不能由 LLM 修改。

包括：

- 世界时代背景；
- 世界边界为虚无之壁；
- 虚无之壁之外是无尽虚空和外神所在地；
- 五大列强；
- 诺克提亚；
- 控制金门海峡且以深渊之神为官方信仰的塞勒米亚苏丹国；
- 罗斯维亚大公国；
- 已设定核心城市；
- 八大神明；
- 六大职业；
- 核心科技水平；
- 核心世界规则；
- 已确定主线真相；
- 已确定历史事件；
- 已存在的重要 NPC；
- 已存在的重要地点。

### Level 1：固定设定的具体表现

LLM 可以根据 RAG 进行补充，但不能改变核心。

例如：

- 阿尔比昂首都的一个贫民区街道；
- 卢米埃某家咖啡馆；
- 瓦尔德某个铁路站；
- 奥斯特某个军官俱乐部；
- 伊斯特亚某个港口旅馆。

### Level 2：临时场景内容

LLM 可以自由度较高地生成。

例如：

- 路人；
- 酒馆老板；
- 旅馆房间；
- 码头搬运工；
- 报纸小新闻；
- 街头传闻；
- 普通商店；
- 一次性旅途事件。

这些内容默认是临时的。

除非系统决定保存，否则不会成为长期世界设定。

### Level 3：可持久化支线内容

LLM 可以生成，但必须经过 validator 和 memory manager 才能持久化。

例如：

- 一个支线 NPC；
- 一个地方秘社；
- 一个小型异常事件；
- 一个可重复访问的地点；
- 一个地区性传闻；
- 一个可追踪委托。

这些信息跟随存档。

每次开新档时，世界回到初始状态。

## 开放生成内容

长期不应该把所有具体地点、NPC、物品、关系、团队、组织、路线、传闻和事件都预先写死。

固定设定应该负责提供：

- 世界边界；
- 国家、城市和组织气质；
- 神明、教会和禁忌规则；
- 科技水平；
- 权限边界；
- 生成内容的持久化规则。

LLM 可以在这些约束下生成：

- 临时房间；
- 街道；
- 码头；
- 酒馆；
- 普通 NPC；
- 临时道具；
- 临时关系；
- 临时团队；
- 临时组织；
- 小事件；
- 传闻；
- 路线。

这些生成内容默认只是 `flavor` 或 `temporary`。

只有经过 validator 和 memory commit 后，才可以升级为可重复访问地点、命名 NPC、支线事实或长期世界记忆。

因此，LLM runtime 不应该因为某个 target 不在 CLI 的 `LOCATIONS` 里就直接拒绝它。真正需要拒绝的是：

- target 为空；
- target 越权声明机械结果；
- target 试图改写固定 canon；
- target 试图绕过 memory 直接成为永久事实。

这条原则适用于所有生成内容，不只适用于地点。

程序应该规避的是 LLM 的缺点，而不是规避 LLM 的想象力：

- 不统一的逻辑；
- 上下文漂移；
- 长期规划不足；
- 记忆不可靠；
- 迎合玩家猜测；
- 无代价发奖励；
- 提前揭露秘密。

因此程序应该写的是约束、验证、裁定和持久化边界，而不是把每一个道具、NPC、关系、团队和事件都预先列完。

## 场景提案格式

LLM 生成场景时，应该输出结构化 proposal。

示例：

```json
{
  "scene_name": "灰鸥旅馆",
  "country": "阿尔比昂",
  "city": "雾港",
  "scene_type": "inn",
  "description": "一间靠近码头的廉价旅馆，空气里有煤烟、海盐和湿木头的气味。",
  "allowed_actions": ["rest", "ask_rumors", "rent_room", "inspect", "talk"],
  "npc_candidates": [
    {
      "name": "玛莎·克莱恩",
      "role": "旅馆老板",
      "attitude": "cautious",
      "secret_level": "minor"
    }
  ],
  "possible_clues": [
    {
      "clue_id": "rumor_missing_sailors",
      "visibility": "requires_conversation"
    }
  ],
  "risk_tags": ["pickpocket", "cult_rumor", "police_attention"],
  "deity_links": ["海洋之神", "隐秘之神"],
  "persistence": "temporary"
}
```

系统需要检查：

- 国家是否存在；
- 城市是否符合设定；
- 场景类型是否允许；
- 科技水平是否合理；
- 神明关联是否合理；
- NPC 是否过强；
- 是否泄露隐藏主线；
- 是否直接给玩家奖励；
- 是否改变世界大设定；
- 是否需要写入长期记忆。

通过校验后，场景才可以展示给玩家。

## 事件生成规则

事件也应由 LLM 提案，规则系统校验。

事件类型：

- 日常事件；
- 调查事件；
- 旅途事件；
- 神秘事件；
- 战斗事件；
- 社交事件；
- 阵营事件；
- 神明污染事件；
- 支线委托；
- 主线推进事件。

LLM 可以生成事件壳子。

例如：

```text
一名湿透的少年在火车站声称，
他从未登上过那艘已经沉没三十年的船，
但他的口袋里却有那艘船的船票。
```

但事件是否真的出现，需要系统判断：

- 当前地点是否合适；
- 当前神明污染值是否足够；
- 当前任务阶段是否允许；
- 玩家是否有相关线索；
- 随机事件概率是否触发；
- 事件等级是否过高；
- 事件奖励是否合理。

LLM 不能随便把所有场景都变成主线级大事件。

## LLM 调用类型

### Intent Parser

目标：把玩家自然语言变成结构化 action。

输入：

- 玩家输入；
- 当前地点；
- 可见对象；
- 可用动作列表。

输出示例：

```json
{
  "action_type": "inspect",
  "target": "corpse_ring",
  "method": "careful"
}
```

权限：

- 不能生成剧情；
- 不能修改状态；
- 不能决定结果。

### Scene Generator

目标：生成局部场景细节。

权限：

- 可以生成临时 NPC；
- 可以生成环境细节；
- 可以生成普通传闻；
- 不能生成重大世界变化。

### Event Generator

目标：生成可能发生的小事件或支线事件。

权限：

- 可以生成候选事件；
- 不能自动触发事件；
- 不能自动给奖励；
- 不能强行推进主线。

### Narrator

目标：把规则结果写成有氛围的文本。

输入：

- rule_result；
- visible_state；
- style guide。

权限：

- 不能改变 rule_result；
- 不能新增事实；
- 不能泄露隐藏信息。

### NPC Dialogue Generator

目标：生成 NPC 对话。

输入：

- NPC 设定；
- NPC 已知信息；
- NPC 对玩家态度；
- 当前场景；
- 玩家问题。

权限：

- 只能使用 NPC 知道的信息；
- 不能透露隐藏真相；
- 不能随意改变 NPC 立场。

### Memory Summarizer

目标：总结游戏历史。

权限：

- 只能总结已发生事实；
- 不能加入新事实；
- 不能直接写入数据库。

## 真实世界感的系统支撑

想让玩家感觉自己真实活在这个世界里，不能只靠 LLM 写得华丽。

还需要：

- 稳定世界规则；
- 持久化记忆；
- 时间推进；
- 地理约束；
- 社会身份约束；
- 信息边界。

## 防止上下文污染

不要把完整聊天记录直接当作事实来源。

每次调用 LLM 时，建议只提供：

- 当前玩家状态；
- 当前地点；
- 当前可见 NPC；
- 当前已发现线索；
- 当前任务阶段；
- RAG 检索到的相关设定；
- 本次玩家输入；
- 输出格式要求；
- 禁止事项。

这样可以减少 LLM 被长上下文带偏。

## 后续模块方向

未来可以逐步加入：

- `llm_intent_parser.py`
- `llm_scene_generator.py`
- `llm_event_generator.py`
- `llm_narrator.py`
- `validator.py`
- `memory_manager.py`
- `rag_retriever.py`

但这些都不应该在 Phase 2 最小 API 阶段一次性完成。

Phase 2 第一目标仍然是：

```text
把当前 CLI 能力稳定暴露成 FastAPI。
```
